# -*- coding: utf-8 -*-

# Autor: Yury
# Data: 05/10/2025

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from dotenv import load_dotenv

from logs import config as save
from interface import routes
from business.handle_db import HandlerDatabase

app = Flask(__name__, template_folder="../interface/templates", static_folder="../interface/static")
handler = HandlerDatabase()
log = save.setup_logs('flask_debug.txt')

routes.init_app(app, handler)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8617)