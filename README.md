# 🛡️ Secure Data Encryption System Using Streamlit

A secure web-based application built using **Streamlit** that allows users to store and retrieve encrypted data using passkeys. It ensures confidentiality with modern encryption, PBKDF2 hashing, time-based lockouts, and a simple multi-user login system.

---

## 🔐 Features

- **Data Encryption & Decryption** using Fernet (from `cryptography` library).
- **PBKDF2_HMAC** for secure passkey hashing.
- **Multi-User Support** with simple username-password authentication.
- **Data Persistence** with local JSON storage.
- **Time-Based Lockout** after multiple failed attempts.
- **Streamlit UI** for easy and interactive experience.

---

## 🗃️ Data Structure

Data is stored in a local JSON file (`data.json`) structured as:

```json
{
  "users": {
    "username": {
      "password_hash": "pbkdf2_hash",
      "salt": "user_salt",
      "data": [
        {
          "encrypted_text": "fernet_encrypted_string",
          "passkey_hash": "pbkdf2_hash"
        }
      ]
    }
  }

