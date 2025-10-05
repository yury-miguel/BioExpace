# -*- coding: utf-8 -*-

# Autor: Yury
# Data: 05/10/2025

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from datetime import datetime

from flask import Flask, render_template, jsonify, request

from business.handle_db import HandlerDatabase


def init_app(app, handler: HandlerDatabase):
    @app.route('/')
    def index():
        try:
            documents = handler.call('get_documents', limit=100)
            processed_documents = []
            for doc in documents:
                pipeline = handler.call('get_last_llm_memory', pipeline_id=doc.id, model_name='qwen')
                themes = pipeline.get('themes', {}) if pipeline else {}
                processed_documents.append({
                    'id': doc.id,
                    'title': doc.title,
                    'url': doc.url,
                    'date': doc.dat_insercao.strftime('%Y-%m-%d'),
                    'themes': themes
                })
            app.logger.info(f"Fetched {len(processed_documents)} documents for index")
            return render_template('index.html', documents=processed_documents)
        except Exception as e:
            app.logger.error(f"Error in index route: {e}")
            return jsonify({'error': 'Failed to load documents'}), 500

    @app.route('/document/<int:doc_id>')
    def document(doc_id):
        try:
            documents = handler.call('get_documents', limit=1, id=doc_id)
            if not documents:
                app.logger.warning(f"Document {doc_id} not found")
                return jsonify({'error': 'Document not found'}), 404
            doc = documents[0]
            pipeline = handler.call('get_last_llm_memory', pipeline_id=doc.id, model_name='qwen')
            themes = pipeline.get('themes', {}) if pipeline else {}
            document = {
                'id': doc.id,
                'title': doc.title,
                'url': doc.url,
                'text': doc.text_extratect[:1000] + '...' if len(doc.text_extratect) > 1000 else doc.text_extratect,
                'themes': themes
            }
            app.logger.info(f"Fetched document {doc_id}: {doc.title}")
            return render_template('document.html', document=document)
        except Exception as e:
            app.logger.error(f"Error in document route for ID {doc_id}: {e}")
            return jsonify({'error': 'Failed to load document'}), 500

    @app.route('/api/themes', methods=['GET'])
    def get_themes():
        try:
            keyword = request.args.get('keyword', '')
            documents = handler.call('get_documents', limit=1000)
            themes = []
            for doc in documents:
                pipeline = handler.call('get_last_llm_memory', pipeline_id=doc.id, model_name='qwen')
                if pipeline and 'themes' in pipeline:
                    for theme, details in pipeline['themes'].items():
                        if keyword.lower() in theme.lower():
                            themes.append({'theme': theme, 'details': details})
            app.logger.info(f"Fetched {len(themes)} themes for keyword: {keyword}")
            return jsonify(themes)
        except Exception as e:
            app.logger.error(f"Error in themes API: {e}")
            return jsonify({'error': 'Failed to fetch themes'}), 500