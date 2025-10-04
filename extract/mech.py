# -*- coding:utf-8 -*-

# Autor: Yury
# Data: 04/10/2025

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapy import ScrapyDocs

def init_scrapy():
    """Function of the mechanism that interprets and triggers the scrapy

    Returns:
        status (str): in case no error is raised
    """
    # INITIALIZE SEARCH CLASS
    extraction = ScrapyDocs()

    links = extraction.setup_search()
    status = extraction.get_docs_html(search=links)


if __name__ == "__main__":
    teste = init_scrapy()
    print(f"FINALLY: {teste}")