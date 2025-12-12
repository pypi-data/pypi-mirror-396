"""
Example: Google Shopping-like extraction using ItemPage pattern

This demonstrates the cleanest approach to extracting structured data
using ItemPage classes with per-field transforms.
"""

from rusticsoup import WebPage, Field, ItemPage


# Define your data model as an ItemPage class
class GoogleOffer(ItemPage):
    """Represents a single offer from Google Shopping"""

    # Text fields with normalization
    seller_name = Field(
        css='div.seller-name',
        transform=lambda s: (s or '').strip() or 'N/A'
    )

    product_title = Field(
        css='div.product-title',
        transform=lambda s: (s or '').strip() or 'N/A'
    )

    discount = Field(
        css='div.discount',
        transform=lambda s: (s or '').strip() or 'N/A',
        default='N/A'
    )

    coupon = Field(
        css='span.coupon',
        transform=lambda s: (s or '').strip() or 'N/A',
        default='N/A'
    )

    rating = Field(
        css='span.rating',
        transform=lambda s: (s or '').strip() or 'N/A',
        default='N/A'
    )

    # Availability with fallback selectors
    availability = Field(
        css=['span.in-stock', 'span.availability'],
        transform=lambda s: (s or '').strip() or 'N/A',
        default='N/A'
    )

    # Price with parsing and conversion
    offer_price = Field(
        css=['span.price-new', 'span.price'],
        transform=lambda s: float((s or '').strip().replace('$', '').replace(',', '') or '0')
    )

    old_price = Field(
        css='div.old-price span',
        transform=lambda s: (s or '').strip() or 'N/A',
        default='N/A'
    )

    # Data attributes
    gpcid = Field(
        css='div.offer-container',
        attr='data-gpcid',
        transform=lambda s: (s or '').strip() or 'N/A'
    )

    seller_id = Field(
        css='div.offer-container',
        attr='data-merchantid',
        transform=lambda s: (s or '').strip() or 'N/A'
    )

    oid = Field(
        css='div.offer-container',
        attr='data-oid',
        transform=lambda s: (s or '').strip() or 'N/A'
    )

    # Links with special handling
    link = Field(
        css='a.offer-link',
        attr='href',
        transform=lambda href: f"https://www.google.com{href}" if href and href.startswith('/url?q=') else (href or 'N/A')
    )


def extract_google_shopping_offers(html: str, page_url: str):
    """
    Extract Google Shopping offers from HTML using ItemPage pattern.

    This is the cleanest approach - all transformation logic is in the Field definitions.
    """
    page = WebPage(html)

    # Extract all offers - returns list of GoogleOffer instances
    offers = page.extract_all(
        'div[data-attrid="organic_offers_grid"] div[role="listitem"]',
        GoogleOffer
    )

    # Convert to dict format if needed
    return [
        {
            'domain': 'google.com',
            'seller_name': offer.seller_name,
            'title': offer.product_title,
            'discount': offer.discount,
            'coupon': offer.coupon,
            'rating': offer.rating,
            'availability': offer.availability,
            'offer_price': offer.offer_price,
            'gpcid': offer.gpcid,
            'seller_id': offer.seller_id,
            'oid': offer.oid,
            'link': offer.link,
            'page_url': page_url,
        }
        for offer in offers
    ]


def example_with_field_mapping():
    """
    Alternative: Use Field objects in a mapping dict for per-field transforms.
    """
    html = """
    <html>
        <body>
            <div class="offer">
                <h3 class="title">Special Deal</h3>
                <span class="price">$19.99</span>
                <span class="discount">20% off</span>
            </div>
            <div class="offer">
                <h3 class="title">Hot Sale</h3>
                <span class="price">$29.99</span>
                <span class="discount">15% off</span>
            </div>
        </body>
    </html>
    """

    def parse_price(s):
        return float(s.replace("$", ""))

    # Use Field objects in mapping for per-field transforms
    offers_field = Field(
        container=".offer",
        mapping={
            "title": Field(css=".title", transform=str.upper),
            "price": Field(css=".price", transform=parse_price),
            "discount": Field(css=".discount"),
        },
    )

    page = WebPage(html)
    offers = offers_field.extract(page)

    print("Offers with Field mapping:")
    for i, offer in enumerate(offers, 1):
        print(f"  {i}. {offer['title']}: ${offer['price']} ({offer['discount']})")


if __name__ == "__main__":
    # Example HTML (simplified Google Shopping structure)
    html = """
    <html>
        <body>
            <div data-attrid="organic_offers_grid">
                <div role="listitem">
                    <div class="offer-container" data-gpcid="123" data-merchantid="M1" data-oid="O1">
                        <div class="seller-name">Best Store</div>
                        <div class="product-title">Awesome Product</div>
                        <span class="price-new">$99.99</span>
                        <div class="old-price"><span>$129.99</span></div>
                        <div class="discount">23% off</div>
                        <span class="coupon">Save $5</span>
                        <span class="rating">4.5 stars</span>
                        <span class="in-stock">In Stock</span>
                        <a class="offer-link" href="/url?q=https://store.com/product">View Offer</a>
                    </div>
                </div>
                <div role="listitem">
                    <div class="offer-container" data-gpcid="456" data-merchantid="M2" data-oid="O2">
                        <div class="seller-name">Great Shop</div>
                        <div class="product-title">Amazing Item</div>
                        <span class="price">$79.99</span>
                        <div class="discount">15% off</div>
                        <span class="rating">4.8 stars</span>
                        <span class="availability">Available</span>
                        <a class="offer-link" href="/url?q=https://shop.com/item">View Offer</a>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

    print("=" * 60)
    print("Google Shopping Extraction with ItemPage Pattern")
    print("=" * 60)

    offers = extract_google_shopping_offers(html, "https://www.google.com/shopping")

    for i, offer in enumerate(offers, 1):
        print(f"\nOffer {i}:")
        print(f"  Seller: {offer['seller_name']}")
        print(f"  Title: {offer['title']}")
        print(f"  Price: ${offer['offer_price']}")
        print(f"  Discount: {offer['discount']}")
        print(f"  Rating: {offer['rating']}")
        print(f"  Availability: {offer['availability']}")
        print(f"  Link: {offer['link']}")

    print("\n" + "=" * 60)
    example_with_field_mapping()
    print("=" * 60)

    print("\n✓ All extractions successful!")
    print("\nKey benefits of ItemPage pattern:")
    print("  • Clean, declarative field definitions")
    print("  • Per-field transforms applied automatically")
    print("  • Fallback selectors for robustness")
    print("  • Reusable data models")
    print("  • Type-safe access to extracted data")
