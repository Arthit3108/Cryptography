import streamlit as st
from PIL import Image

from services_function_utlis import *
from cryptography.fernet import Fernet
import secrets


st.title("🔐 Encryption")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    if st.button("🔑 Home", use_container_width=True):
        st.switch_page("app.py") 


with col2:
    if st.button("🔓 Decryption", use_container_width=True):
        st.switch_page("pages/decrypt.py") 


st.markdown("""
<style>
button[kind="secondary"] {
    border-radius: 10px;
    padding: 10px 20px;
    transition: 0.3s ease-in-out;
}
button[kind="secondary"]:hover {
    background-color: #44475a;
    color: #f8f8f2;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)



uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    
    image = Image.open(uploaded_image)
    st.image(image, caption="uploaded image", use_container_width=True)

    password = st.text_input("Enter your password")

    # Show button only if not already encrypted

    if st.button("Encryption", use_container_width=True):
            # Secret key
            
        # key = Fernet.generate_key()
        key = get_key(current_key_version)
        
        cipher = Fernet(key)
        
        secret_key = secrets.randbelow(10**23 - 10**22) + 10**22
        text = str(secret_key) + ":" + password
        encrypted = cipher.encrypt(text.encode())

        # Decrypt
        # decrypted = cipher.decrypt(encrypted).decode()

        st.session_state.encrypted = True
        # Encryption
        encrypted_result = encrypt_image(
            image_file=uploaded_image,
            secret_key=secret_key,
            output_image_path="encrypted_color_image_all.png"
        )

            # Mark encryption done

        st.session_state.secret_key = encrypted # Save key if needed

            # Show encrypted image and key if encryption was done
        if st.session_state.encrypted:
            image = Image.open("encrypted_color_image_all.png")
            st.image(image, caption="encrypt image", use_container_width=True)
            st.text(f"Secret Key: \n {st.session_state.secret_key}")

st.markdown("""
<hr style="margin-top: 20px;">
<div style="text-align: center; font-size: 13px; color: gray;">
Created with ❤️ by Petch Pair Preaw | © 2025 ImageCrypt
</div>
""", unsafe_allow_html=True)
