import sqlalchemy

from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Catalog(SqlAlchemyBase):
    __tablename__ = 'catalog_accounts'

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True)
    name_game = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name_product = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hash_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    count = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    def set_password(self, password):
        self.hash_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hash_password, password)
