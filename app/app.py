"""Importing the necessary modules from the Streamlit and LangChain packages"""

import json
import sys
from typing import MutableMapping

import ollama
import yaml

from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama import ChatOllama
from google.cloud import modelarmor_v1
from google.oauth2 import service_account

import streamlit as st

from yaml.loader import SafeLoader
with open('config.yaml', mode="r", encoding="utf-8") as file:
    app_config = yaml.load(file, Loader=SafeLoader)

creds = credentials = service_account.Credentials.from_service_account_file("creds.json")
llm_host=app_config["appsettings"]["ollama_host_url"]
gcp_model_armor_api_url=app_config["appsettings"]["gcp_model_armor_api_endpoint"]
gcp_model_armor_template=app_config["appsettings"]["gcp_model_armor_template"]


ollama_client=ollama.Client(llm_host)

def init():
    """Initializes streamlit UI"""
    package_data = {
        "name": "LLM Chatbot Application using Streamlit, ChatOllama, and GCP's Model Armor.",
        "version": "1.0.0-alpha.2",
    }

    st.set_page_config(
        page_title=package_data["name"],
        page_icon="?",
        layout="wide"
    )
    st.header("Chat :blue[Application]")

# Loads available models from JSON file
def load_models():
    """Loads a list of LLM models that we want to use"""
    with open("./data/models.json", mode="r", encoding="UTF-8") as models:
        data = json.load(models)
    return data['models']

def pull_model():
    """Pull selected model from Ollama and installs it locally"""
    # pylint: disable=line-too-long
    # pylint: disable=broad-exception-caught
    model_name = st.session_state['selected_model']
    response = ollama_client.pull(model=model_name, stream=True)
    # Initialize a placeholder for progress update
    progress_bar = st.progress(0)
    progress_status = st.empty()
    try:
        for progress in response:
            if 'completed' in progress and 'total' in progress:
                # Calculate the percentage of completion
                completed = progress['completed']
                total = progress['total']
                progress_percentage = int((completed / total) * 100)
                progress_bar.progress(progress_percentage)
            if 'status' in progress:
                if progress['status'] == 'success':
                    progress_status.success("Model pulled successfully!")
                    break
                if progress['status'] == 'error':
                    progress_status.error("Error pulling the model No specific error message provided.")
                    break
    except Exception as e:
        progress_status.error(f"Failed to pull model: {str(e)}")

def init_chat_history():
    """Initializes chat history"""
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [AIMessage("Hello, how can I help you?")]

    if "selected_model" not in st.session_state:
        st.session_state["selected_model"]: load_models()[0]

    if "model_armor_protection" not in st.session_state:
        st.session_state["model_armor_protection"]: False

    chat_history = st.session_state["chat_history"]
    for history in chat_history:
        if isinstance(history, AIMessage):
            st.chat_message("ai").write(history.content)
        if isinstance(history, HumanMessage):
            st.chat_message("human").write(history.content)

def get_llm():
    """Initializes ChatOllama LLM"""
    # pylint: disable=line-too-long
    model = st.session_state["selected_model"]
    llm = ChatOllama(model=model,base_url=llm_host, temperature=0.7)
    if not llm:
        print("Could not init ChatOllam with the selected model, please make sure ollama has the model downloaded and in its library.")
        sys.exit(1)
    # otherwise return the initialized llm
    return llm

def get_model_armor_client():
    """Initializes ModelArmor Client"""
    ml_armor_client = modelarmor_v1.ModelArmorClient(
        transport="rest",
        client_options = {"api_endpoint" : gcp_model_armor_api_url},
        credentials=creds)
    if not ml_armor_client:
        print("Failed to initialize Model Armor Client")
        sys.exit(1)
    return ml_armor_client

def sanitize_llm_responses_with_model_armor(llm_response):
    """Sanitizes the response from the LLM using ModelArmor's SanitizeModelResponseRequest"""
    # pylint: disable=line-too-long
    client = get_model_armor_client()
    llm_resp_data = modelarmor_v1.DataItem()
    llm_resp_data.text = llm_response
    request = modelarmor_v1.SanitizeModelResponseRequest(
        name=gcp_model_armor_template,
        model_response_data=llm_resp_data
    )
    response = client.sanitize_model_response(request)
    res = parse_model_filter_results(response.sanitization_result.filter_results)

    resp = {}
    resp['filter_match_state'] = response.sanitization_result.filter_match_state
    resp['error_code'] = response.sanitization_result.sanitization_metadata.error_code
    resp['error_msg'] = response.sanitization_result.sanitization_metadata.error_message
    resp['filter_result'] = res
    resp['sanitization_result'] = modelarmor_v1.SanitizationResult.to_json(response.sanitization_result)
    return resp

def sanitized_user_prompts_with_model_armor(prompt):
    # pylint: disable=line-too-long
    """Sanitizes the user prompt before submitting it to the LLM using ModelArmor's SanitizeUserPromptRequest"""
    client = get_model_armor_client()
    user_prompt_data = modelarmor_v1.DataItem()
    user_prompt_data.text = prompt
    request = modelarmor_v1.SanitizeUserPromptRequest(
        name=gcp_model_armor_template,
        user_prompt_data=user_prompt_data
    )
    response = client.sanitize_user_prompt(request)
    res = parse_model_filter_results(response.sanitization_result.filter_results)

    resp = {}
    resp['filter_match_state'] = response.sanitization_result.filter_match_state
    resp['error_code'] = response.sanitization_result.sanitization_metadata.error_code
    resp['error_msg'] = response.sanitization_result.sanitization_metadata.error_message
    resp['filter_result'] = res
    resp['sanitization_result'] = modelarmor_v1.SanitizationResult.to_json(response.sanitization_result)
    return resp

# Model selection module to be used within the Streamlit App layout.
def sidebar_model_selection():
    """Configures Model Selection Dropdown for Streamlit sidebar"""
    st.subheader("Model")

    models = load_models()
    model_options = {model['name']: (model['name'], model['description']) for model in models}
    model_identifier = st.selectbox(
        "Choose a LLM model",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x][0]
    )

    if model_identifier:
        st.session_state['selected_model'] = model_identifier
        st.write(model_options[model_identifier][1])

        col2 = st.columns(2, gap="small")
        with col2:
            if st.button("Pull model", use_container_width=True):
                pull_model()

def sidebar_model_armor_protection_options():
    """Configures the selection boxes to integrated Model Armor"""
    # pylint: disable=line-too-long
    st.subheader("Model Armor Protections")
    st.checkbox("Sanitize User Prompts with Model Armor", False, key="ml_armor_user_prompt_protection")
    st.checkbox("Sanitize LLM Responses with Model Armor", False, key="ml_armor_llm_resp_protection")

def add_chat_message(msg):
    """Add Chat Bot Message to History"""
    st.chat_message("ai").write(msg)
    st.session_state["chat_history"] += [AIMessage(msg)]

def add_human_message(msg):
    """Add Human Message to History"""
    st.chat_message("user").write(msg)
    st.session_state["chat_history"] += [HumanMessage(msg)]

def parse_model_filter_results(filtered_results: MutableMapping[str, modelarmor_v1.FilterResult]):
    """Parses the Model Armor Results to give more concrete results"""
    # pylint: disable=line-too-long
    # pylint: disable=too-many-statements
    #if not filtered_results:
    result = ""
    for k in filtered_results:
        if filtered_results[k].csam_filter_filter_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
            result = "Child Safety Abuse Material Detected"
        if filtered_results[k].malicious_uri_filter_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
            result = "Malicious URI Detected"
        if filtered_results[k].virus_scan_filter_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
            result = "Virus Detected"
        if filtered_results[k].sdp_filter_result.inspect_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
            result = "Sensitive Data Inspection Detected"
        if filtered_results[k].sdp_filter_result.deidentify_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
            result = "Sensitive Data DeIdentification Detected"
        if filtered_results[k].rai_filter_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
            for i in filtered_results[k].rai_filter_result.rai_filter_type_results:
                if filtered_results[k].rai_filter_result.rai_filter_type_results[i].match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
                    result = "Responsible AI Detected - " + i
        if filtered_results[k].pi_and_jailbreak_filter_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
            result = "Prompt injection and jailbreak detection"
    return result

def run():
    """Start streamlit"""
    # pylint: disable=line-too-long
    # pylint: disable=too-many-statements
    init()
    with st.sidebar:
        st.header("Preferences")
        sidebar_model_selection()
        sidebar_model_armor_protection_options()

    init_chat_history()
    prompt = st.chat_input("Add your prompt..")
    selected_model = st.session_state["selected_model"]
    print("Selected model: ", selected_model)

    ml_armor_user_prompt_protection = st.session_state["ml_armor_user_prompt_protection"]
    ml_armor_llm_resp_protection = st.session_state["ml_armor_llm_resp_protection"]

    print("Protect user prompts with model armor:", ml_armor_user_prompt_protection)
    print("Protect llm responses with model armor:", ml_armor_llm_resp_protection)

    llm = get_llm()

    if prompt:
        st.chat_message("user").write(prompt)
        add_human_message(prompt)
        if ml_armor_user_prompt_protection is True:
            resp = sanitized_user_prompts_with_model_armor(prompt)
            if bool(resp):
                if resp.get('filter_match_state','NO_KEY') == modelarmor_v1.FilterMatchState.MATCH_FOUND:
                    filter_type = resp.get('filter_result', '')
                    output = resp.get('error_msg', 'Sorry I am unable to provide a response for this question due to the nature of the content.')
                    sanitization_result = resp.get('sanitization_result','')
                    # Convert to Python object
                    parsed_data = json.loads(sanitization_result)
                    # Pretty print with indentation
                    pretty_json = json.dumps(parsed_data, indent=4)
                    add_chat_message(output + " - " + filter_type + "\n\r" + pretty_json)
                else:
                    output = llm.stream(prompt)
                    with st.chat_message("ai"):
                        ai_message = st.write_stream(output)
                    st.session_state["chat_history"] += [AIMessage(ai_message)]
            else:
                output = llm.stream(prompt)
                with st.chat_message("ai"):
                    ai_message = st.write_stream(output)
                st.session_state["chat_history"] += [AIMessage(ai_message)]

        elif ml_armor_llm_resp_protection is True:
            output = llm.invoke(prompt)
            print("LLM Content: " + output.content)
            resp = sanitize_llm_responses_with_model_armor(output.content)
            if bool(resp):
                if resp.get('filter_match_state','NO_KEY') == modelarmor_v1.FilterMatchState.MATCH_FOUND:
                    filter_type = resp.get('filter_result', '')
                    output = resp.get('error_msg', 'Sorry I am unable to provide a response for \n' +
                    ' this question due to the nature of the content.')
                    sanitization_result = resp.get('sanitization_result','')
                    # Convert to Python object
                    parsed_data = json.loads(sanitization_result)
                    # Pretty print with indentation
                    pretty_json = json.dumps(parsed_data, indent=4)
                    add_chat_message(output + " - " + filter_type + "\n\r" + pretty_json)
                else:
                    add_chat_message(output.content)
            else:
                add_chat_message(output.content)
        else:
            output = llm.stream(prompt)
            with st.chat_message("ai"):
                ai_message = st.write_stream(output)
            st.session_state["chat_history"] += [AIMessage(ai_message)]

if __name__ == "__main__":
    run()
