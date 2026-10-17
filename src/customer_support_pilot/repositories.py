from psycopg import OperationalError
from psycopg_pool import ConnectionPool
from customer_support_pilot.schemas import TicketUpdateRequest


class TicketRepository:
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def find_for_customer(
        self,
        customer_id: str,
        ticket_id: str | None = None,
    ) -> list[dict]:
        query = """
            SELECT ticket_id, customer_id, department, subject,
                   status, latest_update, updated_at, version
            FROM fox_insurance.tickets
            WHERE customer_id = %s
        """
        parameters = [customer_id]

        if ticket_id is not None:
            query += " AND ticket_id = %s"
            parameters.append(ticket_id)

        query += " ORDER BY updated_at DESC, ticket_id"

        try:
            with self._pool.connection() as connection:
                rows = connection.execute(query, parameters).fetchall()
        except OperationalError as error:
            raise ConnectionError(
                "Ticket database is unavailable."
            ) from error

        return [
            {**row, "updated_at": row["updated_at"].isoformat()}
            for row in rows
        ]
    
    def update_if_version_matches(
        self,
        request: TicketUpdateRequest,
    ) -> dict | None:
        """Update a ticket only if its customer and reviewed version match."""

        query = """
            UPDATE fox_insurance.tickets
            SET status = %s,
                latest_update = %s,
                updated_at = CURRENT_TIMESTAMP,
                version = version + 1
            WHERE customer_id = %s
              AND ticket_id = %s
              AND version = %s
            RETURNING ticket_id, customer_id, department, subject,
                      status, latest_update, updated_at, version
        """

        parameters = (
            request.new_status,
            request.note,
            request.customer_id.strip().upper(),
            request.ticket_id.strip().upper(),
            request.expected_version,
        )

        try:
            with self._pool.connection() as connection:
                with connection.transaction():
                    row = connection.execute(
                        query,
                        parameters,
                    ).fetchone()
        except OperationalError as error:
            raise ConnectionError(
                "The ticket update result could not be confirmed."
            ) from error

        if row is None:
            return None

        return {
            **row,
            "updated_at": row["updated_at"].isoformat(),
        }