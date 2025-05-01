import streamlit as st
import json
import os
import time
import base64
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

# === Constants ===
DATA_FILE = "user_data.json"
LOCKOUT_FILE = "lockout.json"
MAX_ATTEMPTS = 3
LOCKOUT_TIME_SECONDS = 60  # 1 minute lockout
MASTER_PASSWORD = "admin123"

# === Load or Initialize Files ===
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(LOCKOUT_FILE):
    with open(LOCKOUT_FILE, "w") as f:
        json.dump({}, f)

# === Encryption Setup ===
key = base64.urlsafe_b64encode(hashlib.sha256(b"secret_key").digest())
cipher = Fernet(key)

# === Helper Functions ===
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_lockout():
    with open(LOCKOUT_FILE, "r") as f:
        return json.load(f)

def save_lockout(lockout_info):
    with open(LOCKOUT_FILE, "w") as f:
        json.dump(lockout_info, f)

def hash_passkey_pbkdf2(passkey, salt="somesalt"):
    return hashlib.pbkdf2_hmac("sha256", passkey.encode(), salt.encode(), 100000).hex()

def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text):
    return cipher.decrypt(encrypted_text.encode()).decode()

def is_locked_out(username):
    lockouts = load_lockout()
    user_info = lockouts.get(username)
    if user_info:
        if user_info["attempts"] >= MAX_ATTEMPTS:
            last_attempt_time = datetime.fromisoformat(user_info["last_attempt"])
            if datetime.now() < last_attempt_time + timedelta(seconds=LOCKOUT_TIME_SECONDS):
                return True
    return False

def record_failed_attempt(username):
    lockouts = load_lockout()
    user_info = lockouts.get(username, {"attempts": 0, "last_attempt": datetime.now().isoformat()})
    user_info["attempts"] += 1
    user_info["last_attempt"] = datetime.now().isoformat()
    lockouts[username] = user_info
    save_lockout(lockouts)

def reset_attempts(username):
    lockouts = load_lockout()
    if username in lockouts:
        lockouts[username] = {"attempts": 0, "last_attempt": datetime.now().isoformat()}
        save_lockout(lockouts)

# === Streamlit UI ===
st.title("🔐 Secure Data Encryption System")

menu = ["Login", "Register", "Store Data", "Retrieve Data"]
choice = st.sidebar.selectbox("Navigation", menu)

# === Authentication State ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# === Login ===
if choice == "Login":
    st.subheader("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if is_locked_out(username):
            st.error("⏳ Account is temporarily locked due to too many failed attempts.")
        else:
            data = load_data()
            if username in data:
                hashed_input = hash_passkey_pbkdf2(password)
                if data[username]["password"] == hashed_input:
                    st.success("✅ Login successful")
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    reset_attempts(username)
                else:
                    record_failed_attempt(username)
                    st.error("❌ Incorrect password.")
            else:
                st.warning("🚫 User not found.")

# === Register ===
elif choice == "Register":
    st.subheader("📝 Register New User")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")

    if st.button("Register"):
        data = load_data()
        if new_username in data:
            st.warning("⚠️ Username already exists.")
        else:
            hashed_pw = hash_passkey_pbkdf2(new_password)
            data[new_username] = {"password": hashed_pw, "data": ""}
            save_data(data)
            st.success("✅ Registered successfully! Please login.")

# === Store Data ===
elif choice == "Store Data":
    st.subheader("💾 Store Encrypted Data")

    if not st.session_state.authenticated:
        st.warning("🔐 Please log in to store data.")
    else:
        user_data = st.text_area("Enter data to store:")
        if st.button("Encrypt & Store"):
            data = load_data()
            encrypted_text = encrypt_data(user_data)
            data[st.session_state.username]["data"] = encrypted_text
            save_data(data)
            st.success("✅ Data stored securely!")

# === Retrieve Data ===
elif choice == "Retrieve Data":
    st.subheader("🔍 Retrieve Your Data")

    if not st.session_state.authenticated:
        st.warning("🔐 Please log in to retrieve data.")
    else:
        if st.button("Retrieve"):
            data = load_data()
            encrypted_text = data[st.session_state.username]["data"]
            if encrypted_text:
                try:
                    decrypted = decrypt_data(encrypted_text)
                    st.success(f"Decrypted Data: {decrypted}")
                except:
                    st.error("❌ Failed to decrypt.")
            else:
                st.info("ℹ️ No data stored yet.")
