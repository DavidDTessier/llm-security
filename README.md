# Securing AI workloads withe Model Armor

## Overview

The following repository showcases a sample ChatBot that leverages Ollama + Langchain for conversational chat with a Chatbot and allows for options to integrate with Google Cloud's Model Armor for security and responsible AI safeguards and protections.

![Model Armor Architecture](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*3yQQ6SiSfSXkJCl0PxLHzQ.png)

(image source from https://medium.com/google-cloud/google-cloud-model-armor-6242dbae90b8)

## Model Armor

Model Armor is a fully managed service provided by Google Cloud Platform that offers capabilities to enhance the safety and security of AI applications. By leveraging the concepts described previously in this post, Model Armor screens LLM prompts and responses for various types of security and safety risks. 

GCP's Model Armor offers the following core features:
* **Universal Model and Cloud Compatibility**: 
    * Operates independently of specific AI models or cloud platforms,enabling seamless integration across multi-cloud and multi-model environments.
* **Centralized Policy Management**:
    * Provides a unified platform for managing and enforcing security and safety policies across all deployed AI models.
* **API-Driven Integration**:
    * Offers a public REST API for direct integration of prompt and response screening into applications, supporting diverse deployment architectures.
* **Granular Access Control**:
    * Implements Role-Based Access Control (RBAC) to precisely manage user permissions and access levels.
* **Low-Latency Regional Endpoints**:
    * Delivers API access through regional endpoints to minimize latency and optimize performance.
* **Global Availability**:
    * Deployed across multiple regions in the United States and Europe for broad accessibility.
* **Security Command Center Integration**:
    * Seamlessly integrates with Security Command Center, allowing for centralized visibility, violation detection, and remediation.
* **Enhanced Safety and Security**:
    * **_Comprehensive Content Safety Filters_**:
        * Includes filters for detecting and mitigating harmful content, such as sexually explicit material, dangerous content, harassment, and hate speech.
    * **_Advanced Threat Detection_**:
        * Detects and prevents prompt injection and jailbreak attacks, safeguarding AI models from manipulation.
* **Detects Malicious URLs within prompts and responses**.
    * **_Integrated Data Loss Prevention (DLP)_**:
        * Leverages Google Cloud's Sensitive Data Protection to discover, classify, and protect sensitive data (e.g., PII, intellectual property), preventing unauthorized disclosure.
* **PDF Content Screening**:
    * Supports the screening of text within PDF documents, for malicious content.

## Setup

1. Update the `.config` file under the `infra` folder to set the necessary values required to configure Model Armor in GCP, like so:

```
GCP_Project_ID={PROJECT_ID}
GCP_Org_ID={ORG_ID}
GCP_Model_Armor_API_Region=us-central1
GCP_Model_Armor_Template_Region=us-central1
GCP_Service_Account_Name=demo-mdl-armor-sa
Model_Armor_Template_Name=demo-mdl-armor
```
2. Next, run the `setup.sh` script under the `infra` folder to provision model armor apis, template, and create the service account

3. Once the necessary resources are provisioned, up the `creds.json` file with the generated `key.json` from the script.

4. Now your ready to run the chat app, you have two options, run the `docker-compose.yaml` to deploy the containers locally, or just run the streamlit app locally

### Local Run 

**Using Streamlit**
To run the streamlit app local, you need to make sure you have Ollama installed, see [Ollama Site](https://ollama.com/) for details on how to install on your machine.  

Create a python environment using the following command(s): 
```
pip install virtualenv
python3.8 -m venv env
```

Activate said python environment: `source env/bin/activate`

Now run the following command to install the python dependencies: `cd app && pip -install -r requirements.txt`

Once all the dependencies a install now you can run the app: `streamlit run app.py`

**Run as Containers**

Make sure to either have [Docker](https://www.docker.com/products/docker-desktop/) or [Podman](https://podman.io/) man installed, this set of steps assumes we are using Podman to host the containers.

Run the command `podman compose --file docker-compose.yaml up` to setup the containers

Once you have with of the options up and running navigate to `http://localhost:8501` to start using the app.

### Live Demo
https://github.com/user-attachments/assets/6b6e1306-b5ff-418e-835b-2a7f4ef418a6



