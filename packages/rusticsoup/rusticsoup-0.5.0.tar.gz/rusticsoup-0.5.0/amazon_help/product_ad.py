"""
Amazon AOD (All Offers Display) parsing helpers using RusticSoup.
Self-contained: no scrapy, no external project dependencies.
"""
from __future__ import annotations

import re
import urllib.parse as _url
from base64 import b64decode
from typing import Any, Dict, List, Optional
import json
import html

import rusticsoup


def _decode_html_fragment(httpResponseBody: Any) -> str:
    if httpResponseBody is None:
        return ''
    if isinstance(httpResponseBody, (bytes, bytearray)):
        raw = bytes(httpResponseBody)
    else:
        raw = str(httpResponseBody).encode('utf-8', errors='ignore')
    try:
        return b64decode(raw).decode('utf-8', errors='ignore')
    except Exception:
        # Already plain HTML
        return raw.decode('utf-8', errors='ignore')


def parse_price(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    m = re.search(r"([\$£€])?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})|[0-9]+(?:\.[0-9]{2})?)", text)
    if not m:
        return None
    cur, num = m.group(1) or '', m.group(2)
    return f"{cur}{num}" if cur else num


def _seller_id_from_href(href: Optional[str]) -> Optional[str]:
    if not href:
        return None
    try:
        q = _url.parse_qs(_url.urlparse(href).query)
        return (q.get('seller') or [None])[0]
    except Exception:
        return None


def _parse_atc_payload(attr_value: Optional[str]) -> Dict[str, Any]:
    """Parse Amazon's data-aod-atc-action JSON which may be HTML-escaped.
    Returns an empty dict on failure.
    """
    if not attr_value:
        return {}
    try:
        # Unescape HTML entities first (e.g., &quot;)
        unescaped = html.unescape(attr_value)
        return json.loads(unescaped)
    except Exception:
        try:
            # Some pages might already be raw JSON
            return json.loads(attr_value)
        except Exception:
            return {}


def extract_aod_offers(html_page: Dict[str, Any], asin: str, domain: str) -> Dict[str, Any]:
    """
    Returns a dict:
    {
      'title': str|None,
      'ad_count': str|None,
      'pinned': {...} or None,
      'offers': [ {...}, ... ]
    }
    """
    html = _decode_html_fragment(html_page.get('httpResponseBody'))

    top_fields = rusticsoup.extract_data(
        html,
        'body',
        {
            'title': '#aod-asin-title-text',
            'ad_count': '#aod-filter-offer-count-string',
        },
    )
    top = top_fields[0] if top_fields else {}

    # Pinned
    pinned_list = rusticsoup.extract_data(
        html,
        '#aod-pinned-offer',
        {
            'price_text': '[id^="aod-price-"] .aok-offscreen',
            'condition': '#aod-offer-heading .a-text-bold',
            'seller_name_link': '#aod-pinned-offer-additional-content #aod-offer-soldBy a@href',
            'seller_name_text': '#aod-pinned-offer-additional-content #aod-offer-soldBy a',
            'seller_name_fallback': '#aod-pinned-offer-additional-content #aod-offer-soldBy .a-size-small.a-color-base',
            'ships_from': '#aod-pinned-offer-additional-content #aod-offer-shipsFrom .a-size-small.a-color-base',
            'qty_options': '[id^="aod-sticky-pinned-offer-qty-option-"]@text@get_all',
            'atc_payload': '[data-action="aod-atc-action"]@data-aod-atc-action',
        },
    )

    pinned = None
    if pinned_list:
        p = pinned_list[0]
        seller_href = p.get('seller_name_link')
        seller_id = _seller_id_from_href(seller_href) or 'ATVPDKIKX0DER'
        seller_name = (p.get('seller_name_text') or p.get('seller_name_fallback') or '').strip() or domain.replace('www.', '')

        # Compute max_quantity for pinned from qty options and ATC JSON payload
        pinned_qty_opts = p.get('qty_options') or []
        pinned_numeric_q = []
        for q in pinned_qty_opts:
            q = (q or '').strip()
            if q.isdigit():
                pinned_numeric_q.append(int(q))
        # Parse maxQty from the add-to-cart JSON, if present
        pinned_atc = _parse_atc_payload(p.get('atc_payload'))
        pinned_max_qty_json = None
        try:
            if isinstance(pinned_atc, dict) and 'maxQty' in pinned_atc:
                pinned_max_qty_json = int(pinned_atc.get('maxQty'))
        except Exception:
            pinned_max_qty_json = None
        pinned_max_quantity = max(pinned_numeric_q) if pinned_numeric_q else None
        if pinned_max_qty_json is not None:
            pinned_max_quantity = max(pinned_max_quantity or 0, pinned_max_qty_json)
        if pinned_max_quantity is None or pinned_max_quantity <= 0:
            pinned_max_quantity = 1

        pinned = {
            'asin': asin,
            'domain': domain,
            'buybox_winner': True,
            'price': parse_price(p.get('price_text')),
            'condition': (p.get('condition') or '').replace('\n', '').replace('  ', ' ').strip() or None,
            'seller_name': seller_name,
            'seller_id': seller_id,
            'seller_info_url': f"https://{domain.replace('www.', '')}{seller_href}" if seller_href else f"https://{domain.replace('www.', '')}",
            'ships_from': (p.get('ships_from') or '').strip() or None,
            'max_quantity': pinned_max_quantity,
            'url': f"https://{domain}/dp/{asin}{f'?smid={seller_id}&th=1' if seller_id else ''}",
        }

    # Non-pinned cards
    offer_cards = rusticsoup.extract_data(
        html,
        '#aod-offer',
        {
            'price_text': '[id^="aod-price-"] .aok-offscreen',
            'condition': '#aod-offer-heading .a-text-bold',
            'qty_options': '[id^="aod-offer-qty-option-"]@text@get_all',
                        'atc_payload': '[data-action="aod-atc-action"]@data-aod-atc-action',
        },
    )

    seller_blocks = rusticsoup.extract_data(
        html,
        '#aod-offer-soldBy',
        {
            'seller_link': 'a@href',
            'seller_name': 'a',
            'seller_name_fallback': '.a-size-small.a-color-base',
            'ratings_texts': '#aod-offer-seller-rating span span@get_all',
        },
    )

    shipper_blocks = rusticsoup.extract_data(
        html,
        '#aod-offer-shipsFrom',
        {
            'ships_from': '.a-size-small.a-color-base',
        },
    )

    offers: List[Dict[str, Any]] = []
    for idx, card in enumerate(offer_cards):
        seller = seller_blocks[idx] if idx < len(seller_blocks) else {}
        shipper = shipper_blocks[idx] if idx < len(shipper_blocks) else {}

        seller_href = seller.get('seller_link')
        seller_id = _seller_id_from_href(seller_href) or 'ATVPDKIKX0DER'
        seller_name = (seller.get('seller_name') or seller.get('seller_name_fallback') or '').strip() or domain.replace('www.', '')

        ratings_texts = seller.get('ratings_texts') or []
        ratings_count = None
        ratings_pct = None
        for t in ratings_texts:
            if not isinstance(t, str):
                continue
            if ratings_count is None:
                m = re.search(r"\((\d+) ratings\)", t)
                if m:
                    ratings_count = m.group(1)
            if ratings_pct is None:
                m = re.search(r"(\d{1,3})% positive", t)
                if m:
                    ratings_pct = m.group(1)

        qty_opts = card.get('qty_options') or []
        numeric_q = []
        for q in qty_opts:
            q = (q or '').strip()
            if q.isdigit():
                numeric_q.append(int(q))
        # Parse maxQty from data-aod-atc-action JSON on the offer
        atc = _parse_atc_payload(card.get('atc_payload'))
        max_qty_json = None
        try:
            if isinstance(atc, dict) and 'maxQty' in atc:
                max_qty_json = int(atc.get('maxQty'))
        except Exception:
            max_qty_json = None
        max_quantity = max(numeric_q) if numeric_q else None
        if max_qty_json is not None:
            max_quantity = max(max_quantity or 0, max_qty_json)
        if max_quantity is None or max_quantity <= 0:
            max_quantity = 1

        offers.append({
            'asin': asin,
            'domain': domain,
            'buybox_winner': False,
            'price': parse_price(card.get('price_text')),
            'condition': (card.get('condition') or '').replace('\n', '').replace('  ', ' ').strip() or None,
            'seller_name': seller_name,
            'seller_id': seller_id,
            'seller_info_url': f"https://{domain.replace('www.', '')}{seller_href}" if seller_href else f"https://{domain.replace('www.', '')}",
            'ships_from': (shipper.get('ships_from') or '').strip() or None,
            'ratings': ratings_count or 'None',
            'ratings_percentage': ratings_pct or 'None',
            'max_quantity': max_quantity,
            'url': f"https://{domain}/dp/{asin}{f'?smid={seller_id}&th=1' if seller_id else ''}",
        })

    return {
        'title': (top.get('title') or '').strip() or None,
        'ad_count': (top.get('ad_count') or '').strip() or None,
        'pinned': pinned,
        'offers': offers,
    }

