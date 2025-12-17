# -*- coding: utf-8 -*-
# Quasarr
# Project by https://github.com/rix1337

import re

import requests
from bs4 import BeautifulSoup

from quasarr.providers.log import info, debug
from urllib.parse import urlparse, urljoin


def get_n4_download_links(shared_state, url, mirror, title):
    n4 = shared_state.values["config"]("Hostnames").get("n4")
    headers = {
        'User-Agent': shared_state.values["user_agent"],
    }

    session = requests.Session()

    try:
        resp = session.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')
    except Exception as e:
        info(f"N4: could not fetch release page for {title}: {e}")
        return False

    # download links are provided as anchors with class 'dl-button'
    anchors = soup.select('a.btn-orange')
    candidates = []
    for a in anchors:
        
        href = a.get('href', '').strip()
        hoster = href.split('/')[3].lower()
        if not href.lower().startswith(('http://', 'https://')):
            href  = 'https://' + n4 + href

        try:
            href = requests.head(href, headers=headers, allow_redirects=True, timeout=20).url
        except Exception as e:
            info(f"N4: could not resolve download link for {title}: {e}")
            continue

        if hoster == 'ddl.to':
            hoster = 'ddownload'

        candidates.append([href, hoster])

    if not candidates:
        info(f"No external download links found on N4 page for {title}")

    return candidates
