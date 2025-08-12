import streamlit as st
import ollama
import os
import time


st.set_page_config(
    page_title="B-Ollama",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto",
)

TEXT_MODEL = "sushruth/solar-uncensored:latest"
MULTIMODAL_MODEL = "llava:34b"

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("B-Ollama")
st.write("Ask me anything, or upload an image and ask about it.")

with st.sidebar:
    st.header("Upload Image")
    uploaded_file = st.file_uploader(
        "Upload an image to chat about.", type=["png", "jpg", "jpeg"]
    )
    
    if uploaded_file:
        st.image(uploaded_file, caption="Image ready for analysis.")

    st.divider()

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        # Reloading the page
        st.rerun()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # For messages with image
        if "image_path" in message:
            st.image(message["image_path"], width=200)
        st.markdown(message["content"])


prompt = st.chat_input("What would you like to ask?")
if prompt:
    
    # Updates chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # checking model to ask response from
        model_to_use = TEXT_MODEL
        ollama_messages = [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ]

        # if image then use MULTIMODAL_MODEL
        if uploaded_file is not None:
            model_to_use = MULTIMODAL_MODEL
            
            # file to temp path
            temp_dir = "uploads"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            filepath = os.path.join(temp_dir, uploaded_file.name)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # adds image along with user prompt
            last_user_message = ollama_messages[-1]
            last_user_message['images'] = [filepath]
            
            # Add the image path to the session state for display
            st.session_state.messages[-1]["image_path"] = filepath

        #try for calling model
        try:
            stream = ollama.chat(
                model=model_to_use,
                messages=ollama_messages,
                stream=True,
            )

            #  displaying of response
            for chunk in stream:
                full_response += chunk['message']['content']
                time.sleep(0.01) # for better visuals
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            full_response = "Sorry, I encountered an error."

    # final response to chat
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )