# ItemPage with extract_all() - New Feature

## Overview

You can now use `ItemPage` classes directly with `WebPage.extract_all()` for the cleanest possible extraction pattern. Additionally, `Field` objects can be used in mapping dictionaries for per-field transforms.

## Features Added

1. **ItemPage with extract_all()**: Pass an ItemPage class to `extract_all()` to get a list of ItemPage instances
2. **Field objects in mappings**: Use Field objects (not just strings) in mapping dicts for per-field transforms
3. **Backward compatible**: All existing dict-based extraction still works

## Usage Pattern 1: ItemPage with extract_all()

### Before (dict-based with post-processing):

```python
from rusticsoup import WebPage

offers_mapping = {
    'seller_name': 'div.seller',
    'price': 'span.price',
    'link': 'a@href',
}

page = WebPage(html)
items = page.extract_all('.offer', offers_mapping)

# Manual transformation in list comprehension
offers = [
    {
        'seller_name': normalize(item['seller_name']),
        'price': parse_price(item['price']),
        'link': normalize_link(item['link']),
    }
    for item in items
]
```

### After (ItemPage with transforms):

```python
from rusticsoup import WebPage, Field, ItemPage

class Offer(ItemPage):
    seller_name = Field(css='div.seller', transform=normalize)
    price = Field(css='span.price', transform=parse_price)
    link = Field(css='a', attr='href', transform=normalize_link)

page = WebPage(html)
offers = page.extract_all('.offer', Offer)  # Returns list of Offer instances

# All transforms already applied!
for offer in offers:
    print(offer.seller_name, offer.price, offer.link)
```

## Usage Pattern 2: Field objects in mapping dict

### Before (string selectors only):

```python
offers_field = Field(
    container='.offer',
    mapping={
        'title': 'h3',
        'price': '.price',
    }
)

offers = offers_field.extract(page)
# Manual transformation needed
offers = [
    {**offer, 'title': offer['title'].upper(), 'price': parse_price(offer['price'])}
    for offer in offers
]
```

### After (Field objects with transforms):

```python
offers_field = Field(
    container='.offer',
    mapping={
        'title': Field(css='h3', transform=str.upper),
        'price': Field(css='.price', transform=parse_price),
    }
)

offers = offers_field.extract(page)  # Transforms already applied!
```

## Complete Example

See `examples/google_shopping_itempage.py` for a complete real-world example showing:

- ItemPage class with multiple field types
- Per-field transforms
- Fallback selectors
- Attribute extraction
- Complex parsing logic

```python
from rusticsoup import WebPage, Field, ItemPage

class GoogleOffer(ItemPage):
    seller_name = Field(css='div.seller-name', transform=normalize)
    product_title = Field(css='div.product-title', transform=normalize)

    # Fallback selectors
    availability = Field(css=['span.in-stock', 'span.availability'], transform=normalize)

    # Complex transforms
    offer_price = Field(
        css=['span.price-new', 'span.price'],
        transform=lambda s: float((s or '').replace('$', '').replace(',', '') or '0')
    )

    # Attributes
    seller_id = Field(css='div.offer-container', attr='data-merchantid', transform=normalize)
    link = Field(css='a', attr='href', transform=normalize_link)

# One line to extract everything!
page = WebPage(html)
offers = page.extract_all('div[role="listitem"]', GoogleOffer)
```

## Benefits

1. **Clean, declarative code**: Field definitions are self-documenting
2. **Reusable data models**: Define once, use everywhere
3. **Per-field transforms**: No more list comprehensions for post-processing
4. **Type-safe access**: `offer.price` instead of `offer['price']`
5. **Fallback selectors**: Built-in robustness
6. **Better separation of concerns**: Extraction logic lives with the data model

## Implementation Details

### WebPage.extract_all()

Now accepts either:
- `dict` mapping (original behavior)
- `ItemPage` class (new behavior)

When an ItemPage class is passed:
1. Extracts all container elements
2. Creates a WebPage from each container's HTML
3. Instantiates the ItemPage class with that WebPage
4. Returns list of ItemPage instances

### Field with container+mapping

Now accepts either:
- String selectors (original behavior)
- Field objects (new behavior)

When Field objects are in the mapping:
1. Creates a WebPage from each container's HTML
2. Calls `field.extract()` on that WebPage
3. Transforms are applied automatically

## Tests

Run `uv run python tests/test_itempage_extract_all.py` to see all tests passing:

- ✓ extract_all with ItemPage
- ✓ extract_all with ItemPage transforms
- ✓ extract_all with ItemPage fallback selectors
- ✓ Field mapping with Field objects
- ✓ Backward compatibility with dict mappings

## Migration Guide

No migration needed! All existing code continues to work. The new patterns are opt-in enhancements.

### Gradually adopt the new pattern:

1. Start with your most complex extraction logic
2. Define an ItemPage class with Field descriptors
3. Replace `extract_all(container, dict)` with `extract_all(container, ItemPageClass)`
4. Remove post-processing list comprehensions

You can mix old and new patterns in the same codebase.
