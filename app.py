import streamlit as st
from services_function_utlis import *


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

st.markdown("""
    <h1 style='padding: 10px; border-radius: 10px;'>
        🔑 Image Cryptography 
    </h1>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; font-size: 16px; margin-bottom: 20px; margin-top: 20px; color: #bbbbbb;">
 Upload your image and choose whether to encrypt or decrypt it using a secure key.  
</div>
""", unsafe_allow_html=True)



# Create two columns
col1, col2 = st.columns(2)

with col1:
    if st.button("🔐 Encryption", use_container_width=True):
        st.switch_page("pages/encrypt.py") 

    st.image("xray.jpg", use_container_width=True)
    st.image("doc.jpg", use_container_width=True)

    

with col2:
    if st.button("🔓 Decryption", use_container_width=True):
        st.switch_page("pages/decrypt.py") 

    st.image("xray_encrypt.jpg", use_container_width=True)
    st.image("doc_encp.jpg", use_container_width=True)


st.markdown("""
<hr style="margin-top: 20px;">
<div style="text-align: center; font-size: 13px; color: gray;">
Created with ❤️ by Petch Pair Preaw | © 2025 ImageCrypt
</div>
""", unsafe_allow_html=True)



# Do something after the button is clicked
# if st.session_state.button_clicked:
#     st.success("You clicked the button!")

