# Importing the necessary modules from the Streamlit and LangChain packages
import streamlit as st
from langchain.llms import openllm


# Setting the title of the Streamlit application
st.title('Simple LLM-App 🤖')

# Creating a sidebar input widget for the OpenAI API key, input type is password for security
#openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password') #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


# Defining a function to generate a response using the OpenAI language model
def generate_response(input_text):
    # Initializing the OpenAI language model with a specified temperature and API key
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    # Displaying the generated response as an informational message in the Streamlit app
    st.info(llm(input_text))

# Creating a form in the Streamlit app for user input
with st.form('my_form'):
    # Adding a text area for user input
    text = st.text_area('Enter text:', '')
    # Adding a submit button for the form
    submitted = st.form_submit_button('Submit')
    # Displaying a warning if the entered API key does not start with 'sk-'
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    # If the form is submitted and the API key is valid, generate a response
    if submitted and openai_api_key.startswith('sk-'):
        generate_response(text)