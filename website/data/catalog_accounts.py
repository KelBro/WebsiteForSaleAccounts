import sqlalchemy

from website.data.db_session import SqlAlchemyBase


class Catalog(SqlAlchemyBase):
    __tablename__ = 'catalog_accounts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    game_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    product_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
