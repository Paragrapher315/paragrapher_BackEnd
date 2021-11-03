import sqlalchemy as db
from flask import redirect, url_for
from sqlalchemy.sql.functions import user
from sqlalchemy.orm import backref
from tools.db_tool import make_session, Base, engine
from tools.crypt_tool import app_bcrypt
from sqlalchemy.ext.declarative import declarative_base
import re
import datetime

association_table = db.Table('association', Base.metadata,
                             db.Column(db.VARCHAR(30), db.ForeignKey('paragraph.id'),name='p_id', primary_key=True),
                             db.Column(db.SMALLINT, db.ForeignKey('tags.id'),name='tag', primary_key=True)
                             )


class paragraph_model(Base):
    __tablename__ = "paragraph"
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    p_text = db.Column(db.VARCHAR(250), nullable=False)
    ref_book = db.Column(db.VARCHAR(100))
    date = db.Column(db.DATETIME, nullable=False)
    replied_id = db.Column(db.BIGINT, db.ForeignKey("paragraph.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tags = db.relationship("tags_model", secondary=association_table, backref="paragraph")
    replies = db.relatoinship("paragraph_model", backref="replied")
    impressions = db.relationship("impressions", backref=backref("paragraph", lazy="dynamic"))
    ima_count = db.Column(db.BIGINT, default=0)


def change_impression(user, paragraph, engine, increment=True):
    """
    :param user:
    :param paragraph:
    :param increment: True for increase impression and False for delete
    :return:
    """
    pass


class impressions(Base):
    p_id = db.Column(db.BIGINT, db.ForeignKey("paragraph.id"), primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)



class tags_model(Base):
    __tablename__ = "tags"
    id = db.Column(db.SMALLINT, primary_key=True)
    name = db.Column(db.VARCHAR(50), unique=True)
