"""Every statement that touches Postgres lives here."""


def order_by_id(conn, order_id):
    return conn.execute("SELECT id, total_cents, state FROM orders WHERE id = %s", (order_id,)).fetchone()


def mark_paid(conn, order_id):
    conn.execute("UPDATE orders SET state = 'paid' WHERE id = %s AND state = 'pending'", (order_id,))
