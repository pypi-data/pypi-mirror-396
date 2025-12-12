"""
Amazon AOD page helper updated to use RusticSoup-based extraction without external deps.
Networking is intentionally not included here; pass in the html_page dict with 'httpResponseBody'.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .product_ad import extract_aod_offers


@dataclass
class AmazonPage:
    asin: str
    domain: str

    def build_amazon_request_url(self) -> str:
        return f'https://www.{self.domain}/gp/product/ajax/ref=dp_aod_ALL_mbc?asin={self.asin}&m=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr=&pc=dp&experienceId=aodAjaxMain'

    def build_followup_request_url(self, ad_page: int) -> str:
        return f'https://www.{self.domain}/gp/product/ajax/ref=aod_page_{ad_page}?asin={self.asin}&m=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr=&pc=dp&isonlyrenderofferlist=true&pageno={ad_page}&experienceId=aodAjaxMain'

    def parse_from_html_page(self, html_page: Dict[str, Any]) -> Dict[str, Any]:
        """
        html_page: a dict that contains 'httpResponseBody' (Base64-encoded or plain HTML string/bytes).
        Returns the same structure as extract_aod_offers.
        """
        return extract_aod_offers(html_page, asin=self.asin, domain=self.domain)
