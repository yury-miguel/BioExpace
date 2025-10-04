# -*- coding:utf-8 -*-

# Autor: Yury
# Data: 04/10/2025

import logging

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

url = "https://www.nature.com/articles/s41526-024-00419-y"
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")
article_body = soup.find(class_="c-article-body")
if article_body:
    parte_abs = article_body.find(id="Abs1-section")
    parte_main = article_body.find(class_="main-content")

    text_abs = parte_abs.get_text(separator="\n", strip=True) if parte_abs else ""
    text_main = parte_main.get_text(separator="\n", strip=True) if parte_main else ""

    text_finally = f"{text_abs}\n\n{text_main}"
    text_finally.replace("\xa0", " ")
    
    with open("extract/test/doc_extrac.txt", "w", encoding="utf-8") as doc:
        doc.write(text_finally)

    logging.info("✅ Text extracted with success!")
else:
    logging.error("❌ Not found class 'c-article-body'")