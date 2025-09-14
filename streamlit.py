import streamlit as st
import requests
import os


st.set_page_config(page_title = "MemeBot", page_icon = "🤖")
st.title("MemeBot 🤖")


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/chat")

IMAGE_DIR = "meme_templates"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image_path" in message:
            st.image(message["image_path"])

if prompt := st.chat_input("Describe your meme in question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)



    with st.chat_message("assistant"):
        with st.spinner("Let me cook..."):
            try:
                api_history = [
                        {"role": message["role"], "content": message["content"]}
                        for message in st.session_state.messages
                    ]

                payload = {
                        "question": prompt,
                        "chat_history": api_history[:-1]
                    }


                response = requests.post(BACKEND_URL, json=payload)
                response.raise_for_status()


                data = response.json()
                answer = data["answer"]
                filename = data["filename"]
                image_path = os.path.join(IMAGE_DIR, filename)

                st.markdown(answer)
                st.image(image_path)

                st.session_state.messages.append({"role": "assistant", "content": answer, "image_path": image_path})


            except requests.exceptions.RequestException as e:
                    st.error(f"Error communicating with backend: {e}")






                    


            




