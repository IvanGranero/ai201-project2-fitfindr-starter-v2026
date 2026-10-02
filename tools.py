"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings
import re

# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:

    listings = load_listings()
    description_words = set(description.lower().split())

    filtered = []

    for listing in listings:

        # Price filter
        if max_price is not None and listing["price"] > max_price:
            continue

        # Size filter
        if size is not None:
            requested_size = size.lower()

            listing_sizes = re.split(r"[/,\s]+", listing["size"].lower())

            if requested_size not in listing_sizes:
                continue

        # Build searchable text
        searchable_text = " ".join(
            [
                str(listing.get("title", "")),
                str(listing.get("description", "")),
                str(listing.get("category", "")),
                " ".join(listing.get("style_tags", [])),
            ]
        ).lower()

        searchable_words = set(re.findall(r"\w+", searchable_text))

        score = len(description_words & searchable_words)

        if score > 0:
            filtered.append((score, listing))

    filtered.sort(key=lambda x: x[0], reverse=True)

    return [
        listing
        for score, listing in filtered[: config.SEARCH_RESULT_LIMIT]
    ]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:

    wardrobe_items = wardrobe.get("items", [])

    item_summary = f"""
    Title: {new_item.get('title')}
    Category: {new_item.get('category')}
    Colors: {', '.join(new_item.get('colors', []))}
    Style Tags: {', '.join(new_item.get('style_tags', []))}
    """

    if not wardrobe_items:

        prompt = f"""
        You are a fashion stylist.

        A user is considering this thrift find:

        {item_summary}

        The user has not provided any wardrobe items.

        Suggest one or two general styling ideas for wearing this item.
        Keep the response practical and concise.
        """

        return generate(prompt)

    wardrobe_text = "\n".join(
        f"- {item.get('name', str(item))}"
        if isinstance(item, dict)
        else f"- {item}"
        for item in wardrobe_items
    )

    prompt = f"""
    You are a fashion stylist.

    The user is considering this thrift item:

    {item_summary}

    Items already owned:

    {wardrobe_text}

    Create one or two outfit suggestions using pieces from the wardrobe.
    Reference the existing wardrobe items directly whenever possible.
    Keep the response concise.
    """

    return generate(prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:

    if not outfit or not outfit.strip():

        return (
            f"Found a {new_item.get('title', 'thrift item')} for "
            f"${new_item.get('price', 0):.2f} on "
            f"{new_item.get('platform', 'a resale platform')}, "
            "but no outfit suggestion was available."
        )

    prompt = f"""
    Write a social-media caption about this thrift find.

    Item:
    - Title: {new_item.get('title')}
    - Category: {new_item.get('category')}
    - Price: ${new_item.get('price')}
    - Platform: {new_item.get('platform')}
    - Style tags: {', '.join(new_item.get('style_tags', []))}

    Suggested outfit:
    {outfit}

    Requirements:
    - 2 to 4 sentences.
    - Mention the item once.
    - Mention the price once.
    - Mention the platform once.
    - Sound like a real thrift-fashion post.
    - Describe the vibe of the outfit.
    - Do not read like a product listing.
    """

    return generate(prompt)
