import sys
import time
from base import Controller
from account import Account
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

#Login to SCC -> Platform Menu -> Multicloud Defense -> System and Accounts -> API Keys
#Role of API Key -> admin_rw
#Download API Key JSON file
#In the file, you will find restAPIServer, apiKeyID, apiKeySecret
VALTIX_CONTROLLER_URL = "https://<restAPIServer>/api/v1"
VALTIX_API_KEY_ID = "<apiKeyID>"
VALTIX_API_KEY_SECRET = "<apiKeySecret>"
#MCD Controller Tenant Name
#Login to SCC -> Platform Menu -> Multicloud Defense -> System and Accounts -> System Information -> Tenant ID
VALTIX_ACCOUNT_NAME = "<multicloudDefenseTenantID>"

def aws_flow(name: str, account_number: str, aws_iam_role: str, aws_inventory_role: str, aws_iam_role_external_id: str):
    logger.info(f"Initialize Valtix Controller")
    valtix_controller = Controller(url=VALTIX_CONTROLLER_URL,
                          id=VALTIX_API_KEY_ID,
                          secret=VALTIX_API_KEY_SECRET,
                          acctname=VALTIX_ACCOUNT_NAME)

    logger.info(f"logging into controller")
    if valtix_controller.login():
        logger.info(f"bearer token is generated successfully")
    else:
        logger.error(f"login failed")
        sys.exit(f"controller login failed")

    logger.info(f"create valtix account object")
    valtix_acct = Account(valtix_controller)

    logger.info(f"onboarding aws account")
    
    valtix_acct.create_aws(name=name,
                          account_number=account_number,
                          aws_iam_role=aws_iam_role,
                          aws_inventory_role=aws_inventory_role,
                          aws_iam_role_external_id=aws_iam_role_external_id)

if __name__ == "__main__":
    #Friendly name of aws account (account will be shown on Multicloud Defense Controller with this name)
    name = "<aws_account_name>"
    #Account number, controller role ARN, and inventory role ARN are outputs of the CFT
    account_number = "<aws_account_number"
    #controller role
    aws_iam_role = "<controller_role_arn>"
    aws_inventory_role = "<inventory_role_arn>"
    #Instructions provided in email on how to generate and re-use the same external ID for onboarding all accounts
    aws_iam_role_external_id = "<external_id>"

    aws_flow(name, account_number, aws_iam_role, aws_inventory_role, aws_iam_role_external_id)
    