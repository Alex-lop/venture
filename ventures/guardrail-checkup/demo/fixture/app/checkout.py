"""Checkout: charge once, then mark the order paid."""

from db import queries


def complete(conn, gateway, order_id):
    order = queries.order_by_id(conn, order_id)
    gateway.charge(order["id"], order["total_cents"])
    queries.mark_paid(conn, order_id)
