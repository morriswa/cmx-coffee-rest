from psycopg2 import errors

from app.connections import cursor
from app.exceptions import BadRequestException


def register(email: str):
    with cursor() as cur:
        cur.execute("""select 1 as present from auth_integration where email = %(email)s""", {'email': email})
        result = cur.fetchone() or {'present': 0}
        is_present = result.get('present') == 1
        if not is_present:
            cur.execute("""insert into auth_integration (email) values (%(email)s)""", {'email': email})
