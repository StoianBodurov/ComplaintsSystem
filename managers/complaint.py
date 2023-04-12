import os
import uuid

from constans import TEMP_FILE_FOLDER
from db import database
from models import complaint, RoleType, State, user, transaction
from services.s3 import S3Services
from services.ses import SESServices
from services.wise import WiseService
from utils.helpers import decode_photo, get_complainer_email_by_complain_id

s3 = S3Services()
ses = SESServices()
wise = WiseService()


class ComplaintManager:
    @staticmethod
    async def get_complaints(user):
        q = complaint.select()
        if user['role'] == RoleType.complainer:
            q = q.where(complaint.c.complainer_id == user['id'])
        elif user['role'] == RoleType.approver:
            q = q.where(complaint.c.state == State.pending)
        return await database.fetch_all(q)

    @staticmethod
    async def create_complaint(complaint_data, user):
        data = complaint_data.dict()
        data['complainer_id'] = user['id']
        encoded_photo = data.pop('encoded_photo')
        ext = data.pop('extension')
        name = f'{uuid.uuid4()}.{ext}'
        path = os.path.join(TEMP_FILE_FOLDER, name)
        decode_photo(path, encoded_photo)
        data['photo_url'] = s3.upload_photo(path, name, ext)
        os.remove(path)
        id_ = await database.execute(complaint.insert().values(**data))
        await ComplaintManager.issue_transaction(data['amount'], f'{user["first_name"]} {user["last_name"]}', id_)
        return await database.fetch_one(complaint.select().where(complaint.c.id == id_))

    @staticmethod
    async def delete(complaint_id):
        complaint_db = await database.fetch_one(complaint.select().where(complaint.c.id == complaint_id))
        photo = complaint_db['photo_url'].split('/')[-1]
        await database.execute(complaint.delete().where(complaint.c.id == complaint_id))
        s3.delete_photo(photo)

    @staticmethod
    async def approve(complain_id):
        user_email = await get_complainer_email_by_complain_id(complain_id)
        await database.execute(complaint.update().where(complaint.c.id == complain_id).values(status=State.approved))
        transaction_data = await database.fetch_one(transaction.select().where(transaction.c.complaint_id == complain_id))
        wise.fund_transfer(transaction_data['transfer_id'])
        ses.send_email('Your complaint is approved', [user_email], 'Congrats! Your complaint is approved.')

    @staticmethod
    async def reject(complain_id):
        user_email = await get_complainer_email_by_complain_id(complain_id)
        transaction_data = await database.fetch_one(transaction.select().where(transaction.c.complaint_id == complain_id))
        wise.cancel_transfer(transaction_data['transfer_id'])
        await database.execute(complaint.update().where(complaint.c.id == complain_id).values(status=State.rejected))
        ses.send_email('Your complaint is rejected', [user_email], 'Sorry! Your complaint is rejected.')

    @staticmethod
    async def issue_transaction(amount, full_name, iban, complaint_id):
        quote_id = wise.create_quote(amount)
        recipient_id = wise.create_recipient_account(full_name, iban)
        transfer_id = wise.create_transfer(recipient_id, quote_id)
        data = {
            'quote_id': quote_id,
            'transfer_id': transfer_id,
            'target_account_id': str(recipient_id),
            'amount': amount,
            'complaint_id': complaint_id
        }
        await database.execute(transaction.insert().values(**data))
