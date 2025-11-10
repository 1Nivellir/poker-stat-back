from sqlmodel import Session, SQLModel, create_engine, select
import os
# from app import crud
# from app.core.config import settings
# from app.models import User, UserCreate
from app.core.config import settings
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
def init_db(session: Session) -> None:
    print('init db')
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)
