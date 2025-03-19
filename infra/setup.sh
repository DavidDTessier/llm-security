#!/bin/bash

## Requires the modelarmor.admin and modelarmor.floorSettingsAdmin
# Current Supported Regions
#    Iowa (us-central1 region): modelarmor.us-central1.rep.googleapis.com
#    Northern Virginia (us-east4 region): modelarmor.us-east4.rep.googleapis.com
#    Oregon (us-west1 region): modelarmor.us-west1.rep.googleapis.com
#    Netherlands (europe-west4 region): modelarmor.europe-west4.rep.googleapis.com

## Read Configuration
source .config

echo $GCP_Project_ID
echo $GCP_Model_Armor_API_Region
echo $GCP_Model_Armor_Template_Region
echo $GCP_Service_Account_Name
echo $Model_Armor_Template_Name

model_armor_url=""

if [ $GCP_Model_Armor_API_Region = "global" ]; then
    model_armor_url="modelarmor.googleapis.com"
else
    model_armor_url="modelarmor.$GCP_Model_Armor_API_Region.rep.googleapis.com"
fi

echo $model_armor_url

## Authenticae
gcloud auth login

# Set Project
gcloud config set project $GCP_Project_ID

# Set the API Endpoint for the Model Armor Service
gcloud config set api_endpoint_overrides/modelarmor "https://$model_armor_url/"

# Enable Model Armor on the GCP Project
gcloud services enable modelarmor.googleapis.com --project $GCP_Project_ID

# create the model armor template
gcloud model-armor templates create $Model_Armor_Template_Name --location $GCP_Model_Armor_Template_Region \
    --project $GCP_Project_ID --malicious-uri-filter-settings-enforcement=enabled \
    --rai-settings-filters=./responsible-ai-settings.json \
    --basic-config-filter-enforcement=enabled --pi-and-jailbreak-filter-settings-enforcement=enabled \
    --pi-and-jailbreak-filter-settings-confidence-level=medium-and-above \
    --template-metadata-custom-llm-response-safety-error-code=798 \
    --template-metadata-custom-llm-response-safety-error-message="The content returned from the LLM has been reviewed for harmful or explicit content. Unfortunate we cannot display this content." \
    --template-metadata-custom-prompt-safety-error-code=799 \
    --template-metadata-custom-prompt-safety-error-message="Unfortunately I cannot process that question, please refine your request and avoid any explicit content." \
    --template-metadata-ignore-partial-invocation-failures --template-metadata-log-operations \
    --template-metadata-log-sanitize-operations

# create service account to use in the application
gcloud iam service-accounts create $GCP_Service_Account_Name --display-name="Demo Model Armor Service Account"

SRVC_ACCT="$GCP_Service_Account_Name@$GCP_Project_ID.iam.gserviceaccount.com"

# add Iam for ModelArmor User to the SA
gcloud projects add-iam-policy-binding $GCP_Project_ID --member="serviceAccount:$SRVC_ACCT" --role="roles/modelarmor.user"

# Generate a Service Account Key for the SA
gcloud iam service-accounts keys create key.json --iam-account=$SRVC_ACCT