"""
Base SQLAlchemy configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def get_engine(connection_string: str):
    """Create SQLAlchemy engine from connection string."""
    return create_engine(connection_string, echo=False)


def get_session(connection_string: str):
    """Create SQLAlchemy session from connection string."""
    engine = get_engine(connection_string)
    Session = sessionmaker(bind=engine)
    return Session()
