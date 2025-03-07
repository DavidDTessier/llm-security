#!/bin/bash

## Requires the modelarmor.admin and modelarmor.floorSettingsAdmin
# Current Supported Regions
#    Iowa (us-central1 region): modelarmor.us-central1.rep.googleapis.com
#    Northern Virginia (us-east4 region): modelarmor.us-east4.rep.googleapis.com
#    Oregon (us-west1 region): modelarmor.us-west1.rep.googleapis.com
#    Netherlands (europe-west4 region): modelarmor.europe-west4.rep.googleapis.com

## Read Configuration
source .config

echo $GCP_Org_ID
echo $GCP_Project_ID
echo $GCP_Org_Domain
echo $GCP_Region

model_armor_url=""

if [ $GCP_Region = "global" ]; then
    model_armor_url="modelarmor.googleapis.com"
else
    model_armor_url="modelarmor.$GCP_Region.rep.googleapis.com"
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