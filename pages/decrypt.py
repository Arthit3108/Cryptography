import streamlit as st
from PIL import Image
import numpy as np
import random
import os

from services_function_utlis import *

st.title(" 🔓 Decryption")

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
            decrypted_channels = decrypt_image(
                encrypted_image_path="encrypted_color_image_all.png",
                secret_key=int(secret_key),
                    output_path="decrypted_color_image_all.png"
            )

            encrypt_image = Image.open("decrypted_color_image_all.png")
            st.image(encrypt_image, caption="decrypt image", use_container_width=True) 
    
    # Secret key


 
