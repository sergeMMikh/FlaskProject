from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import Column, Integer, String, DateTime, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask('app')
DSN = 'postgresql://app:1234@127.0.0.1:5432/netology'

engine = create_engine(DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    password = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())


Base.metadata.create_all(engine)


class UserView(MethodView):

    def get(self):
        ...

    def post(self):
        ...

    def patch(self):
        ...

    def delete(self):
        ...


app.add_url_rule('/user/', view_func=UserView.as_view('users'), methods=['GET', 'POST', 'PATCH', 'DELETE'])

app.run()
