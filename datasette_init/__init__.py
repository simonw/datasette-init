from datasette import hookimpl
import sqlite_utils


@hookimpl
def startup(datasette):
    async def inner():
        config = datasette.plugin_config("datasette-init")
        for database_name, db_details in config.items():
            database = datasette.get_database(database_name)
            for table, table_details in (db_details.get("tables") or {}).items():

                def create_table(conn):
                    db = sqlite_utils.Database(conn)
                    if not db[table].exists():
                        db[table].create(
                            table_details["columns"], pk=table_details.get("pk")
                        )

                await database.execute_write_fn(create_table, block=True)

    return inner
