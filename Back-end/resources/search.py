import os
from http import HTTPStatus as hs
from flask_restful import Resource, reqparse
from flask import request, make_response, jsonify
from tools.db_tool import engine, make_session
from tools.token_tool import authorize, community_role
from typing import List
from sqlalchemy import or_, and_

from db_models.community import community_member, get_community, get_role, community_model
from db_models.paragraph import paragraph_model, POD

from tools.string_tools import gettext


class searcher(Resource):
    def __init__(self, **kwargs):
        self.engine = kwargs['engine']

    @authorize
    def get(self, current_user):
        typer = ''
        text = ''
        try:
            typer = request.args.get('type')
            if typer == None:
                msg = gettext("search_item_needed").format("type")

                return {'message': msg}, hs.BAD_REQUEST
            typer = str(typer)
        except:
            msg = gettext("search_item_needed").format("type")

            return {'message': msg}, hs.BAD_REQUEST
        try:
            text = request.args.get('text')
            if text == None:
                msg = gettext("search_item_needed").format("text")

                return {'message': msg}, hs.BAD_REQUEST
            text = str(text)
        except:
            msg = gettext("search_item_needed").format("type")
            return {'message': msg}, hs.BAD_REQUEST
        print("$$$", text)
        req_data = request.json
        start = None 
        end = None
        try:
            print(req_data['start_off'])
            start = int(req_data['start_off'])
        except:
            msg = gettext("search_start_needed")
            return {'message': msg}, hs.BAD_REQUEST

        try:
            print(req_data['end_off'])
            end = int(req_data['end_off'])

        except:
            msg = gettext("search_end_needed")
            return {'message': msg}, hs.BAD_REQUEST

        allComs = self.get_user_community_list(current_user)

        if typer == "community":

            res = self.search_community(text=text , start=start , end=end)
        elif typer == "author":
            res = self.search_author(text=text , start=start , end=end , allComs=allComs)
        elif typer == "book":
            res = self.search_book(text=text , start=start , end=end , allComs=allComs)
        else:
            msg = gettext("search_type_invalid")
            return {'message': msg}, hs.NOT_FOUND
        return make_response({"message": "item founded", 'res': res}, hs.OK)

    def search_community(self, text: str , start , end):
        session = make_session(self.engine)

        coms: List[community_model] = session.query(community_model).filter(
            community_model.name.like("%{}%".format(text))).order_by(community_model.member_count.desc()).slice(start,end).all()

        res = []
        for row in coms:
            res.append(row.json)

        return res

    def get_user_community_list(self,current_user):
        session = make_session(self.engine)

        coms: List[community_member] = session.query(community_member).filter(
            community_member.m_id==current_user.id).all()
        res = []
        for row in coms:
            res.append(row.c_id)

        return res

    def search_author(self, text , start , end , allComs):
        session = make_session(self.engine)

        coms: List[paragraph_model] = session.query(paragraph_model).filter(
            paragraph_model.author.like("%{}%".format(text))).order_by(paragraph_model.ima_count.desc()).slice(start,end).all()

        res = []
        for row in coms:
            if row.community_id in allComs:
                res.append(row.json)

        return res

    def search_book(self, text , start , end , allComs):
        session = make_session(self.engine)
        # search paragraph books
        coms: List[paragraph_model] = session.query(paragraph_model).filter(
            paragraph_model.ref_book.like("%{}%".format(text))).order_by(paragraph_model.ima_count.desc()).slice(start,end).all()

        res = []
        for row in coms:
            if row.community_id in allComs:
                res.append(row.json)

        return res


class community_searcher(Resource):
    def __init__(self, **kwargs):
        self.engine = kwargs['engine']

    @authorize
    @community_role(1, 2)
    def get(self, current_user, name, req_community: community_model, mem_role):

        print("here**************")
        try:
            text = request.args.get('text')
            if text is None or text == "":
                msg = gettext("search_item_needed").format("text")

                return {'message': msg}, hs.BAD_REQUEST
            text = str(text)
        except:
            msg = gettext("search_item_needed").format("text")
            return {'message': msg}, hs.BAD_REQUEST
        print("$$$", text, "\n com:", req_community.name)

        res = self.search_community_paragraph(text, req_community)

        print(res)
        return make_response({"message": "item founded", 'res': res}, hs.OK)

    def search_community_paragraph(self, text, community: community_model, start_off=1, end_off=201):
        session = make_session(self.engine)
        paras: List[paragraph_model] = session.query(paragraph_model).filter(
            and_(paragraph_model.community_id == community.id,
                 or_(paragraph_model.author.like("%{}%".format(text)),
                     paragraph_model.ref_book.like("%{}%".format(text)))
                 )).order_by(paragraph_model.date).slice(start_off, end_off).all()

        res = []
        print("\n\nresult", paras)
        for p in paras:
            res.append(p.json)
            print(p.json)

        return res
