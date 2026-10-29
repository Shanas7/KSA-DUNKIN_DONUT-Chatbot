import json
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


BASE_URL = "https://www.dunkinksa.com"
HOME_URL = f"{BASE_URL}/home"
OUTPUT_FILE = "dunkin_menu.json"


def clean_text(text):
    if not text:
        return ""

    return " ".join(text.split())


def extract_price(page):
    """
    Extract the product price from the KSA product page.
    """

    # Main price element
    price_element = page.locator("#itemPrice")

    if price_element.count() > 0:

        price_text = clean_text(
            price_element.first.inner_text()
        )

        price_text = (
            price_text
            .replace("SAR", "")
            .strip()
        )

        try:
            return float(price_text)
        except ValueError:
            pass

    # Backup price element
    price_element = page.locator("#itemPrice3")

    if price_element.count() > 0:

        price_text = clean_text(
            price_element.first.inner_text()
        )

        price_text = (
            price_text
            .replace("SAR", "")
            .strip()
        )

        try:
            return float(price_text)
        except ValueError:
            pass

    return None


def extract_category(url):
    """
    Example:

    /details/Hot-Beverages/1/Bold-Breakfast-Black-Tea/36

    Category = Hot Beverages
    """

    parts = url.split("/")

    if len(parts) > 4:

        category = parts[4]

        return category.replace(
            "-",
            " "
        )

    return ""


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page(
        viewport={
            "width": 1440,
            "height": 900
        }
    )

    print("========================================")
    print("DUNKIN KSA MENU SCRAPER")
    print("========================================")

    # ========================================
    # 1. OPEN HOMEPAGE
    # ========================================

    print("\nOpening Dunkin KSA...")

    page.goto(
        HOME_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(8000)

    print("Homepage loaded.")

    # ========================================
    # 2. FIND PRODUCT CARDS
    # ========================================

    cards = page.locator(".item-box")

    card_count = cards.count()

    print(
        f"\nProduct cards found: {card_count}"
    )

    products = []

    # ========================================
    # 3. GET PRODUCT NAME + VIEW ITEM URL
    # ========================================

    for index in range(card_count):

        try:

            card = cards.nth(index)

            # --------------------------------
            # Product name
            # --------------------------------

            card_text = clean_text(
                card.inner_text()
            )

            name = card_text.replace(
                "VIEW ITEM",
                ""
            ).strip()

            # --------------------------------
            # IMPORTANT:
            # Find the actual View Item link
            # --------------------------------

            view_link = card.locator(
                "a"
            ).filter(
                has_text="VIEW ITEM"
            ).first

            if view_link.count() == 0:
                continue

            href = view_link.get_attribute(
                "href"
            )

            if not href:
                continue

            product_url = urljoin(
                BASE_URL,
                href
            )

            if not name:
                continue

            products.append(
                {
                    "name": name,
                    "url": product_url
                }
            )

        except Exception as error:

            print(
                f"Could not process card "
                f"{index + 1}: {error}"
            )

    # ========================================
    # REMOVE DUPLICATES
    # ========================================

    unique_products = {}

    for product in products:

        unique_products[
            product["url"]
        ] = product

    products = list(
        unique_products.values()
    )

    print(
        f"Unique products found: "
        f"{len(products)}"
    )

    # ========================================
    # 4. OPEN EACH PRODUCT
    # ========================================

    menu = []

    for index, product in enumerate(products):

        print("\n----------------------------------------")
        print(
            f"PRODUCT {index + 1}/"
            f"{len(products)}"
        )
        print("----------------------------------------")

        print(
            "Name:",
            product["name"]
        )

        print(
            "URL:",
            product["url"]
        )

        try:

            page.goto(
                product["url"],
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(1500)

            # --------------------------------
            # Price
            # --------------------------------

            price = extract_price(page)

            # --------------------------------
            # Category
            # --------------------------------

            category = extract_category(
                product["url"]
            )

            # --------------------------------
            # Customisation
            # --------------------------------

            customisable = (
                "/options/"
                in product["url"]
            )

            # --------------------------------
            # Description
            #
            # Leave empty unless we find a
            # verified product description.
            # We do NOT want footer text.
            # --------------------------------

            description = ""

            # --------------------------------
            # Save record
            # --------------------------------

            item = {
                "name": product["name"],
                "price": price,
                "currency": "SAR",
                "category": category,
                "description": description,
                "customisable": customisable,
                "bestseller": False,
                "source": product["url"]
            }

            menu.append(item)

            # --------------------------------
            # Print result
            # --------------------------------

            if price is not None:

                print(
                    f"Price: SAR {price:.2f}"
                )

            else:

                print(
                    "Price: NOT FOUND"
                )

            print(
                "Category:",
                category
            )

            print(
                "Customisable:",
                customisable
            )

        except Exception as error:

            print(
                "ERROR:",
                error
            )

            # Save product even if page fails

            menu.append(
                {
                    "name": product["name"],
                    "price": None,
                    "currency": "SAR",
                    "category": extract_category(
                        product["url"]
                    ),
                    "description": "",
                    "customisable": (
                        "/options/"
                        in product["url"]
                    ),
                    "bestseller": False,
                    "source": product["url"]
                }
            )

    # ========================================
    # 5. SAVE JSON
    # ========================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            menu,
            file,
            indent=4,
            ensure_ascii=False
        )

    # ========================================
    # STATISTICS
    # ========================================

    prices_found = sum(
        1
        for item in menu
        if item["price"] is not None
    )

    prices_missing = (
        len(menu) - prices_found
    )

    customisable_count = sum(
        1
        for item in menu
        if item["customisable"]
    )

    print("\n========================================")
    print("SCRAPING COMPLETE")
    print("========================================")

    print(
        f"Products saved: {len(menu)}"
    )

    print(
        f"Prices found: {prices_found}"
    )

    print(
        f"Prices missing: {prices_missing}"
    )

    print(
        f"Customisable products: "
        f"{customisable_count}"
    )

    print(
        f"\nSaved to: {OUTPUT_FILE}"
    )

    input(
        "\nPress ENTER to close..."
    )

    browser.close()