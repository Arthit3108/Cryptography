import streamlit as st
from PIL import Image
from cryptography.fernet import Fernet
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
    password = st.text_input("Enter your secret password")
    

    if secret_key is not None:
        if st.button("Decrypt", use_container_width=True):

            # Decrypt
            try:
                # st.write("secret", secret_key)
                date = str(get_date(secret_key))
                # st.write("date", date)

                # key = get_key(date)
                # st.write("key", key)

                version = "KEY_" + date
                key = st.secrets[version]

                cipher = Fernet(key)

                secret_key = secret_key = ast.literal_eval(secret_key)
                # st.write("sec", secret_key)
                
                # ถอดรหัส 
                decrypted = cipher.decrypt(secret_key).decode()
                # st.write("dec", decrypted)

                secret_key, password_user = decrypted.split(":")

                if password == password_user:
                    decrypted_channels = decrypt_image(
                        encrypted_image_path="encrypted_color_image_all.png",
                        secret_key=int(secret_key),
                        output_path="decrypted_color_image_all.png"
                    )
                    encrypt_image = Image.open("decrypted_color_image_all.png")
                    st.image(encrypt_image, caption="decrypt image", use_container_width=True)
                    # st.write("pass") 
                else:
                    st.error("Invalid secret key or password format. Please enter secret key.") 
                 

            except ValueError:
                st.error("Invalid secret key or password format. Please enter secret key.")
                
            except Exception as e:
                st.error("Invalid secret key or password format. Please enter secret key.")
    
    # Secret key

st.markdown("""
<hr style="margin-top: 20px;">
<div style="text-align: center; font-size: 13px; color: gray;">
Created with ❤️ by Petch Pair Preaw | © 2025 ImageCrypt
</div>
""", unsafe_allow_html=True)


 