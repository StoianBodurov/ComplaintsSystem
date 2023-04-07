from decouple import config
import databases
import sqlalchemy

DATABASE_URL = f'postgresql://{config("DB_USER")}:{config("DB_PASSWORD")}@localhost:{config("DB_PORT")}/complain'
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

