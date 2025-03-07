# Importing the necessary modules from the Streamlit and LangChain packages
import streamlit as st 
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage

st.set_page_config(page_title="LLM Chat Application")
st.header("Chat :blue[Application]")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [AIMessage("Hello, how can I help you?")]

chat_history = st.session_state["chat_history"]
for history in chat_history:
    if isinstance(history, AIMessage):
        st.chat_message("ai").write(history.content)
    if isinstance(history, HumanMessage):
        st.chat_message("human").write(history.content)

prompt = st.chat_input("Add your prompt..")

llm = ChatOllama(model="llama2-uncensored", temperature=0.7)

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["chat_history"] += [HumanMessage(prompt)]
    output = llm.stream(prompt)
    
    with st.chat_message("ai"):
        ai_message = st.write_stream(output)
    
    st.session_state["chat_history"] += [AIMessage(ai_message)]

## https://www.youtube.com/watch?v=k8I8nsml47g