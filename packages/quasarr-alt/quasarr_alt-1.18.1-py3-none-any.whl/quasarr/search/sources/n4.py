# -*- coding: utf-8 -*-
# Quasarr
# Source for n4 (renamed from nima4k)

import re
import time
from base64 import urlsafe_b64encode
from datetime import datetime

from bs4 import BeautifulSoup
import requests

from quasarr.providers.log import info, debug

hostname = "n4"
supported_mirrors = ["rapidgator", "ddownload"]


def convert_to_rss_date(date_str: str) -> str:
    # Try to parse common formats like "13. Dezember 2025 / 12:34" or "13.12.2025 - 12:34"
    date_str = date_str.strip()
    for fmt in ("%d. %B %Y / %H:%M", "%d.%m.%Y - %H:%M", "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        except Exception:
            continue
    # fallback: return empty string
    return ""


def extract_size(text: str) -> dict:
    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*([A-Za-z]+)", text)
    if match:
        size = match.group(1).replace(',', '.')
        unit = match.group(2)
        return {"size": size, "sizeunit": unit}
    # fallback
    return {"size": "0", "sizeunit": "MB"}


def n4_feed(shared_state, start_time, request_from, mirror=None):
    releases = []
    host = shared_state.values["config"]("Hostnames").get(hostname)

    if not "arr" in request_from.lower():
        debug(f'Skipping {request_from} search on "{hostname.upper()}" (unsupported media type)!')
        return releases

    if mirror and mirror not in supported_mirrors:
        debug(f'Mirror "{mirror}" not supported by {hostname}.')
        return releases

    url = f'https://{host}/rss.xml'
    headers = {"User-Agent": shared_state.values["user_agent"]}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        info(f"{hostname}: could not fetch feed: {e}")
        return releases

    soup = BeautifulSoup(r.content, 'html.parser')

    # assume feed items are in article tags or h2/h3 headings
    items = soup.find_all(['article', 'h2', 'h3'])
    for it in items:
        try:
            a = it.find('a', href=True)
            if not a:
                continue
            title = a.get_text(strip=True)
            source = a['href']

            # size and date heuristics
            size_text = ''
            date_text = ''
            maybe_span = it.find('span')
            if maybe_span:
                txt = maybe_span.get_text(" ", strip=True)
                # look for sizes like "1.23 GB" or dates
                if re.search(r"\d+\s*[GMK]B", txt, re.IGNORECASE):
                    size_text = txt
                else:
                    date_text = txt

            size_item = extract_size(size_text) if size_text else {"size": "0", "sizeunit": "MB"}
            mb = shared_state.convert_to_mb(size_item)
            size = mb * 1024 * 1024

            published = convert_to_rss_date(date_text) if date_text else ""

            imdb_id = None
            try:
                imdb_id = re.search(r'tt\d+', str(it)).group()
            except Exception:
                imdb_id = None

            payload = urlsafe_b64encode(f"{title}|{source}|{mirror}|{mb}|".encode('utf-8')).decode('utf-8')
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
            debug(f"{hostname}: error parsing feed item: {e}")
            continue

    elapsed = time.time() - start_time
    debug(f"Time taken: {elapsed:.2f}s ({hostname})")
    return releases


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

    url = f'https://{host}/search'
    headers = {"User-Agent": shared_state.values["user_agent"]}
    data = {"search": search_string}

    try:
        r = requests.post(url, headers=headers, data=data, timeout=10)
        r.raise_for_status()
    except Exception as e:
        info(f"{hostname}: search load error: {e}")
        return releases

    soup = BeautifulSoup(r.content, 'html.parser')
    results = soup.find_all(['article', 'h2', 'h3'])

    for result in results:
        try:
            a = result.find('a', href=True)
            if not a:
                continue
            title = a.get_text(strip=True)

            if not shared_state.is_valid_release(title, request_from, search_string, season, episode):
                continue

            source = a['href']

            size_text = ''
            maybe_span = result.find('span')
            if maybe_span:
                size_text = maybe_span.get_text(strip=True)

            size_item = extract_size(size_text) if size_text else {"size": "0", "sizeunit": "MB"}
            mb = shared_state.convert_to_mb(size_item)
            size = mb * 1024 * 1024

            date_text = ''
            try:
                date_text = result.parent.find('span', class_='date updated').get_text(strip=True)
            except Exception:
                date_text = ''

            published = convert_to_rss_date(date_text) if date_text else ""

            try:
                imdb = re.search(r'tt\d+', str(result)).group()
            except Exception:
                imdb = imdb_id

            payload = urlsafe_b64encode(f"{title}|{source}|{mirror}|{mb}|".encode('utf-8')).decode('utf-8')
            link = f"{shared_state.values['internal_address']}/download/?payload={payload}"

            releases.append({
                "details": {
                    "title": title,
                    "hostname": hostname,
                    "imdb_id": imdb,
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
