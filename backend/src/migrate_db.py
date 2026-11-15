from sqlalchemy import create_engine

from src.helper.config import settings
from src.models.task import Base
from src.models.user import Base as Base2

engine = create_engine(settings.DATABASE_URL, echo=True)


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # TODO: もうちょっと良い感じにしたい
    Base2.metadata.drop_all(bind=engine)
    Base2.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_database()
