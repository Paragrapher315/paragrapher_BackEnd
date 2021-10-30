import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = None

def make_connection(username , password , host , db_name):
    engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}'.format(username , password , host  , db_name ), echo=True)
    return engine 

def make_session(engine):
    Session = db.orm.sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    return session

def init_db(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB):
    global engine
    try:
        engine = make_connection(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB)
        init_tables(engine)
        return engine
    except Exception as e:
        print(e)
        exit(1)

def init_tables(engine):
    Base.metadata.create_all(engine)
