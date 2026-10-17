import hashlib
import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from psycopg.rows import dict_row

from customer_support_pilot.context import SupportContext
from psycopg_pool import ConnectionPool


def build_thread_config(
    conversation_id: UUID,
    context: SupportContext,
) -> dict:
    access_scope = json.dumps(
        {
            "role": context.role,
            "customer_ids": sorted(context.allowed_customer_ids),
        },
        sort_keys=True,
    )
    scope_hash = hashlib.sha256(access_scope.encode()).hexdigest()
    thread_id = f"{context.employee_id}:{scope_hash}:{conversation_id}"

    return {"configurable": {"thread_id": thread_id}}


@contextmanager
def open_checkpointer() -> Iterator[PostgresSaver]:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is missing from .env.")

    with psycopg.connect(
        database_url,
        sslmode="require",
        connect_timeout=10,
        autocommit=True,
        prepare_threshold=0,
        row_factory=dict_row,
    ) as connection:
        connection.execute("SET search_path TO fox_insurance, pg_catalog")

        row = connection.execute(
            "SELECT current_schema() AS schema_name"
        ).fetchone()

        if row["schema_name"] != "fox_insurance":
            raise RuntimeError("Create the fox_insurance schema first.")
        serializer = JsonPlusSerializer(
            allowed_msgpack_modules=[
                ("customer_support_pilot.schemas", "SupportResponse"),
            ],
        )

        yield PostgresSaver(connection, serde=serializer)

@contextmanager
def open_database_pool() -> Iterator[ConnectionPool]:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is missing from .env.")

    with ConnectionPool(
        conninfo=database_url,
        min_size=1,
        max_size=4,
        open=False,
        timeout=10,
        kwargs={
            "sslmode": "require",
            "connect_timeout": 10,
            "autocommit": True,
            "prepare_threshold": 0,
            "row_factory": dict_row,
        },
    ) as pool:
        pool.wait(timeout=10)
        yield pool