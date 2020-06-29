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


@pytest.mark.asyncio
async def test_tables_compound_primary_key(tmp_path_factory):
    ds = build_datasette(
        tmp_path_factory,
        {
            "tables": {
                "dogs": {
                    "columns": {"id1": "integer", "id2": "integer", "name": "text",},
                    "pk": ["id1", "id2"],
                }
            }
        },
    )
    await ds.invoke_startup()
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/test/dogs.json")
        assert 200 == response.status_code
        data = response.json()
        assert ["id1", "id2", "name"] == data["columns"]
        assert ["id1", "id2"] == data["primary_keys"]


@pytest.mark.asyncio
async def test_views(tmp_path_factory):
    ds = build_datasette(tmp_path_factory, {"views": {"two": "select 1 + 1"}})
    await ds.invoke_startup()
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/test/two.json?_shape=array")
        assert 200 == response.status_code
        assert [{"1 + 1": 2}] == response.json()


@pytest.mark.asyncio
async def test_replace_view_if_already_exists(tmp_path_factory):
    ds = build_datasette(
        tmp_path_factory,
        {"views": {"two": "select 1 + 1"}},
        db_init=lambda db: db.create_view("two", "select 1 + 3"),
    )
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/test/two.json?_shape=array")
        assert [{"1 + 3": 4}] == response.json()
        await ds.invoke_startup()
        response2 = await client.get("http://localhost/test/two.json?_shape=array")
        assert [{"1 + 1": 2}] == response2.json()


@pytest.mark.asyncio
async def test_no_error_if_no_metadata():
    ds = Datasette([], memory=True)
    await ds.invoke_startup()
    async with httpx.AsyncClient(app=ds.app()) as client:
        assert 200 == (await client.get("http://localhost/")).status_code
