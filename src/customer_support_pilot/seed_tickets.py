from dotenv import load_dotenv

from customer_support_pilot.persistence import open_database_pool
from customer_support_pilot.records import TICKETS


INSERT_TICKET = """
    INSERT INTO fox_insurance.tickets (
        ticket_id, customer_id, department, subject,
        status, latest_update, updated_at
    )
    VALUES (
        %(ticket_id)s, %(customer_id)s, %(department)s, %(subject)s,
        %(status)s, %(latest_update)s, %(updated_at)s
    )
    ON CONFLICT (ticket_id) DO NOTHING
"""


def main() -> None:
    load_dotenv()
    inserted = 0

    with open_database_pool() as pool:
        with pool.connection() as connection:
            with connection.transaction():
                for ticket in TICKETS.values():
                    cursor = connection.execute(INSERT_TICKET, ticket)
                    inserted += cursor.rowcount

    print(
        f"Inserted {inserted} tickets. "
        "Existing tickets were preserved."
    )


if __name__ == "__main__":
    main()