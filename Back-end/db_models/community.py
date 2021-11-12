import sqlalchemy as db
from flask import redirect, url_for
from sqlalchemy.sql.functions import user
from sqlalchemy.orm import backref
from tools.db_tool import make_session, Base
from tools.crypt_tool import app_bcrypt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from db_models.users import UserModel
import datetime


class community_model(Base):
    __tablename__ = "community"
    id = db.Column(db.VARCHAR(30), primary_key=True)
    name = db.Column(db.VARCHAR(36), unique=True)
    creation_date = db.Column(db.DATE, name="creation_date")
    image = db.Column(db.VARCHAR(150), nullable=True)
    members = relationship("community_member", backref=backref("community"), lazy="subquery",
                           cascade="all, delete-orphan")
    member_count = db.Column(db.Integer, default=0, nullable=False)
    description = db.Column(db.VARCHAR(250), nullable=True)

    def __init__(self, name, m_id, engine):
        self.id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        self.name = name
        self.creation_date = datetime.date.today()
        # add_community_member(c_id=self.id, user_id=m_id , role = 1 , engine=engine)

    @property
    def json(self):
        dic = {"name": self.name,
               "creation_date": self.creation_date,
               "avatar": self.image,
               "member_count": self.member_count,
               "description": self.description
               }
        return dic

    def get_members_json(self):
        mems = self.members
        memlist = []
        for m in mems:
            memlist.append(m.member.json)

        return memlist

    def get_one_member(self, user_id):
        for member in self.members:
            if member.m_id == user_id:
                return member
        return None


def change_community_desc(c_name, description, engine):
    session = make_session(engine)
    print("\n\nchange ", c_name, " \ndes ", description)
    session.query(community_model).filter(community_model.name == c_name).update({community_model.description: description})
    session.flush()
    session.commit()
    return "ok", 200


def change_community_image(current_user: UserModel, name, url, engine):
    session = make_session(engine)
    session.query(community_model).filter(community_model.name == name).update({community_model.image: url})
    session.flush()
    session.commit()
    return "ok", 200


class community_member(Base):
    __tablename__ = "community_member"
    id = db.Column(db.VARCHAR(30), primary_key=True)
    m_id = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)
    role = db.Column(db.SMALLINT, nullable=False, default=2)  # role 1 for admin | role 2 for member
    c_id = db.Column(db.VARCHAR(30), db.ForeignKey("community.id"), nullable=False)
    __table_args__ = (
        db.UniqueConstraint("c_id", "m_id", name="member_community_u"),
    )

    def __init__(self, c_id, m_id, role=2):
        self.id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        self.c_id = c_id
        self.m_id = m_id
        self.role = role

    @property
    def json(self):
        dic = {"c_id": self.c_id,
               "m_id": self.m_id,
               "role": self.role,
               }
        return dic


def get_role(user_id, community_id, engine):
    session = make_session(engine)
    mem_c: community_member = session.query(community_member).filter(
        db.and_(community_member.m_id == user_id, community_member.c_id == community_id)).first()
    if mem_c == None:
        return -1
    return mem_c.role


def delete_member(user_id, community_id, engine):
    session = make_session(engine)
    mem_c: community_member = session.query(community_member).filter(
        db.and_(community_member.m_id == user_id, community_member.c_id == community_id)).first()
    session.delete(mem_c)
    com: community_model = session.query(community_model).filter(community_model.id == community_id).first()
    com.member_count -= 1
    session.commit()


def get_community(name, engine):
    session = make_session(engine)
    our_community: community_model = session.query(community_model).filter((community_model.name == name)).first()
    return our_community


def add_community(name, user_id, engine):
    session = make_session(engine)
    jwk_user = community_model(name=name, m_id=user_id, engine=engine)
    session.add(jwk_user)
    session.commit()
    add_community_member(jwk_user.id, user_id, 1, engine)
    return jwk_user


def add_community_member(c_id, user_id, role, engine):
    session = make_session(engine)
    jwk_user = community_member(c_id=c_id, m_id=user_id, role=role)
    com: community_model = session.query(community_model).filter(community_model.id == c_id).first()
    com.member_count += 1
    session.add(jwk_user)
    session.commit()