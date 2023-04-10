import base64

from fastapi import HTTPException

from db import database
from models import complaint, user


def decode_photo(path, encoded_string):
    with open(path, 'wb') as f:
        try:
            f.write(base64.b64decode(encoded_string.encode('utf-8')))
        except Exception:
            raise HTTPException(status_code=400, detail='Invalid photo encoding')


async def get_complainer_email_by_complain_id(complain_id):
    complain_db = await database.fetch_one(complaint.select().where(complaint.c.id == complain_id))
    complainer_id = complain_db['complainer_id']
    user_db = await database.fetch_one(user.select().where(user.c.id == complainer_id))
    user_email = user_db['email']
    return user_email
