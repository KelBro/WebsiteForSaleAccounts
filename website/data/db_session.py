import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SqlAlchemyBase = declarative_base()
__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return

    db_exists = os.path.exists(db_file)

    engine = create_engine(
        f'sqlite:///{db_file}?check_same_thread=False',
        echo=False
    )

    if not db_exists:
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        print(f"Создана новая база данных: {db_file}")
    else:
        print(f"Используется существующая база данных: {db_file}")

    from website.data import __all_models

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    required_tables = SqlAlchemyBase.metadata.tables.keys()

    tables_to_create = [table for table in required_tables if table not in existing_tables]

    if tables_to_create:
        print(f"Создаем таблицы: {', '.join(tables_to_create)}")
        for table_name in tables_to_create:
            table = SqlAlchemyBase.metadata.tables[table_name]
            table.create(bind=engine)
    else:
        print("Все таблицы уже существуют")

    # Создаем фабрику сессий
    __factory = sessionmaker(bind=engine)


def create_session():
    if not __factory:
        raise RuntimeError("Database not initialized! Call global_init() first.")
    return __factory()