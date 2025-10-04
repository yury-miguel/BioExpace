# -*- coding: utf-8 -*-

# Author: Yury
# Data: 04/10/2025

import os
import sys
import time
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from typing import Dict, Union

import re
import requests
import pandas as pd
from bs4 import BeautifulSoup, Tag

from business import handle_db
from logs import config as save
log = save.setup_logs("scrapy_debug.txt")


class ScrapyErrors(Exception):
    """Catches exceptions when extracting data from HTML"""
    pass


class ScrapyDocs():
    DOCS_FONT = "publications/SB_publication_PMC.csv"
    DOCS_SAVE_DATA = "extract/docs"
    

    def __init__(self):
        """Show the directory of the CSV that contains the publications
        the CSV contains the title and the link and where to save the extractions
        """
        self.font = self.DOCS_FONT
        self.dir_save = self.DOCS_SAVE_DATA
        self.handle = handle_db.HandlerDatabase() 
    
    def setup_search(self) -> Dict | ScrapyErrors:
        """Retrieve each search link contained in the CSV"""
        try:
            df = pd.read_csv(self.font, sep=",")
            log.info("CSV read and explored!")
            return df.set_index("Title")["Link"].to_dict()
        except Exception as errors:
            message = f"errors in search links csv: {errors}"
            log.error(message)
            raise ScrapyErrors(message) from errors

    def get_docs_html(self, search: Dict) -> Union[str, ScrapyErrors]:
        """Responsible for going to each link, 
        capturing the document that is in HTML, 
        then separating it and saving it in the /docs directory
        
        Args:
            search (Union[setup_search, Dict]): dictionary with document title and search link

        Raises:
            exception (ScrapyErrors): caught exception in extract data docs
        
        Returns:
            status (str): success if all links were extracted and saved
        """
        try:
            for title, link in search.items():
                url = link
                title_doc = title + ".txt"
                
                try:
                    headers = {
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/125.0.0.0 Safari/537.36"
                        ),
                        "Accept-Language": "en-US,en;q=0.9",
                        "Referer": "https://www.google.com/",
                    }
                    response = requests.get(url, headers=headers, timeout=30)
                    response.raise_for_status()

                    raw_html = response.text
                    soup = BeautifulSoup(response.text, "lxml")
                    exclude_patterns = [
                        "notes", "ack1", "ref", "contrib",
                        "fn", "Bib", "sec", "__ad", "founding"
                    ]

                    section = soup.find("section", attrs={"aria-label": "Article content"})
                    if not section:
                        raise Exception("Section 'Article content' not found.")


                    for tag in list(section.find_all(True)):
                        try:
                            if not isinstance(tag, Tag):
                                continue

                            id_attr = tag.get("id", "") or ""
                            class_attr = " ".join(tag.get("class", [])) if tag.get("class") else ""

                            if any(
                                pat.lower() in id_attr.lower() or pat.lower() in class_attr.lower()
                                for pat in exclude_patterns
                            ):
                                tag.decompose()
                        except Exception as e:
                            log.warning(f"⚠️ Ignored invalid tag: {e}")
                            continue

                    footer = section.find("footer")
                    if footer:
                        footer.decompose()
                    

                    text_extracted = self.clean_text(section.get_text(separator="\n", strip=True))
                    self.handle.call(
                        "insert_publication",
                        title=title,
                        url=url,
                        raw_html=raw_html,
                        text_extratect=text_extracted
                    )

                    log.info(f"✅ Text {title_doc} for {url} extracted with success!")
                    time.sleep(random.uniform(2, 5))

                except Exception as errors:
                    message = f"Error visiting site -> {url} and capturing data: {errors}"
                    log.error(message)
                    raise ScrapyErrors(message) from errors
            
            return "success"

        except Exception as errors:
            message = f"Error in the search run: {errors}"
            log.error(message)
            raise ScrapyErrors(message) from errors
    
    def clean_text(self, data: str) -> str:
        """Remove spaces and invisible characters

        Args:
            data (str): str containing texte doc extracted from html
        
        Returns:
            treated (str): text doc clean
        """
        text = re.sub(r"\s+", " ", data)
        treated = text.replace("\xa0", " ")
        return treated.strip()