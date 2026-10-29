def detect_intent(message: str) -> str:

    message = message.lower().strip()

    # Complaint
    complaint_words = [
        "complaint",
        "complain",
        "issue",
        "problem",
        "bad service",
        "report an issue"
    ]

    if any(word in message for word in complaint_words):
        return "COMPLAINT"

    # Bestseller
    bestseller_words = [
        "bestseller",
        "best seller",
        "most popular",
        "popular item",
        "popular product",
        "what is popular"
    ]

    if any(word in message for word in bestseller_words):
        return "BESTSELLER_QUERY"

    # Price
    price_words = [
        "price",
        "cost",
        "how much",
        "rate"
    ]

    if any(word in message for word in price_words):
        return "PRICE_QUERY"

    # Category
    category_words = [
        "show me",
        "what are the",
        "menu",
        "beverages",
        "drinks",
        "donuts",
        "bakery",
        "snacks",
        "burgers"
    ]

    if any(word in message for word in category_words):
        return "CATEGORY_QUERY"

    # Greeting
    greeting_words = [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    if any(word in message for word in greeting_words):
        return "GREETING"

    # Default
    return "MENU_QUERY"