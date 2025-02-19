import streamlit as st
from modules import *
st.title("UdyogYantra.AI Assistant")
st.write("Ask a question related to the UdyogYantra.AI console.")

# User Input
user_input = st.text_area("Enter your query:")

# Button to Generate Response
if st.button("Generate"):
    if user_input.strip():
        st.subheader("Response:")
        placeholder = st.empty()
        streamed_text = ""
        for chunk in response(user_input):  
            if chunk:
                streamed_text += chunk
            else:
                streamed_text +=""
            placeholder.markdown(streamed_text) 
        url = open_link(streamed_text) 
        if (url):
            st.link_button("Redirect to Page", url)
    else:
        st.warning("Please enter a query before clicking Generate.")
        
