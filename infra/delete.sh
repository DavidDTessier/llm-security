## Read Configuration
source .config

echo $GCP_Project_ID
echo $GCP_Model_Armor_API_Region
echo $GCP_Model_Armor_Template_Region
echo $GCP_Service_Account_Name
echo $Model_Armor_Template_Name

## Authenticate
gcloud auth login

# delete model armor template
gcloud model-armor templates delete $Model_Armor_Template_Name --location=$GCP_Model_Armor_API_Region

SRVC_ACCT="$GCP_Service_Account_Name@$GCP_Project_ID.iam.gserviceaccount.com"

# Delete the service account
gcloud iam service-accounts delete $SRVC_ACCT
