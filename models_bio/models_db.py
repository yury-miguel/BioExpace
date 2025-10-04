# -*- coding: utf-8 -*-

# Author: Yury
# Data: 04/10/2025


from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, func


Base = declarative_base()

class Publications(Base):
    __tablename__ = "publications"
    __table_args__ = {"schema": "nasa"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    url = Column(Text)
    raw_html = Column(Text)
    text_extratect = Column(Text)
    dat_insercao = Column(TIMESTAMP, server_default=func.current_timestamp())


class LlmPipeline(Base):
    __tablename__ = "llm_pipeline"
    __table_args__ = {"schema": "nasa"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    publication_id = Column(Integer, nullable=False)
    stage = Column(String(50))  
    status = Column(String(50), default="pending") 
    result_json = Column(JSONB)  
    message = Column(Text)  
    dat_insercao = Column(TIMESTAMP, server_default=func.current_timestamp())


class LlmMemory(Base):
    __tablename__ = "llm_memory"
    __table_args__ = {"schema": "nasa"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(Integer, nullable=False)
    model_name = Column(String(50))
    chunk_index = Column(Integer)
    context_json = Column(JSONB)
    dat_insercao = Column(TIMESTAMP, server_default=func.current_timestamp())