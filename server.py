import pydantic
import re
from typing import Type, Optional
from flask_bcrypt import Bcrypt
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import Column, Integer, String, DateTime, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

app = Flask('app')
bcrypt = Bcrypt(app)


class HttpError(Exception):
    def __init__(self, stats_code: int, message: str | dict | list):
        self.stats_code = stats_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({
        'status': 'error',
        'message': error.message
    })
    response.status_code = error.stats_code
    return response


DSN = 'postgresql://app:1234@localhost:5432/netology'

engine = create_engine(DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)

password_regex = re.compile(
    "^(?=.*[a-z_])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&_])[A-Za-z\d@$!#%*?&_]{8,200}$"
)


class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    password = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())


Base.metadata.create_all(engine)


class CreateUserSchema(pydantic.BaseModel):
    name: str
    password: str

    @pydantic.validator("password")
    def check_name(cls, value: str):
        if len(value) > 32:
            raise ValueError("name mast be less 32 chars")

        return value

    @pydantic.validator("password")
    def check_password(cls, value: str):
        if not re.search(password_regex, value):
            raise ValueError("password to easy")

        value.encode()
        value = bcrypt.generate_password_hash(value)
        value = value.decode()

        return value


class PatchUserSchema(pydantic.BaseModel):
    name: Optional[str]
    password: Optional[str]

    @pydantic.validator("password")
    def check_name(cls, value: str):
        if len(value) > 32:
            raise ValueError("name mast be less 32 chars")

        return value

    @pydantic.validator("password")
    def check_password(cls, value: str):
        if not re.search(password_regex, value):
            raise ValueError("password to easy")

        value.encode()
        value = bcrypt.generate_password_hash(value)
        value = value.decode()

        return value


def validate(data_to_validate: dict, validation_class: Type[CreateUserSchema] | Type[PatchUserSchema]):
    try:
        return validation_class(**data_to_validate).dict(exclude_none=True)
    except pydantic.ValidationError as err:
        raise HttpError(400, err.errors())


def get_by_id(item_id: int, orm_model: Type[UserModel], session: Session):
    orm_item = session.query(orm_model).get(item_id)

    if orm_item is None:
        raise HttpError(404, 'item not found')

    return orm_item


class UserView(MethodView):

    def get(self, user_id: int):
        with Session() as session:
            user = get_by_id(user_id, UserModel, session)

            if user is None:
                raise HttpError(404, 'user not found')

            return jsonify({
                'user': user.name,
                'creation time': user.creation_time.isoformat()
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            try:
                new_user = UserModel(**validate(json_data, CreateUserSchema))
                session.add(new_user)
                session.commit()
            except IntegrityError:
                raise HttpError(409, 'User name already exists')
            return jsonify({'status': 'ok', 'id': new_user.id})

    def patch(self, user_id: int):
        data_to_patch = validate(request.json, PatchUserSchema)

        with Session() as session:
            user = get_by_id(user_id, UserModel, session)

            for field, value in data_to_patch.items():
                setattr(user, field, value)
            session.commit()
            return jsonify({'status': 'success', 'id': user.id})

    def delete(self, user_id: int):
        with Session() as session:
            user = get_by_id(user_id, UserModel, session)
            session.delete(user)
            session.commit()
            return jsonify({'status': 'success', 'id': user.id})


app.add_url_rule('/user/<int:user_id>', view_func=UserView.as_view('users_get'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/user/', view_func=UserView.as_view('users'), methods=['POST'])

app.run()
