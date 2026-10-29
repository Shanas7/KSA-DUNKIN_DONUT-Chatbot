import json
from playwright.sync_api import sync_playwright


URL = "https://www.dunkinksa.com/home"
OUTPUT_FILE = "dunkin_menu.json"


def clean_text(text):
    if not text:
        return ""

    return " ".join(text.split())


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

    print("================================")
    print("DUNKIN KSA MENU SCRAPER")
    print("================================")

    print("\nOpening Dunkin KSA website...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    # Give the website time to load dynamic content
    page.wait_for_timeout(8000)

    print("\nPage title:")
    print(page.title())

    print("\nCurrent URL:")
    print(page.url)

    print("\nCollecting menu items...")

    # Find all "View Item" buttons
    view_items = page.get_by_text(
        "View Item",
        exact=True
    )

    count = view_items.count()

    print(f"\nFound {count} menu item buttons.")

    menu = []

    for index in range(count):

        try:

            # Re-locate the elements every iteration
            # because opening an item can change the page
            items = page.get_by_text(
                "View Item",
                exact=True
            )

            if index >= items.count():
                break

            item_button = items.nth(index)

            # Get the parent card
            card = item_button.locator(
                "xpath=.."
            )

            card_text = clean_text(
                card.inner_text()
            )

            print("\n--------------------------------")
            print(f"ITEM {index + 1}/{count}")
            print("--------------------------------")
            print(card_text)

            lines = [
                clean_text(line)
                for line in card.inner_text().splitlines()
                if clean_text(line)
            ]

            # Try to identify the product name
            name = ""

            for line in lines:

                if line.lower() == "view item":
                    continue

                if line.startswith("SAR"):
                    continue

                if line.replace(".", "", 1).isdigit():
                    continue

                name = line
                break

            # Create the menu record
            item = {
                "name": name,
                "price": None,
                "currency": "SAR",
                "category": "",
                "description": "",
                "customisable": False,
                "bestseller": False,
                "source": URL
            }

            menu.append(item)

        except Exception as error:

            print(
                f"Could not process item "
                f"{index + 1}: {error}"
            )

    # Remove duplicate products
    unique_menu = {}

    for item in menu:

        name = item["name"]

        if name:

            unique_menu[
                name.lower()
            ] = item

    menu = list(
        unique_menu.values()
    )

    # Save JSON
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

    print("\n================================")
    print("MENU EXTRACTION COMPLETE")
    print("================================")

    print(
        f"Saved {len(menu)} items "
        f"to {OUTPUT_FILE}"
    )

    input(
        "\nPress ENTER to close the browser..."
    )

    browser.close()