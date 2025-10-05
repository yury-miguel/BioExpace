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
from models_bio.models_db import (Publications, LlmPipeline, LlmMemory)
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
            log.info(f"Save the database: {title}")
            return "success"

        except Exception as errors:
            session.rollback()
            message = f"Error saving to the database {title}: {errors}"
            log.error(message)
            raise DbError(message) from errors

        finally:
            session.close()

    def insert_llm_pipeline(self, publication_id, stage, result_json=None, status="running", message=None):
        """Creates or updates the execution record of an LLM step"""
        session = self.Session()
        try:
            pipeline = LlmPipeline(
                publication_id=publication_id,
                stage=stage,
                result_json=result_json,
                status=status,
                message=message,
            )
            session.add(pipeline)
            session.commit()
            return pipeline.id

        except Exception as errors:
            session.rollback()
            log.error(f"Error saving pipeline {stage}: {errors}")
            raise DbError(errors)
        finally:
            session.close()

    def insert_llm_memory(self, pipeline_id, model_name, chunk_index, context_json):
        """Saves the state (incremental memory) of an LLM run"""
        session = self.Session()
        try:
            mem = LlmMemory(
                pipeline_id=pipeline_id,
                model_name=model_name,
                chunk_index=chunk_index,
                context_json=context_json,
            )
            session.add(mem)
            session.commit()
            return mem.id

        except Exception as errors:
            session.rollback()
            log.error(f"Error saving memory {model_name}: {errors}")
            raise DbError(errors)
        finally:
            session.close()

    def get_documents(self, limit=10):
        """Search for documents not yet processed"""
        session = self.Session()
        try:
            return session.query(Publications).limit(limit).all()
        except Exception as errors:
            log.error(f"Error fetching documents: {errors}")
            raise DbError(e)
        finally:
            session.close()

    def get_last_llm_memory(self, pipeline_id, model_name):
        """Retrieve the last analysis of the document 
        to continue and assimilate where it left off
        """
        session = self.Session()
        try:
            record = (session.query(LlmMemory)
                    .filter_by(pipeline_id=pipeline_id, model_name=model_name)
                    .order_by(LlmMemory.id.desc())
                    .first())
            return record.context_json if record else None
        except Exception as errors:
            log.error(f"Error fetching memory: {errors}")
            raise DbError(errors)
        finally:
            session.close()