from datasette import hookimpl
import sqlite_utils


@hookimpl
def startup(datasette):
    async def inner():
        config = datasette.plugin_config("datasette-init")
        for database_name, db_details in config.items():
            database = datasette.get_database(database_name)

            def create_tables_and_views(conn):
                db = sqlite_utils.Database(conn)
                for table, table_details in (db_details.get("tables") or {}).items():
                    if not db[table].exists():
                        db[table].create(
                            table_details["columns"], pk=table_details.get("pk")
                        )
                for view_name, view_definition in (
                    db_details.get("views") or {}
                ).items():
                    db.create_view(view_name, view_definition, replace=True)

            await database.execute_write_fn(create_tables_and_views, block=True)

    return inner
