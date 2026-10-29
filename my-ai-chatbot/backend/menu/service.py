import json
import os


# Get the path of dunkin_menu.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MENU_FILE = os.path.join(BASE_DIR, "dunkin_menu.json")


# Load menu data
with open(MENU_FILE, "r", encoding="utf-8") as f:
    MENU = json.load(f)


# User-friendly names → actual database categories
CATEGORY_MAP = {
    "beverages": "Hot Beverages",
    "beverage": "Hot Beverages",
    "drinks": "Hot Beverages",
    "drink": "Hot Beverages",

    "donuts": "Donuts and Munchkins",
    "donut": "Donuts and Munchkins",
    "munchkins": "Donuts and Munchkins",

    "bakery": "Bakery",

    "boxes": "Boxes",
    "box": "Boxes",

    "coffee": "Coffee Bags and Tea",
    "tea": "Coffee Bags and Tea",

    "offers": "Dunkin Offers   Discounts",
    "discounts": "Dunkin Offers   Discounts",

    "tumblers": "Tumblers",
    "tumbler": "Tumblers",

    "other": "Other Products"
}


def get_category_items(category_name: str):
    """
    Return all products belonging to a category.
    """

    category_name = category_name.lower().strip()

    actual_category = CATEGORY_MAP.get(category_name)

    if not actual_category:
        return []

    return [
        item
        for item in MENU
        if item.get("category") == actual_category
    ]


def search_menu(query: str):
    """
    Search menu products by product name or description.

    Example:
        "chocolate"
        "choco"
        "mango"
        "croissant"
    """

    query = query.lower().strip()

    if not query:
        return []

    results = []

    for item in MENU:
        name = item.get("name", "").lower()
        description = item.get("description", "").lower()

        if query in name or query in description:
            results.append(item)

    return results


def get_donuts():
    """
    Return all donut and munchkin products.
    """

    return [
        item
        for item in MENU
        if item.get("category") == "Donuts and Munchkins"
    ]


def get_items_under_price(max_price: float):
    """
    Return all products whose price is less than or equal
    to the requested maximum price.
    """

    return [
        item
        for item in MENU
        if isinstance(item.get("price"), (int, float))
        and item.get("price") <= max_price
    ]