# -*- coding: utf-8 -*-

# Autor: Yury
# Data: 05/10/2025

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from datetime import datetime

from flask import Flask, render_template, jsonify, request

from logs import config as save
from business.handle_db import HandlerDatabase

log = save.setup_logs('flask_debug.txt')

def init_app(app, handler: HandlerDatabase):
    @app.route('/')
    def index():
        try:
            documents = handler.call('get_documents', limit=100)
            processed_documents = []

            for doc in documents:
                pipelines = handler.call('get_pipelines_by_publication', publication_id=doc.id)
                all_memories = []
                for pipe in pipelines:
                    all_memories.extend(handler.call('get_all_llm_memories', pipeline_id=pipe.id, model_name='qwen'))

                merged_themes = {}
                for mem in all_memories:
                    themes = mem.get('themes', {})
                    for theme, details in themes.items():
                        if theme not in merged_themes:
                            merged_themes[theme] = {
                                'points': [],
                                'cause_effects': [],
                                'observations': [],
                                'cascade_effects': [],
                                'impactful': []
                            }
                        for key in merged_themes[theme]:
                            merged_themes[theme][key].extend(details.get(key, []))
                            merged_themes[theme][key] = list(set(merged_themes[theme][key]))

                processed_documents.append({
                    'id': doc.id,
                    'title': doc.title,
                    'url': doc.url,
                    'date': doc.dat_insercao.strftime('%Y-%m-%d'),
                    'themes': merged_themes
                })

            log.info(f"Fetched {len(processed_documents)} documents for index")
            return render_template('index.html', documents=processed_documents)

        except Exception as e:
            log.error(f"Error in index route: {e}")
            return jsonify({'error': 'Failed to load documents'}), 500


    @app.route('/api/documents', methods=['GET'])
    def api_documents():
        try:
            documents = handler.call('get_documents', limit=1000)
            processed_documents = []

            for doc in documents:
                pipelines = handler.call('get_pipelines_by_publication', publication_id=doc.id)
                all_memories = []
                for pipe in pipelines:
                    all_memories.extend(handler.call('get_all_llm_memories', pipeline_id=pipe.id, model_name='qwen'))

                merged_themes = {}
                for mem in all_memories:
                    themes = mem.get('themes', {})
                    for theme, details in themes.items():
                        if theme not in merged_themes:
                            merged_themes[theme] = {
                                'points': [],
                                'cause_effects': [],
                                'observations': [],
                                'cascade_effects': [],
                                'impactful': []
                            }
                        for key in merged_themes[theme]:
                            merged_themes[theme][key].extend(details.get(key, []))
                            merged_themes[theme][key] = list(set(merged_themes[theme][key]))

                processed_documents.append({
                    'id': doc.id,
                    'title': doc.title,
                    'url': doc.url,
                    'date': doc.dat_insercao.strftime('%Y-%m-%d'),
                    'themes': merged_themes
                })

            log.info(f"Fetched {len(processed_documents)} documents for API")
            return jsonify(processed_documents)

        except Exception as e:
            log.error(f"Error fetching documents API: {e}")
            return jsonify({'error': 'Failed to load documents'}), 500


    @app.route('/document/<int:doc_id>')
    def document(doc_id):
        try:
            documents = handler.call('get_documents', limit=1, id=doc_id)
            if not documents:
                log.warning(f"Document {doc_id} not found")
                return jsonify({'error': 'Document not found'}), 404

            doc = documents[0]
            pipelines = handler.call('get_pipelines_by_publication', publication_id=doc.id)
            all_memories = []
            for pipe in pipelines:
                all_memories.extend(handler.call('get_all_llm_memories', pipeline_id=pipe.id, model_name='qwen'))

            merged_themes = {}
            for mem in all_memories:
                themes = mem.get('themes', {})
                for theme, details in themes.items():
                    if theme not in merged_themes:
                        merged_themes[theme] = {
                            'points': [],
                            'cause_effects': [],
                            'observations': [],
                            'cascade_effects': [],
                            'impactful': []
                        }
                    for key in merged_themes[theme]:
                        merged_themes[theme][key].extend(details.get(key, []))
                        merged_themes[theme][key] = list(set(merged_themes[theme][key]))

            document = {
                'id': doc.id,
                'title': doc.title,
                'url': doc.url,
                'text': doc.text_extratect[:1000] + '...' if len(doc.text_extratect) > 1000 else doc.text_extratect,
                'themes': merged_themes
            }

            log.info(f"Fetched document {doc_id}: {doc.title}")
            return render_template('document.html', document=document)

        except Exception as e:
            log.error(f"Error in document route for ID {doc_id}: {e}")
            return jsonify({'error': 'Failed to load document'}), 500


    @app.route('/api/themes', methods=['GET'])
    def get_themes():
        try:
            keyword = request.args.get('keyword', '')
            documents = handler.call('get_documents', limit=1000)
            themes = []

            for doc in documents:
                pipelines = handler.call('get_pipelines_by_publication', publication_id=doc.id)
                all_memories = []
                for pipe in pipelines:
                    all_memories.extend(handler.call('get_all_llm_memories', pipeline_id=pipe.id, model_name='qwen'))

                merged_themes = {}
                for mem in all_memories:
                    doc_themes = mem.get('themes', {})
                    for theme, details in doc_themes.items():
                        if theme not in merged_themes:
                            merged_themes[theme] = details
                        else:
                            for key, val in details.items():
                                merged_themes[theme].setdefault(key, []).extend(val)

                for theme, details in merged_themes.items():
                    if keyword.lower() in theme.lower():
                        themes.append({'theme': theme, 'details': details})

            log.info(f"Fetched {len(themes)} themes for keyword: {keyword}")
            return jsonify(themes)

        except Exception as e:
            log.error(f"Error in themes API: {e}")
            return jsonify({'error': 'Failed to fetch themes'}), 500


    @app.route('/api/themes/all', methods=['GET'])
    def api_all_themes():
        try:
            documents = handler.call('get_documents', limit=1000)
            themeCounts = {}

            for doc in documents:
                pipelines = handler.call('get_pipelines_by_publication', publication_id=doc.id)
                all_memories = []
                for pipe in pipelines:
                    all_memories.extend(handler.call('get_all_llm_memories', pipeline_id=pipe.id, model_name='qwen'))

                for mem in all_memories:
                    if 'themes' in mem:
                        for theme in mem['themes']:
                            themeCounts[theme] = themeCounts.get(theme, 0) + 1

            log.info(f"Fetched {len(themeCounts)} total themes")
            return jsonify(themeCounts)

        except Exception as e:
            log.error(f"Error fetching all themes: {e}")
            return jsonify({'error': 'Failed to fetch themes'}), 500