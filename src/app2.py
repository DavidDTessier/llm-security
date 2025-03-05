# Importing the necessary modules from the Streamlit and LangChain packages
import streamlit as st
from langchain_community.llms import Ollama


# Setting the title of the Streamlit application
st.title('Simple LLM-App 🤖')

# Creating a sidebar input widget for the OpenAI API key, input type is password for security
#openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password') #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



# Defining a function to generate a response using the OpenAI language model
def generate_response(input_text):
    # Initializing the OpenAI language model with a specified temperature and API key
    llm = ollama(temperature=0.7, openai_api_key=openai_api_key)
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


        with st.sidebar:
    st.title('Simple LLM-App 🤖')
    st.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlit](<https://streamlit.io/>)
    - [HugChat](<https://github.com/Soulter/hugging-chat-api>)
    - [OpenAssistant/oasst-sft-6-llama-30b-xor](<https://huggingface.co/OpenAssistant/oasst-sft-6-llama-30b-xor>) LLM model
    
    💡 Note: No API key required!
    ''')

    st.

    st.write('Made with ❤️ by [Data Professor](<https://youtube.com/dataprofessor>)')

# Creating a form in the Streamlit app for user input
with st.form('my_form'):


    llm = OllamaLLM(model="llama2-uncensored")
    # User query input
    query = st.text_input(label="Enter your query")

    # Submit button
    if st.form_submit_button(label="Ask LLM", type="primary"):

        with st.container(border=True):
            with st.spinner(text="Generating response"):
                # Get response from llm
                response = llm.invoke(query)

            # Display it
            st.write(response)

