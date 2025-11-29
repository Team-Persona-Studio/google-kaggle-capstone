# frontend/app.py
import streamlit as st
import requests
import time
from datetime import datetime
import os


BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
if BASE_URL.endswith("/"):
    BASE_URL = BASE_URL[:-1]

st.set_page_config(page_title="Character AI", layout="wide")

# ---------------------- SESSION STATE ----------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "persona_id" not in st.session_state:
    st.session_state.persona_id = None
if "personas" not in st.session_state:
    st.session_state.personas = []
if "persona_name" not in st.session_state:
    st.session_state.persona_name = None
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"   # Track active page


# ---------------------- API HELPERS ----------------------
def api_post(path, json=None, params=None):
    try:
        return requests.post(f"{BASE_URL}{path}", json=json, params=params, timeout=30)
    except Exception as e:
        st.error(f"Network Error: {e}")
        return None


def api_get(path, params=None):
    try:
        return requests.get(f"{BASE_URL}{path}", params=params, timeout=30)
    except Exception as e:
        st.error(f"Network Error: {e}")
        return None


def api_delete(path, params=None):
    try:
        return requests.delete(f"{BASE_URL}{path}", params=params, timeout=30)
    except Exception as e:
        st.error(f"Network Error: {e}")
        return None


# ---------------------- AUTH UI ----------------------
def register_ui():
    st.subheader("Register")
    username = st.text_input("New username")
    password = st.text_input("New password", type="password")

    if st.button("Register"):
        if not username or not password:
            st.warning("Fill all fields")
            return

        r = api_post("/register", {"username": username, "password": password})
        if r and r.status_code == 200:
            st.success("Registered! Now login.")
        else:
            st.error(r.text if r else "Error")


def login_ui():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.warning("Enter username and password")
            return

        r = api_post("/login", {"username": username, "password": password})
        if r and r.status_code == 200:
            data = r.json()
            st.session_state.user_id = data["user_id"]
            st.session_state.username = data["username"]
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")


# ---------------------- PERSONA FUNCTIONS ----------------------
def load_personas():
    if not st.session_state.user_id:
        return []
    r = api_get(f"/personas/list/{st.session_state.user_id}")
    if r and r.status_code == 200:
        st.session_state.personas = r.json()
    return st.session_state.personas


def create_persona_ui():
    st.header("Create Persona")

    with st.form("persona_form"):
        name = st.text_input("Character Name")
        mode = st.selectbox("Mode", ["auto", "custom"])
        tone = st.text_input("Tone (optional)")
        summary = st.text_area("Summary (required only for CUSTOM)") if mode == "custom" else None
        submit = st.form_submit_button("Create")

    if submit:
        if not name:
            st.error("Character name is required")
            return

        if mode == "custom" and not summary:
            st.error("Summary required for custom mode")
            return

        payload = {
            "user_id": st.session_state.user_id,
            "character_name": name,
            "mode": mode,
            "tone": tone or None,
            "summary": summary or None,
        }

        r = api_post("/personas", json=payload)
        if r and r.status_code == 200:
            new_p = r.json()
            st.success(f"🎉 Character **{new_p['character_name']}** created successfully!")

            # Auto-select newly created persona and redirect to Chat page
            st.session_state.persona_id = new_p["id"]
            st.session_state.persona_name = new_p["character_name"]
            st.session_state.menu = "Chat"
            st.rerun()
        else:
            st.error(r.text if r else "Error")


def delete_persona(persona_id):
    params = {"user_id": st.session_state.user_id}
    r = api_delete(f"/personas/{persona_id}", params=params)

    if r and r.status_code == 200:
        st.success("Persona deleted successfully")
        if st.session_state.persona_id == persona_id:
            st.session_state.persona_id = None
        st.rerun()
    else:
        st.error(r.text if r else "Error deleting persona")


# ---------------------- CHAT UI ----------------------
def chat_ui(persona):
    st.header(f"Chat with {persona['character_name']}")

    persona_id = persona["id"]

    # Fetch full history
    r = api_get(f"/messages/full/{persona_id}")
    messages = r.json() if (r and r.status_code == 200) else []

    # Display messages
    for m in messages:
        sender = m["sender"]
        text = m["message"]
        if sender == "user":
            st.chat_message("user").markdown(text)
        else:
            st.chat_message("assistant").markdown(text)

    # Chat input
    user_msg = st.chat_input("Type your message…")

    if user_msg:
        # Show user message instantly
        st.chat_message("user").markdown(user_msg)

        payload = {
            "user_id": st.session_state.user_id,
            "persona_id": persona_id,
            "user_input": user_msg
        }

        # Send to backend
        api_post("/agent/respond", json=payload)

        # Wait a moment, then refresh history
        time.sleep(0.2)
        st.rerun()


# ---------------------- MAIN PAGE ----------------------
def main():
    st.title("Character AI – Frontend")

    if not st.session_state.user_id:
        st.sidebar.title("Welcome")
        mode = st.sidebar.radio("Select Action", ["Login", "Register"])
        if mode == "Login":
            login_ui()
        else:
            register_ui()
        return

    # Logged-in UI
    st.sidebar.title(f"Logged in as {st.session_state.username}")

    menu_items = ["Dashboard", "Create Persona", "Chat", "Logout"]

    # Use the session state value to set the radio button's index
    current_index = menu_items.index(st.session_state.menu) if st.session_state.menu in menu_items else 0

    action = st.sidebar.radio(
        "Menu",
        menu_items,
        index=current_index
    )

    # Only update if user actually clicked a different option
    if action != st.session_state.menu:
        st.session_state.menu = action

    # Render pages
    if st.session_state.menu == "Logout":
        st.session_state.clear()
        st.rerun()

    elif st.session_state.menu == "Dashboard":
        personas = load_personas()
        st.header("Your Characters")

        if not personas:
            st.info("No personas yet. Create one!")
        else:
            for p in personas:
                with st.container():
                    cols = st.columns([3, 1, 1])
                    cols[0].markdown(
                        f"### {p['character_name']}\nMode: `{p['mode']}`\nTone: `{p.get('tone', '')}`"
                    )

                    if cols[1].button("Chat", key=f"chat_{p['id']}"):
                        st.session_state.persona_id = p["id"]
                        st.session_state.persona_name = p["character_name"]
                        st.session_state.menu = "Chat"
                        st.rerun()

                    if cols[2].button("Delete", key=f"del_{p['id']}"):
                        delete_persona(p["id"])

    elif st.session_state.menu == "Create Persona":
        create_persona_ui()

    elif st.session_state.menu == "Chat":
        if not st.session_state.persona_id:
            st.info("Select a persona from the Dashboard first.")
        else:
            personas = load_personas()
            persona = next((x for x in personas if x["id"] == st.session_state.persona_id), None)

            if persona:
                chat_ui(persona)
            else:
                st.error("Persona not found.")


if __name__ == "__main__":
    main()
    