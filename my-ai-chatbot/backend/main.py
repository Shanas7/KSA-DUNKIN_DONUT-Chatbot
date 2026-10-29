import os
import re
import traceback

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google import genai
from google.genai import types

from chatbot.intent import detect_intent

from menu.service import (
    get_category_items,
    search_menu,
    get_donuts,
    get_items_under_price
)

from outlet.service import (
    get_nearest_store_info,
    get_outlet_hours_info,
    get_order_outlet_info
)


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI()


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==========================================
# CHROMADB
# ==========================================

chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = chroma_client.get_collection(
    name="dunkin_menu_ksa"
)


print("========================================")
print("DUNKIN KSA BACKEND")
print("========================================")

print(
    "KSA products available:",
    collection.count()
)

print("========================================")


# ==========================================
# CONVERSATION STATE
# ==========================================

"""
Demo-only conversation memory.

The key is the session_id received from
the frontend.

Example:

session_id:
abc123

state:
waiting_for_billing_number
"""

conversation_states = {}


# ==========================================
# REQUEST MODEL
# ==========================================

class ChatRequest(BaseModel):

    session_id: str

    message: str


# ==========================================
# HOME ENDPOINT
# ==========================================

@app.get("/")
def home():

    return {
        "message":
        "Dunkin KSA AI chatbot backend is running!"
    }


# ==========================================
# CHAT ENDPOINT
# ==========================================

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        # --------------------------------------
        # 1. GET USER QUESTION
        # --------------------------------------

        question = request.message.strip()

        session_id = request.session_id.strip()


        if not session_id:

            return {
                "message":
                "Invalid chat session."
            }


        if not question:

            return {
                "message":
                "Please enter a question."
            }


        question_lower = question.lower()


        # --------------------------------------
        # 2. GET CURRENT CONVERSATION STATE
        # --------------------------------------

        current_state = conversation_states.get(
            session_id
        )


        print("\n========================================")
        print("NEW CHAT REQUEST")
        print("Session ID:", session_id)
        print("Question:", question)
        print("Current state:", current_state)
        print("========================================")


        # ======================================
        # 3. CONVERSATION STATE
        # ======================================
        #
        # This section handles messages that
        # depend on what happened previously.
        # ======================================


        # --------------------------------------
        # WAITING FOR MAIN COMPLAINT TYPE
        # --------------------------------------

        if current_state == "waiting_for_issue_type":

            if question_lower == "order issue":

                conversation_states[session_id] = (
                    "waiting_for_order_problem"
                )

                return {
                    "message": (
                        "I'm sorry about the order issue. 😔\n\n"
                        "Please select the type of order problem:"
                    ),

                    "options": [
                        "Wrong Order",
                        "Missing Item",
                        "Extra Item",
                        "Order Not Received",
                        "Other Order Problem"
                    ]
                }


            if question_lower == "food / product":

                conversation_states[session_id] = (
                    "waiting_for_food_problem"
                )

                return {
                    "message": (
                        "I'm sorry about the food or product issue. 😔\n\n"
                        "Please describe what went wrong."
                    )
                }


            if question_lower == "incorrect price":

                conversation_states[session_id] = (
                    "waiting_for_price_problem"
                )

                return {
                    "message": (
                        "I'm sorry about the pricing issue. 😔\n\n"
                        "Please provide the billing number or "
                        "tell me what price was incorrect."
                    )
                }


            if question_lower == "service":

                conversation_states[session_id] = (
                    "waiting_for_service_problem"
                )

                return {
                    "message": (
                        "I'm sorry about the service issue. 😔\n\n"
                        "Please describe what happened."
                    )
                }


            if question_lower == "menu information":

                conversation_states[session_id] = (
                    "waiting_for_menu_problem"
                )

                return {
                    "message": (
                        "Please tell me what menu information "
                        "you need help with."
                    )
                }


            if question_lower == "other":

                conversation_states[session_id] = (
                    "waiting_for_other_problem"
                )

                return {
                    "message": (
                        "Please describe the issue you would "
                        "like to report."
                    )
                }


            return {
                "message": (
                    "Please select one of the issue types "
                    "shown above."
                ),

                "options": [
                    "Order Issue",
                    "Food / Product",
                    "Incorrect Price",
                    "Service",
                    "Menu Information",
                    "Other"
                ]
            }


        # --------------------------------------
        # WAITING FOR ORDER PROBLEM
        # --------------------------------------

        if current_state == "waiting_for_order_problem":

            valid_order_problems = [
                "wrong order",
                "missing item",
                "extra item",
                "order not received",
                "other order problem"
            ]


            if question_lower in valid_order_problems:

                # Save the selected problem
                conversation_states[session_id] = (
                    "waiting_for_billing_number"
                )


                if question_lower == "wrong order":

                    problem_name = "wrong order"

                elif question_lower == "missing item":

                    problem_name = "missing item"

                elif question_lower == "extra item":

                    problem_name = "extra item"

                elif question_lower == "order not received":

                    problem_name = "order not received"

                else:

                    problem_name = "other order problem"


                return {
                    "message": (
                        f"I understand that you have a "
                        f"{problem_name} issue.\n\n"
                        "Please enter your billing number."
                    )
                }


            return {
                "message": (
                    "Please select the type of order problem "
                    "from the options below."
                ),

                "options": [
                    "Wrong Order",
                    "Missing Item",
                    "Extra Item",
                    "Order Not Received",
                    "Other Order Problem"
                ]
            }


        # --------------------------------------
        # WAITING FOR BILLING NUMBER
        # --------------------------------------

        if current_state == "waiting_for_billing_number":

            # Accept a numeric billing number
            billing_match = re.fullmatch(
                r"\d{4,20}",
                question
            )


            if billing_match:

                billing_number = question


                print(
                    "Billing number received:",
                    billing_number
                )


                # ----------------------------------
                # DEMO ORDER LOOKUP
                # ----------------------------------
                #
                # We don't have a real billing
                # database yet.
                #
                # Later:
                #
                # billing number
                #       ↓
                # order database
                #       ↓
                # outlet + timestamp
                #       ↓
                # CCTV
                #
                # For now we only demonstrate
                # the conversation flow.
                # ----------------------------------

                conversation_states[session_id] = (
                    "checking_order"
                )


                return {
                    "message": (
                        "Thank you. I'm checking the "
                        "order information... 🔎\n\n"
                        f"Billing number: {billing_number}\n\n"
                        "This is currently a demo. "
                        "The billing database and CCTV "
                        "system will be connected later."
                    )
                }


            return {
                "message": (
                    "Please enter a valid billing number "
                    "using numbers only."
                )
            }


        # --------------------------------------
        # OTHER COMPLAINT STATES
        # --------------------------------------

        if current_state in [
            "waiting_for_food_problem",
            "waiting_for_price_problem",
            "waiting_for_service_problem",
            "waiting_for_menu_problem",
            "waiting_for_other_problem"
        ]:

            conversation_states[session_id] = (
                "complaint_received"
            )


            return {
                "message": (
                    "Thank you for providing the details. "
                    "Your complaint information has been "
                    "received. A support workflow can be "
                    "connected here later."
                )
            }


        # ======================================
        # 4. DETECT INTENT
        # ======================================

        intent = detect_intent(question)

        print(
            "Detected intent:",
            intent
        )


        # ======================================
        # 5. START COMPLAINT WORKFLOW
        # ======================================

        if intent == "COMPLAINT":

            conversation_states[session_id] = (
                "waiting_for_issue_type"
            )


            return {
                "message": (
                    "I'm sorry you had a problem. 😔\n\n"
                    "I can help you report it. "
                    "Please select the type of issue:"
                ),

                "options": [
                    "Order Issue",
                    "Food / Product",
                    "Incorrect Price",
                    "Service",
                    "Menu Information",
                    "Other"
                ]
            }


        # ======================================
        # 6. CATEGORY QUERY
        # ======================================

        if intent == "CATEGORY_QUERY":

            words = question_lower.split()

            category = None


            for word in words:

                items = get_category_items(word)

                if items:

                    category = word

                    break


            if category:

                items = get_category_items(
                    category
                )


                response_text = (
                    f"Here are the {category} "
                    "available on our menu:\n\n"
                )


                for item in items:

                    # Ignore missing/zero prices
                    if item.get("price", 0) <= 0:

                        continue


                    response_text += (
                        f"- {item['name']} - "
                        f"{item['currency']} "
                        f"{item['price']:.2f}\n"
                    )


                return {
                    "message":
                    response_text
                }


        # ======================================
        # 7. OUTLET INFORMATION
        # ======================================

        # --------------------------------------
        # NEAREST OUTLET
        # --------------------------------------

        if (
            "nearest dunkin" in question_lower
            or "nearest store" in question_lower
            or "nearest outlet" in question_lower
            or "find a dunkin" in question_lower
            or "where is dunkin" in question_lower
        ):

            outlet_info = (
                get_nearest_store_info()
            )


            return {
                "message":
                outlet_info["message"],

                "url":
                outlet_info["url"]
            }


        # --------------------------------------
        # OPENING HOURS
        # --------------------------------------

        if (
            "opening hours" in question_lower
            or "opening time" in question_lower
            or "closing time" in question_lower
            or "what time do you open" in question_lower
            or "what time do you close" in question_lower
        ):

            outlet_info = (
                get_outlet_hours_info()
            )


            return {
                "message":
                outlet_info["message"],

                "url":
                outlet_info["url"]
            }


        # --------------------------------------
        # ORDER OUTLET
        # --------------------------------------

        if (
            "which outlet" in question_lower
            or "what outlet" in question_lower
            or "order came from" in question_lower
            or "order come from" in question_lower
        ):

            outlet_info = (
                get_order_outlet_info()
            )


            return {
                "message":
                outlet_info["message"]
            }


        # ======================================
        # 8. MENU SEARCH
        # ======================================

        # --------------------------------------
        # CHOCOLATE SEARCH
        # --------------------------------------

        if (
            "chocolate" in question_lower
            or "choco" in question_lower
        ):

            items = search_menu(
                "chocolate"
            )


            items = [
                item
                for item in items
                if item.get("price", 0) > 0
            ]


            if items:

                response_text = (
                    "Here are the chocolate items "
                    "available on our menu:\n\n"
                )


                for item in items:

                    response_text += (
                        f"- {item['name']} - "
                        f"{item['currency']} "
                        f"{item['price']:.2f}\n"
                    )


                return {
                    "message":
                    response_text
                }


        # --------------------------------------
        # DONUT SEARCH
        # --------------------------------------

        if (
            "donut" in question_lower
            or "munchkin" in question_lower
        ):

            items = get_donuts()


            items = [
                item
                for item in items
                if item.get("price", 0) > 0
            ]


            if items:

                response_text = (
                    "Here are the donuts and "
                    "munchkins available on our menu:\n\n"
                )


                for item in items:

                    response_text += (
                        f"- {item['name']} - "
                        f"{item['currency']} "
                        f"{item['price']:.2f}\n"
                    )


                return {
                    "message":
                    response_text
                }


        # --------------------------------------
        # PRICE SEARCH
        # --------------------------------------

        price_match = re.search(
            r"(?:sar|sr)\s*(\d+(?:\.\d+)?)",
            question_lower
        )


        if price_match:

            max_price = float(
                price_match.group(1)
            )


            items = get_items_under_price(
                max_price
            )


            items = [
                item
                for item in items
                if item.get("price", 0) > 0
            ]


            if items:

                response_text = (
                    f"Here are some items you can get "
                    f"for SAR {max_price:.2f} or less:\n\n"
                )


                for item in items:

                    response_text += (
                        f"- {item['name']} - "
                        f"{item['currency']} "
                        f"{item['price']:.2f}\n"
                    )


                return {
                    "message":
                    response_text
                }


            return {
                "message": (
                    f"I couldn't find any menu items "
                    f"for SAR {max_price:.2f} or less."
                )
            }


        # ======================================
        # 9. CREATE QUERY EMBEDDING
        # ======================================

        print(
            "Creating query embedding..."
        )


        result = client.models.embed_content(

            model="gemini-embedding-001",

            contents=question,

            config=types.EmbedContentConfig(

                task_type="RETRIEVAL_QUERY",

                output_dimensionality=768
            )
        )


        query_embedding = (
            result.embeddings[0].values
        )


        print(
            "Embedding created."
        )


        # ======================================
        # 10. SEARCH CHROMADB
        # ======================================

        print(
            "Searching KSA ChromaDB..."
        )


        results = collection.query(

            query_embeddings=[
                query_embedding
            ],

            n_results=5
        )


        documents = results["documents"][0]


        print(
            "Documents found:",
            len(documents)
        )


        # ======================================
        # 11. CREATE CONTEXT
        # ======================================

        context = "\n".join(
            documents
        )


        # ======================================
        # 12. CREATE RAG PROMPT
        # ======================================

        prompt = f"""
You are a helpful customer-service AI assistant
for Dunkin Saudi Arabia.

Use ONLY the information provided in the
KSA menu context below.

Do not invent:
- products
- prices
- ingredients
- availability
- promotions
- bestseller information

If the information is not available in the
context, say:

"I don't have enough information to answer that."

Prices are in SAR.

When giving a price, always include SAR.

Do not assume that any product is a bestseller
unless the provided data explicitly says so.

Keep your answer short, clear and friendly.

KSA MENU CONTEXT:
{context}

CUSTOMER QUESTION:
{question}
"""


        # ======================================
        # 13. GENERATE ANSWER
        # ======================================

        print(
            "Sending request to Gemini..."
        )


        response = client.models.generate_content(

            model="gemini-3.5-flash-lite",

            contents=prompt,

            config=types.GenerateContentConfig(

                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                ),

                max_output_tokens=200
            )
        )


        print(
            "Gemini request completed."
        )


        # ======================================
        # 14. DEBUG GEMINI RESPONSE
        # ======================================

        print(
            "\n========== GEMINI RESPONSE =========="
        )


        print(
            "Response text:",
            repr(response.text)
        )


        print(
            "======================================"
        )


        # ======================================
        # 15. RETURN RESPONSE
        # ======================================

        return {
            "message":
            response.text
        }


    # ==========================================
    # ERROR HANDLING
    # ==========================================

    except Exception as error:

        print(
            "\n========== ERROR =========="
        )


        print(
            "Error:",
            str(error)
        )


        traceback.print_exc()


        print(
            "============================"
        )


        return {

            "message":
            "An error occurred while processing your request.",

            "error":
            str(error)
        }