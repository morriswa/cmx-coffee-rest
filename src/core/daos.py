

from app import connections

from core.models import Territory


def get_approved_territories():
    with connections.cursor() as cur:
        cur.execute("select * from vendor_approved_territory")
        res = cur.fetchall()
        return [Territory(**data) for data in res]
