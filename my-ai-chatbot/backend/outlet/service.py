# ==========================================
# DUNKIN KSA OUTLET SERVICE
# ==========================================

OFFICIAL_STORE_LOCATOR = (
    "https://www.dunkinksa.com/nearby_stores?source=2"
)


def get_nearest_store_info():
    """
    Provide the official Dunkin KSA store locator.
    """

    return {
        "message": (
            "You can find your nearest Dunkin KSA outlet "
            "using the official store locator."
        ),
        "url": OFFICIAL_STORE_LOCATOR
    }


def get_outlet_hours_info():
    """
    Opening hours are not currently stored
    in our local database.
    """

    return {
        "message": (
            "I don't currently have verified opening "
            "hours for Dunkin KSA outlets. "
            "Please check the official store locator "
            "for the outlet's current hours."
        ),
        "url": OFFICIAL_STORE_LOCATOR
    }


def get_order_outlet_info():
    """
    Outlet associated with an order requires
    order/billing data. We will connect this
    later when we build the order database.
    """

    return {
        "message": (
            "I can help identify the outlet for your order, "
            "but I need your order or billing information "
            "to look it up."
        )
    }