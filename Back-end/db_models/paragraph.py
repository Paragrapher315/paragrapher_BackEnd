import sqlalchemy as db
from flask import redirect, url_for
from sqlalchemy.sql.functions import user
from sqlalchemy.orm import backref
from tools.db_tool import make_session, Base, engine
from tools.crypt_tool import app_bcrypt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import  relationship

import re
import datetime

association_table = db.Table('association', Base.metadata,
                             db.Column(db.BIGINT, db.ForeignKey('paragraph.id'),name='p_id', primary_key=True),
                             db.Column(db.SMALLINT, db.ForeignKey('tags.id'),name='tag', primary_key=True)
                             )


class paragraph_model(Base):
    __tablename__ = "paragraph"
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    p_text = db.Column(db.VARCHAR(250), nullable=False)
    ref_book = db.Column(db.VARCHAR(100))
    date = db.Column(db.DATETIME, nullable=False)
    replied_id = db.Column(db.BIGINT, db.ForeignKey("paragraph.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    community_id = db.Column(db.VARCHAR(30) , db.ForeignKey("community.id") , nullable=False)
    tags = relationship("tags_model", secondary=association_table, backref="paragraph")
    #replies = relationship("paragraph_model", backref="replied")
    impressions = relationship("impressions",  backref=backref("pragraph"), lazy="subquery",cascade="all, delete-orphan")
    ima_count = db.Column(db.BIGINT, default=0)

def add_paragraph( text , ref , user_id , community_id , engine):
    session = make_session(engine)
    jwk_user = paragraph_model(p_text=text, ref_book=ref ,  user_id=user_id , community_id=community_id, engine=engine)
    session.add(jwk_user)
    session.commit()
    return jwk_user

class POD(Base):
    """
    for saving the paragraph of the day for a community on a specified date
    """
    __tablename__ = "pod"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_id = db.Column(db.VARCHAR(30), db.ForeignKey("community.id"), nullable=False)
    date = db.Column(db.DATE, nullable=False)
    p_id = db.Column(db.BIGINT, db.ForeignKey("paragraph.id"))
    paragraph = relationship("paragraph_model", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("c_id", "date", name="date_community_u"),
    )

    def __init__(self, date, c_id, paragraph):
        self.c_id = c_id
        self.date = date
        self.paragraph = paragraph

def change_impression(user, paragraph, engine, increment=True):
    """
    :param user:
    :param paragraph:
    :param increment: True for increase impression and False for delete
    :return:
    """
    pass


class impressions(Base):
    __tablename__ = "impressions"
    p_id = db.Column(db.BIGINT, db.ForeignKey("paragraph.id"), primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey("Users.id"), primary_key=True)



class tags_model(Base):
    __tablename__ = "tags"
    id = db.Column(db.SMALLINT, primary_key=True)
    name = db.Column(db.VARCHAR(50), unique=True)
