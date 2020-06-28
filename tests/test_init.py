from datasette.app import Datasette
import pytest
import sqlite_utils
import httpx


def build_datasette(tmp_path_factory, init={}, db_init=None):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    db = sqlite_utils.Database(db_path)
    if db_init:
        db_init(db)
    db.vacuum()
    ds = Datasette([db_path], metadata={"plugins": {"datasette-init": {"test": init}}})
    return ds


@pytest.mark.asyncio
async def test_tables(tmp_path_factory):
    ds = build_datasette(
        tmp_path_factory,
        {
            "tables": {
                "dogs": {
                    "columns": {
                        "id": "integer",
                        "name": "text",
                        "age": "integer",
                        "weight": "float",
                    },
                    "pk": "id",
                }
            }
        },
    )
    await ds.invoke_startup()
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/test/dogs.json")
        assert 200 == response.status_code
        data = response.json()
        assert ["id", "name", "age", "weight"] == data["columns"]
        assert ["id"] == data["primary_keys"]


@pytest.mark.asyncio
async def test_ignore_if_table_already_exists(tmp_path_factory):
    ds = build_datasette(
        tmp_path_factory,
        {"tables": {"dogs": {"columns": {"id": "integer"}, "pk": "id",}}},
        db_init=lambda db: db["dogs"].create({"id": int}),
    )
    await ds.invoke_startup()
