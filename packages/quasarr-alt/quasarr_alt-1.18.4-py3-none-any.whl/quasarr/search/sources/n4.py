# -*- coding: utf-8 -*-
# Quasarr
# Project by https://github.com/rix1337

import re
import time
from base64 import urlsafe_b64encode
from datetime import datetime
from html import unescape
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from quasarr.providers.imdb_metadata import get_localized_title
from quasarr.providers.log import info, debug

hostname = "n4"
supported_mirrors = ["rapidgator", "ddownload"]


def convert_to_rss_date(date_str: str) -> str:
    date_str = date_str.strip()
    for fmt in ("%d. %B %Y / %H:%M", "%d.%m.%Y / %H:%M", "%d.%m.%Y - %H:%M", "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        except Exception:
            continue
    return ""


def extract_size(text: str) -> dict:
    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*([A-Za-z]+)", text)
    if match:
        size = match.group(1).replace(',', '.')
        unit = match.group(2)
        return {"size": size, "sizeunit": unit}
    return {"size": "0", "sizeunit": "MB"}


def n4_search(shared_state, start_time, request_from, search_string, mirror=None, season=None, episode=None):
    releases = []
    host = shared_state.values["config"]("Hostnames").get(hostname)

    if not "arr" in request_from.lower():
        debug(f'Skipping {request_from} search on "{hostname.upper()}" (unsupported media type)!')
        return releases

    if mirror and mirror not in supported_mirrors:
        debug(f'Mirror "{mirror}" not supported by {hostname}.')
        return releases
    

    imdb_id = shared_state.is_imdb_id(search_string)
    if imdb_id:
        title = get_localized_title(shared_state, imdb_id, 'de')
        if not title:
            info(f"{hostname}: no title for IMDb {imdb_id}")
            return releases
        search_string = title
    else:
        return releases

    search_string = unescape(search_string)

    url = f'https://{host}/search'
    headers = {"User-Agent": shared_state.values["user_agent"]}
    data = {"search": search_string}

    try:
        r = requests.post(url, headers=headers, data=data, timeout=20)
        soup = BeautifulSoup(r.content, 'html.parser')
        results = soup.find_all('div', class_='article-right')
    except Exception as e:
        info(f"{hostname}: search load error: {e}")
        return releases


    if not results:
        return releases

    for result in results:
        try:
            imdb_a = result.select_one('a.imdb')
            if imdb_a and imdb_a.get('href'):
                try:
                    imdb_test = re.search(r'tt\d+', imdb_a['href']).group()
                    if imdb_test != imdb_id:
                        debug(f"{hostname}: IMDb ID mismatch: expected {imdb_id}, found {imdb_test}")
                        continue
                except Exception:
                    debug(f"{hostname}: could not extract IMDb ID from link")
                    continue

            a = result.find('a', class_='release-details', href=True)
            if not a:
                continue
            title = a.get_text(strip=True)
            
            sub_title = result.find('span', class_='subtitle')
            if sub_title:
                release_title = sub_title.get_text(strip=True)
            else:
                release_title = ""

            if shared_state.is_valid_release(release_title, request_from, search_string, season, episode):
                title = release_title
            else:
                combined_title = f"{title} [{release_title}]".strip()
                if shared_state.is_valid_release(combined_title, request_from, search_string, season, episode):
                    title = combined_title
                else:
                    if not shared_state.is_valid_release(title, request_from, search_string, season, episode):
                        imdb_title = get_localized_title(shared_state, imdb_id, 'en')
                        if shared_state.is_valid_release(imdb_title, request_from, search_string, season, episode):
                            title = imdb_title
                        else:
                            continue

            source = urljoin(f'https://{host}', a['href'])

            def get_release_field(res, label):
                for li in res.select('ul.release-infos li'):
                    sp = li.find('span')
                    if not sp:
                        continue
                    if sp.get_text(strip=True).lower() == label.lower():
                        txt = li.get_text(' ', strip=True)
                        return txt[len(sp.get_text(strip=True)):].strip()
                return ''

            size_text = get_release_field(result, 'Größe') or get_release_field(result, 'Size')
            size_item = extract_size(size_text) if size_text else {"size": "0", "sizeunit": "MB"}
            mb = shared_state.convert_to_mb(size_item)
            size = mb * 1024 * 1024

            password = ''
            mirrors_p = result.find('p', class_='mirrors')
            if mirrors_p:
                strong = mirrors_p.find('strong')
                if strong and strong.get_text(strip=True).lower().startswith('passwort'):
                    nxt = strong.next_sibling
                    if nxt:
                        val = str(nxt).strip()
                        if val:
                            password = val.split()[0]

            date_text = ''
            p_meta = result.find('p', class_='meta')
            if p_meta:
                spans = p_meta.find_all('span')
                if len(spans) >= 2:
                    date_part = spans[0].get_text(strip=True)
                    time_part = spans[1].get_text(strip=True).replace('Uhr', '').strip()
                    date_text = f"{date_part} / {time_part}"

            published = convert_to_rss_date(date_text) if date_text else ""

            payload = urlsafe_b64encode(f"{title}|{source}|{mirror}|{mb}|{password}|{imdb_id}".encode("utf-8")).decode()
            link = f"{shared_state.values['internal_address']}/download/?payload={payload}"
            
            releases.append({
                "details": {
                    "title": title,
                    "hostname": hostname,
                    "imdb_id": imdb_id,
                    "link": link,
                    "mirror": mirror,
                    "size": size,
                    "date": published,
                    "source": source
                },
                "type": "protected"
            })
        except Exception as e:
            debug(f"{hostname}: error parsing search result: {e}")
            continue

    elapsed = time.time() - start_time
    debug(f"Time taken: {elapsed:.2f}s ({hostname})")
    return releases
