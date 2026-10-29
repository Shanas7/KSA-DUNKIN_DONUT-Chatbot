/* =====================================================
   DUNKIN AI ASSISTANT
   FRONTEND JAVASCRIPT
===================================================== */


/* =====================================================
   SESSION ID
===================================================== */

/*
 * Every chat gets its own session ID.
 *
 * The backend uses this ID to remember
 * where the customer is in a conversation.
 */

function createSessionId() {

    if (window.crypto && crypto.randomUUID) {

        return crypto.randomUUID();

    }

    return (
        Date.now().toString(36) +
        Math.random().toString(36).substring(2)
    );
}


let sessionId = createSessionId();


/* =====================================================
   ELEMENTS
===================================================== */

const messageInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");

const messages =
    document.getElementById("messages");

const newChatButton =
    document.getElementById("newChatButton");


/* =====================================================
   COMPLAINT ELEMENTS
===================================================== */

const complaintButton =
    document.getElementById("complaintButton");

const complaintOverlay =
    document.getElementById("complaintOverlay");

const closeComplaint =
    document.getElementById("closeComplaint");

const complaintForm =
    document.getElementById("complaintForm");

const complaintSuccess =
    document.getElementById("complaintSuccess");


/* =====================================================
   DARK MODE
===================================================== */

const darkModeButton =
    document.getElementById("darkModeButton");


/* =====================================================
   ADD MESSAGE
===================================================== */

function addMessage(text, type) {

    const message =
        document.createElement("div");

    message.className =
        `message ${type}-message`;


    if (type === "assistant") {

        message.innerHTML = `
            <div class="avatar">
                DN
            </div>

            <div class="message-bubble">
                <p>${formatText(text)}</p>
            </div>
        `;

    } else {

        message.innerHTML = `
            <div class="message-bubble">
                <p>${formatText(text)}</p>
            </div>
        `;
    }


    messages.appendChild(message);


    messages.scrollTop =
        messages.scrollHeight;


    return message;
}


/* =====================================================
   FORMAT TEXT
===================================================== */

function formatText(text) {

    if (!text) {

        return "";
    }


    return text
        .replace(/\n/g, "<br>")
        .replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );
}


/* =====================================================
   ADD INTERACTIVE OPTIONS
===================================================== */

function addOptions(options) {

    if (!options || options.length === 0) {

        return;
    }


    const optionsContainer =
        document.createElement("div");


    optionsContainer.className =
        "chat-options";


    options.forEach(function(option) {

        const button =
            document.createElement("button");


        /*
         * IMPORTANT:
         * This class connects the button
         * to the CSS styling.
         */

        button.className =
            "chat-option-button";


        button.type =
            "button";


        button.textContent =
            option;


        /*
         * When the user clicks an option,
         * send that option to the backend.
         */

        button.addEventListener(
            "click",
            function() {

                messageInput.value =
                    option;

                sendMessage();

            }
        );


        optionsContainer.appendChild(
            button
        );

    });


    messages.appendChild(
        optionsContainer
    );


    messages.scrollTop =
        messages.scrollHeight;
}


/* =====================================================
   SEND MESSAGE
===================================================== */

async function sendMessage() {

    const message =
        messageInput.value.trim();


    /* -----------------------------------------
       Stop if input is empty
    ----------------------------------------- */

    if (!message) {

        return;
    }


    /* -----------------------------------------
       Add user message
    ----------------------------------------- */

    addMessage(
        message,
        "user"
    );


    /* -----------------------------------------
       Clear input
    ----------------------------------------- */

    messageInput.value = "";


    /* -----------------------------------------
       Disable send button
    ----------------------------------------- */

    sendButton.disabled = true;


    /* -----------------------------------------
       Show loading message
    ----------------------------------------- */

    const loadingMessage =
        addMessage(
            "Thinking...",
            "assistant"
        );


    try {

        /* -------------------------------------
           Send request to FastAPI
        ------------------------------------- */

        const response =
            await fetch(
                "http://127.0.0.1:8000/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        /*
                         * Send the conversation ID
                         * along with the message.
                         */

                        session_id: sessionId,

                        message: message
                    })
                }
            );


        /* -------------------------------------
           Check server response
        ------------------------------------- */

        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        /* -------------------------------------
           Convert response to JSON
        ------------------------------------- */

        const data =
            await response.json();


        /* -------------------------------------
           Remove loading message
        ------------------------------------- */

        loadingMessage.remove();


        /* -------------------------------------
           Add assistant response
        ------------------------------------- */

        addMessage(
            data.message,
            "assistant"
        );


        /* -------------------------------------
           Add interactive options
        ------------------------------------- */

        if (
            data.options &&
            data.options.length > 0
        ) {

            addOptions(
                data.options
            );
        }

    }


    catch (error) {

        console.error(
            "Chat error:",
            error
        );


        /* -------------------------------------
           Remove loading message
        ------------------------------------- */

        loadingMessage.remove();


        /* -------------------------------------
           Show error message
        ------------------------------------- */

        addMessage(
            "Sorry, I couldn't connect to the assistant. Please make sure the backend server is running.",
            "assistant"
        );

    }


    finally {

        /* -------------------------------------
           Re-enable send button
        ------------------------------------- */

        sendButton.disabled = false;


        /* -------------------------------------
           Focus input
        ------------------------------------- */

        messageInput.focus();
    }
}


/* =====================================================
   SEND BUTTON
===================================================== */

sendButton.addEventListener(
    "click",
    sendMessage
);


/* =====================================================
   ENTER KEY
===================================================== */

messageInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }
    }
);


/* =====================================================
   SUGGESTION CARDS
===================================================== */

const suggestionCards =
    document.querySelectorAll(
        ".suggestion-card"
    );


suggestionCards.forEach(
    function(card) {

        card.addEventListener(
            "click",
            function() {

                const question =
                    card.dataset.question;


                messageInput.value =
                    question;


                messageInput.focus();


                sendMessage();
            }
        );
    }
);


/* =====================================================
   NEW CHAT
===================================================== */

newChatButton.addEventListener(
    "click",
    function() {

        /*
         * IMPORTANT:
         *
         * Generate a NEW session ID.
         *
         * This tells the backend that this
         * is a completely new conversation.
         */

        sessionId =
            createSessionId();


        messages.innerHTML = `

            <div class="message assistant-message">

                <div class="avatar">
                    DN
                </div>

                <div class="message-bubble">

                    <p>
                        Hello! 👋 I'm your
                        Dunkin AI assistant.
                    </p>

                    <p>
                        I can help you with
                        menu items, prices,
                        categories and more.
                    </p>

                </div>

            </div>

        `;


        messageInput.value = "";


        messageInput.focus();
    }
);


/* =====================================================
   DARK MODE
===================================================== */

darkModeButton.addEventListener(
    "click",
    function() {

        document.body.classList.toggle(
            "dark"
        );


        /* -------------------------------------
           Save preference
        ------------------------------------- */

        const isDark =
            document.body.classList.contains(
                "dark"
            );


        localStorage.setItem(
            "dunkinDarkMode",
            isDark
        );
    }
);


/* =====================================================
   LOAD DARK MODE PREFERENCE
===================================================== */

const savedDarkMode =
    localStorage.getItem(
        "dunkinDarkMode"
    );


if (savedDarkMode === "true") {

    document.body.classList.add(
        "dark"
    );
}


/* =====================================================
   REPORT AN ISSUE
===================================================== */

complaintButton.addEventListener(
    "click",
    function() {

        complaintOverlay.classList.add(
            "show"
        );
    }
);


/* =====================================================
   CLOSE COMPLAINT
===================================================== */

closeComplaint.addEventListener(
    "click",
    function() {

        complaintOverlay.classList.remove(
            "show"
        );
    }
);


/* =====================================================
   CLOSE WHEN CLICKING OUTSIDE
===================================================== */

complaintOverlay.addEventListener(
    "click",
    function(event) {

        if (
            event.target ===
            complaintOverlay
        ) {

            complaintOverlay.classList.remove(
                "show"
            );
        }
    }
);


/* =====================================================
   ESC KEY CLOSE
===================================================== */

document.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Escape"
        ) {

            complaintOverlay.classList.remove(
                "show"
            );
        }
    }
);


/* =====================================================
   COMPLAINT FORM
===================================================== */

complaintForm.addEventListener(
    "submit",
    function(event) {

        event.preventDefault();


        /*
         * For now this only shows
         * a success message.
         *
         * Later we can connect this
         * form to FastAPI + database.
         */

        complaintSuccess.classList.add(
            "show"
        );


        complaintForm.reset();


        setTimeout(
            function() {

                complaintSuccess.classList.remove(
                    "show"
                );


                complaintOverlay.classList.remove(
                    "show"
                );

            },
            2000
        );
    }
);