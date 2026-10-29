import re
import json

INPUT_FILE = "dunkin_menu_raw.txt"
OUTPUT_FILE = "dunkin_menu.json"


# Categories available on the Dunkin menu
categories = {
    "Cold Beverages",
    "Hot Beverages",
    "Burgers & More",
    "Burger Meals",
    "Single Burger",
    "Wraps",
    "Snacks",
    "Combos"
}


# Read raw menu
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    lines = [line.strip() for line in file.readlines()]


menu = []

current_category = None


for i, line in enumerate(lines):

    # --------------------------------
    # 1. Detect category
    # --------------------------------

    category_found = None

    for category in categories:

        # Handles:
        # Cold Beverages
        # Cold Beverages 22

        if line == category or re.match(
            rf"^{re.escape(category)}\s+\d+$",
            line
        ):
            category_found = category
            break

    if category_found:
        current_category = category_found
        continue


    # --------------------------------
    # 2. Detect price
    # --------------------------------

    price_match = re.match(
        r"₹\s*([\d,]+(?:\.\d+)?)$",
        line
    )

    if price_match and current_category:

        price = float(
            price_match.group(1).replace(",", "")
        )


        # --------------------------------
        # 3. Find product name
        # --------------------------------

        name = ""

        j = i - 1

        while j >= 0:

            previous_line = lines[j]

            if previous_line in ["", "ADD", "Customisable"]:
                j -= 1
                continue

            # Avoid category names
            if previous_line in categories:
                j -= 1
                continue

            # Avoid filter/navigation text
            if previous_line in [
                "Veg",
                "Non-Veg",
                "Pickup",
                "From",
                "Select Outlet",
                "CHANGE",
                "LOGIN / SIGN UP"
            ]:
                j -= 1
                continue

            name = previous_line
            break


        # --------------------------------
        # 4. Check if customisable
        # --------------------------------

        customisable = False

        next_lines = lines[i + 1:i + 4]

        if "Customisable" in next_lines:
            customisable = True


        # --------------------------------
        # 5. Save product
        # --------------------------------

        if name:

            menu.append({
                "name": name,
                "price": price,
                "category": current_category,
                "customisable": customisable
            })


# --------------------------------
# Remove duplicates
# --------------------------------

unique_menu = []

seen = set()

for item in menu:

    key = (
        item["name"],
        item["price"],
        item["category"]
    )

    if key not in seen:
        seen.add(key)
        unique_menu.append(item)


# --------------------------------
# Save JSON
# --------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        unique_menu,
        file,
        indent=2,
        ensure_ascii=False
    )


print(f"Saved {len(unique_menu)} menu items.")

print("\nFirst 10 items:\n")

for item in unique_menu[:10]:
    print(item)