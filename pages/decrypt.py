import streamlit as st
from PIL import Image
from cryptography.fernet import Fernet
import secrets
import ast



from services_function_utlis import *

st.title(" 🔓 Decryption")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    if st.button("🔑 Home", use_container_width=True):
        st.switch_page("app.py") 


with col2:
    if st.button("🔐 Encryption", use_container_width=True):
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

# st.button("Encryption")


if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption="uploaded image", use_container_width=True)

    secret_key = st.text_input("Enter your secret key")
    

    if secret_key is not None:
        if st.button("Decrypt", use_container_width=True):

            # Decrypt
            try:
                received = ast.literal_eval(secret_key)
                # received = secret_key.encode()
                # received = received.decode()
                key_part, encrypted_part = received.split(b'||')

                # สร้าง cipher ใหม่
                cipher = Fernet(key_part)

                # ถอดรหัส
                decrypted_secret_key = cipher.decrypt(encrypted_part).decode()

                decrypted_channels = decrypt_image(
                    encrypted_image_path="encrypted_color_image_all.png",
                    secret_key=int(decrypted_secret_key),
                        output_path="decrypted_color_image_all.png"
                )

                encrypt_image = Image.open("decrypted_color_image_all.png")
                st.image(encrypt_image, caption="decrypt image", use_container_width=True) 
            except ValueError:
                st.error("Invalid secret key format. Please enter secret key.")
            except Exception as e:
                st.error("Invalid secret key format. Please enter secret key.")
    
    # Secret key

st.markdown("""
<hr style="margin-top: 20px;">
<div style="text-align: center; font-size: 13px; color: gray;">
Created with ❤️ by Petch Pair Preaw | © 2025 ImageCrypt
</div>
""", unsafe_allow_html=True)


 
