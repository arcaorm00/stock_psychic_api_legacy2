from com_stock_api.ext.db import db
from com_stock_api.resources.board import BoardDto
from com_stock_api.resources.member import MemberDto
import datetime

from com_stock_api.ext.db import db
import pandas as pd
import json

from flask import request, jsonify
from flask_restful import Resource, reqparse
import datetime

class CommentDto(db.Model):

    __tablename__ = "comments"
    __table_args__ = {"mysql_collate": "utf8_general_ci"}

    id: int = db.Column(db.Integer, primary_key=True, index=True)
    board_id: int = db.Column(db.Integer, db.ForeignKey(BoardDto.id), nullable=False)
    email: str = db.Column(db.String(100), db.ForeignKey(MemberDto.email), nullable=False)
    comment: str = db.Column(db.String(500), nullable=False)
    regdate: datetime = db.Column(db.String(1000), default=datetime.datetime.now(), nullable=False)
    comment_ref: int = db.Column(db.Integer, nullable=False)
    comment_level: int = db.Column(db.Integer, nullable=False)
    comment_step: int = db.Column(db.Integer, nullable=False)

    board = db.relationship('BoardDto', back_populates='comments')

    def __init__(self, board_id, email, comment, regdate, comment_ref, comment_level, comment_step):
        self.board_id = board_id
        self.email = email
        self.comment = comment
        self.regdate = regdate
        self.comment_ref = comment_ref
        self.comment_level = comment_level
        self.comment_step = comment_step

    def __repr__(self):
        return f'id={self.id}, board_id={self.board_id}, email={self.email}, comment={self.comment}, regdate={self.regdate}, ref={self.comment_ref}, level={self.comment_level}, step={self.comment_step}'

    @property
    def json(self):
        return {
            'id': self.id,
            'board_id': self.board_id,
            'email': self.email,
            'comment': self.comment,
            'regdate': self.regdate,
            'comment_ref': self.comment_ref,
            'comment_level': self.comment_level,
            'comment_step': self.comment_step
        }

class CommentVo:
    id: int = 0
    board_id: int = 0
    email: str = ''
    comment: str = ''
    regdate: datetime = datetime.datetime.now()
    comment_ref: int = 0
    comment_level: int = 0
    comment_step: int = 0

# ref, level, step은 대댓글 기능을 위함

# ref: 최초 댓글 - 자신의 id / 대댓글 - 모댓글 ref
# level: 최초 댓글 - 0 / 대댓글 - 모댓글 level + 1
# step: 최초 댓글 - 0 / 대댓글 - 모댓글과 ref가 같은 댓글 중 모댓글보다 step이 큰 댓글 모두 step +1 이후 자신은 모댓글 step +1

'''
순서		    ref	    level	step
1		        1	    0	    0
	5	        1	    1	    1
        7	    1	    2	    2
	4	        1	    1	    3
	    6	    1	    2	    4
2		        2	    0	    0
3		        3	    0	    0

* 정렬 기준: ref asc 우선 -> step asc
'''







class CommentDao(CommentDto):

    def __init__(self):
        ...

    @classmethod
    def find_all(cls):
        sql = cls.query
        df = pd.read_sql(sql.statement, sql.session.bind)
        return json.loads(df.to_json(orient='records'))

    @classmethod
    def find_by_id(cls, id):
        sql = cls.query.filter(cls.id.like(id))
        df = pd.read_sql(sql.statement, sql.session.bind)
        print(json.loads(df.to_json(orient='records')))
        return json.loads(df.to_json(orient='records'))

    @classmethod
    def find_by_boardid(cls, board_id):
        sql = cls.query.filter(cls.board_id.like(board_id))
        df = pd.read_sql(sql.statement, sql.session.bind)
        # print(json.loads(df.to_json(orient='records')))
        return json.loads(df.to_json(orient='records'))
    
    @staticmethod
    def save(comment):
        db.session.add(comment)
        db.session.commit()

    @staticmethod
    def modify_comment(comment):
        db.session.add(comment)
        db.session.commit()

    @classmethod
    def delete_comment(cls, id):
        data = cls.query.get(id)
        db.session.delete(data)
        db.session.commit()





# =====================================================================
# =====================================================================
# ============================ controller =============================
# =====================================================================
# =====================================================================





parser = reqparse.RequestParser()
parser.add_argument('id', type=int, required=True, help='This field cannot be left blank')
parser.add_argument('board_id', type=int)
parser.add_argument('email', type=str)
parser.add_argument('comment', type=str)
parser.add_argument('regdate', type=str)
parser.add_argument('comment_ref', type=int)
parser.add_argument('comment_level', type=int)
parser.add_argument('comment_step', type=int)


class Comment(Resource):
    
    @staticmethod
    def post():
        body = request.get_json()
        print(f'body: {body}')
        comment = CommentDto(**body)
        CommentDao.save(comment)
        content = comment.comment
        return {'comment': str(content)}, 200
    
    @staticmethod
    def get(id):
        try:
            comment = CommentDao.find_by_id(id)
            if comment:
                return comment
        except Exception as e:
            print(e)
            return {'message': 'Comment not found'}, 404

    @staticmethod
    def update():
        args = request.get_json()
        print(f'Comment {args["id"]} updated')
        return {'code': 0, 'message': 'SUCCESS'}, 200
   
    @staticmethod
    def delete():
        print('여 기 온 다 네')
        args = parser.parse_args()
        print(f'Comment {args["id"]} deleted')
        return {'code': 0, 'message': 'SUCCESS'}, 200
    
class Comments(Resource):
    def post(self):
        c_dao = CommentDao()
        c_dao.insert_many('boards')

    def get(self, id):
        data = CommentDao.find_by_boardid(id)
        return data, 200



