import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from prompts import HITESH_SIR_PROMPT, PIYUSH_SIR_PROMPT

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
client = OpenAI(
    api_key=api_key,
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
            # Try to parse as JSON array first
            try:
                data = json.loads(msg["content"])
                if isinstance(data, list):
                    for obj in data:
                        if obj.get("step") == "result":
                            st.markdown(f"**{persona_name}:** {obj.get('content')}")
                            shown = True
                elif isinstance(data, dict):
                    if data.get("step") == "result":
                        st.markdown(f"**{persona_name}:** {data.get('content')}")
                        shown = True
            except json.JSONDecodeError:
                # Fallback: parse line by line
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

st.markdown(
    """
    <hr style='margin-top: 2em;'>
    <div style='text-align:center; font-size:0.9em; color:gray;'>
        Made by Lakshay Jain
        <a href='https://github.com/LakshayJ17' target='_blank' style='text-decoration: none; margin-left: 6px;'>
            <img src='https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/github.svg' alt='GitHub' width='18' style='vertical-align:middle; filter: invert(100%);' />
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

