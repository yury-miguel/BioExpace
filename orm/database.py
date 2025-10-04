# -*- coding: utf-8 -*-

# Author: Yury
# Data: 04/10/2025


import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from logs import config as save
from models_bio.models_db import (Publications)
log = save.setup_logs('database_debug.txt')


load_dotenv()
Base = declarative_base()


class DbError(Exception):
    """Catches exceptions when using the database"""
    pass


class Database:
    def __init__(self):
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASS")
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.name = os.getenv("DB_NAME")
        
        self.engine = create_engine(
            f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}",
            echo=False,
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def insert_publication(self, title: str, url: str, raw_html: str, text_extratect: str):
        """Insert a post into the table nasa.publication"""
        session = self.Session()
        try:
            pub = Publications(
                title=title,
                url=url,
                raw_html=raw_html,
                text_extratect=text_extratect,
            )
            session.add(pub)
            session.commit()
            log.info(f"✅ Save the database: {title}")
            return "success"

        except Exception as errors:
            session.rollback()
            message = f"❌ Error saving to the database {title}: {errors}"
            log.error(message)
            raise DbError(message) from errors

        finally:
            session.close()
