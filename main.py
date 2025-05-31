import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from prompts import HITESH_SIR_PROMPT, PIYUSH_SIR_PROMPT

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

st.title("🎙️ Chat with AI Persona")
username = st.text_input("Enter your name : ")
persona = st.selectbox("Choose a persona:", ["Piyush Garg", "Hitesh Choudhary"])

if persona == "Hitesh Choudhary":
    SYSTEM_PROMPT = HITESH_SIR_PROMPT
    persona_name = "Hitesh Sir"
else:
    SYSTEM_PROMPT = PIYUSH_SIR_PROMPT
    persona_name = "Piyush Sir"

# Session state for chat history - Fresh chat start ( in case of first time chat and switching persona)
if "messages" not in st.session_state or st.session_state.get("last_persona") != persona:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.session_state.last_persona = persona

# Show chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"**{username}:** {msg['content']}")
    elif msg["role"] == "assistant":
        shown = False
        with st.chat_message("assistant"):
            for line in msg["content"].strip().splitlines():
                line = line.strip()
                if not line or line.startswith("```"):
                    continue
                line = line.replace("```json", "").replace("```", "").strip()
                try:
                    data = json.loads(line)
                    if data.get("step") == "result":
                        st.markdown(f"**{persona_name}:** {data.get('content')}")
                        shown = True
                except json.JSONDecodeError:
                    continue
            if not shown:
                # Debug: Show raw response if no result step found
                st.markdown(
                    f"<span style='color:gray;font-size:small;'>[No 'result' step found. Raw response:]</span><br><code>{msg['content']}</code>",
                    unsafe_allow_html=True
                )

query = st.text_input(f"{username}, enter your question:", key="user_input")

if st.button("Ask") and query.strip():
    st.session_state.messages.append({"role": "user", "content": query})
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=st.session_state.messages
        )
        content = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": content})
    st.rerun()