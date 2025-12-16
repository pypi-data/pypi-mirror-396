import uuid
from typing import Sequence

from basejump.core.common.config.logconfig import set_logging
from basejump.core.database import db_utils
from basejump.core.database.crud import crud_connection, crud_table, crud_utils
from basejump.core.database.db_connect import ConnectDB, TableManager
from basejump.core.database.index import DBTableIndexer
from basejump.core.models import errors, models
from basejump.core.models import schemas as sch
from redis.asyncio import Redis as RedisAsync
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

logger = set_logging(handler_option="stream", name=__name__)


class DBManager:
    """Manage and update database connections and save them in the
    database for future use as a connection string"""

    def __init__(
        self,
        db: AsyncSession,
        connections: Sequence[models.DBConn],
        db_params: sch.DBParamsSchema,
        database: models.DBParams,
        client_user: sch.ClientUserInfo,
        db_id: int,
        db_uuid: uuid.UUID,
        embedding_model_info: sch.AzureModelInfo,
        small_model_info: sch.ModelInfo,
        redis_client_async: RedisAsync,
        sql_engine: AsyncEngine,
    ):
        self.db = db
        self.db_params = db_params
        self.database = database
        self.client_user = client_user
        self.db_id = db_id
        self.db_uuid = db_uuid
        self.embedding_model_info = embedding_model_info
        self.small_model_info = small_model_info
        self.redis_client_async = redis_client_async
        self.sql_engine = sql_engine
        self.connections = connections

    async def validate_db(self):
        # TODO: Updated jinja values supplied to the db_params object don't get saved to the database
        # remove the option to save jinja values when updating the database
        # Verify the updated params using a random connection
        conn_db = await crud_connection.get_conndb_from_connection(
            db_params=self.db_params, connection=self.connections[0]
        )
        conn_db.conn_params.schemas = self.db_params.schemas  # Use the db schemas when
        await crud_connection.verify_connection(conn_db=conn_db)

    async def validate_db_alias(self):
        # Ensure no duplicate alias names excluding the current alias in database
        client_dbs = await crud_connection.get_client_dbs(db=self.db, client_id=self.client_user.client_id)
        for client_db in client_dbs:
            if client_db.db_id == self.database.db_id:
                continue
            other_db_alias = ConnectDB.decrypt_db({"database_name_alias": client_db.database_name_alias})[
                "database_name_alias"
            ]
            logger.debug("New DB Alias = %s", self.db_params.database_name_alias)
            logger.debug("Other DB Alias = %s", other_db_alias)
            if self.db_params.database_name_alias == other_db_alias:
                raise errors.DBAliasConflict

    async def get_index_db_tables(self):
        db_vector = await crud_connection.get_vector_connection_from_id(db=self.db, vector_id=self.database.vector_id)
        return DBTableIndexer(
            client_id=self.client_user.client_id,
            client_uuid=self.client_user.client_uuid,
            db_uuid=self.db_uuid,
            vector_uuid=db_vector.vector_uuid,
            embedding_model_info=self.embedding_model_info,
        )

    async def update_schemas(self) -> list[str]:
        # Determine if there are new schemas
        tables = [sch.GetSQLTable.from_orm(table) for table in self.database.tables]
        tables_formatted = await db_utils.process_db_tables(tables=tables)
        schemas = {table.table_schema for table in tables_formatted}
        new_schemas = set([schema.schema_nm for schema in self.db_params.schemas]) - schemas
        updated_schemas = False
        brand_new_schemas = set()
        for new_schema in new_schemas:
            for schema_map in self.db_params.schema_maps:
                if new_schema == schema_map.new_schema:
                    updated_schemas = True
                else:
                    brand_new_schemas.add(new_schema)
        if updated_schemas:
            logger.info("Updated schemas detected: %s", new_schemas)
        index_db_tables = await self.get_index_db_tables()
        logger.debug("Updating the index for: %s", str(index_db_tables.vector_uuid))
        if updated_schemas:
            if self.db_params.schema_maps:
                connections = await crud_connection.get_db_conns(db=self.db, db_id=self.db_id)
                await crud_connection.update_connection_schemas(
                    db_params=self.db_params, schema_maps=self.db_params.schema_maps, connections=list(connections)
                )
            # Update existing table schemas
            await self.update_table_schemas(
                tables=tables_formatted,
                index_db_tables=index_db_tables,
            )
        return list(brand_new_schemas)

    async def update_db(self) -> sch.GetDBParams:
        if not self.db_params.database_name_alias:
            self.db_params.database_name_alias = ConnectDB.decrypt_db(
                {"database_name_alias": self.database.database_name_alias}
            )["database_name_alias"]
        conn_db = await crud_connection.get_conndb_from_connection(
            db_params=self.db_params, connection=self.connections[0]
        )
        for key, value in conn_db.conn_params_bytes.dict().items():
            # TODO: Reference the db models directly since the names could change and hard coded is not best practice
            # Skip values not in SQLDB params
            if key in ["username", "password", "data_source_desc", "schema_maps"]:
                pass
            else:
                setattr(self.database, key, value)
        await self.db.commit()
        await self.db.refresh(self.database)
        get_db_params = crud_utils.helper_decrypt_db(database=self.database)
        logger.info("Client engine updated and saved in database")
        # TODO: Raise an error if schema maps don't match anything
        return get_db_params

    async def get_connections_to_update(self) -> list[sch.SQLConnSchema]:
        # Get connections to update
        connections_to_update = []
        for connection in self.connections:
            conn_db_to_update = await crud_connection.get_conndb_from_connection(
                db_params=self.db_params, connection=connection
            )
            sql_conn = sch.SQLConnSchema(
                conn_params=conn_db_to_update.conn_params,
                conn_id=connection.conn_id,
                conn_uuid=str(connection.conn_uuid),
                db_id=self.db_id,
                vector_id=connection.database_params.vector_id,
                db_uuid=str(self.db_uuid),
            )
            connections_to_update.append(sql_conn)
        return connections_to_update

    async def update_table_schemas(
        self,
        tables: list[sch.SQLTable],
        index_db_tables: DBTableIndexer,
    ) -> None:
        # Retrieve the tables from the DB
        tables_w_new_schema = []
        tbl_uuids = [table.tbl_uuid for table in tables if table.tbl_uuid is not None]
        db_tables = await crud_table.get_tables_from_uuid(db=self.db, tbl_uuids=tbl_uuids, include_cols=True)
        # Update the table schemas
        for db_table in db_tables:
            for table in tables:
                if str(db_table.tbl_uuid) != str(table.tbl_uuid):
                    continue
                for schema_map in self.db_params.schema_maps:
                    if table.table_schema == schema_map.old_schema:
                        # Update the table schema
                        full_table_name = TableManager.get_full_table_name(
                            table_name=table.table_name, schema=schema_map.new_schema
                        )
                        table.table_schema = schema_map.new_schema
                        table.full_table_name = full_table_name
                        tables_w_new_schema.append(table)
                        # Update the db table as well
                        db_table.table_name = full_table_name
                    # Update the database table columns
                    for db_column in db_table.columns:
                        if db_column.foreign_key_table_name:
                            foreign_key_table_name = db_utils.get_table_name(db_column.foreign_key_table_name)
                            db_column.foreign_key_table_name = TableManager.get_full_table_name(
                                table_name=foreign_key_table_name, schema=schema_map.new_schema
                            )
                    for column in table.columns:
                        if column.foreign_key_table_name:
                            foreign_key_table_name = db_utils.get_table_name(column.foreign_key_table_name)
                            column.foreign_key_table_name = TableManager.get_full_table_name(
                                table_name=foreign_key_table_name, schema=schema_map.new_schema
                            )

        # Update the schema table columns
        # Index any new schemas in the vector database
        # TODO: Submit this to the background
        for table in tables_w_new_schema:
            table_info = TableManager.format_table_info(table=table)
            table.table_info = table_info
        logger.info("Here are the tables w/new schemas: %s", tables_w_new_schema)
        await index_db_tables.update_index_from_tables(
            tables=tables_w_new_schema, redis_client_async=self.redis_client_async
        )
