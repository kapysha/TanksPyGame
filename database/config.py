from sqlalchemy import create_engine, Column, Integer, DDL, event, Float
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker, Session, declarative_base

engine = create_engine("sqlite:///main.db")
session = scoped_session(sessionmaker(bind=engine, class_=Session))
Base = declarative_base()


class Main(Base):
    __tablename__ = 'main'
    id = Column(Integer, primary_key=True)
    total_battles = Column(Integer, default=0)
    player_wins = Column(Integer, default=0)
    ai_wins = Column(Integer, default=0)
    player_total_shots = Column(Integer, default=0)
    ai_total_shots = Column(Integer, default=0)
    shortest_battle_duration = Column(Float, default=0.0)
    longest_battle_duration = Column(Float, default=0.0)


@event.listens_for(Main.__table__, 'after_create')
def create_one_field(mapper, connection, **kwargs):
    # Connection: Это объект соединения с базой данных
    # mapper: Это объект, который представляет собой целевую таблицу или модель, на которую ссылается триггер. В данном случае это RaffleInfo.table
    connection.execute(DDL("""
        CREATE TRIGGER one_field
        BEFORE INSERT ON main
        WHEN (SELECT COUNT(*) FROM main) >= 1
        BEGIN
            SELECT RAISE(FAIL, 'Only one row is allowed in the Main table');
        END;
    """))


def create_db():
    Base.metadata.create_all(engine)
    try:
        with session() as sess:
            sess.add(Main())
            sess.commit()
    except IntegrityError:
        return
