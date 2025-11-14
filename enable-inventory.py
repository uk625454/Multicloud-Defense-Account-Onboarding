import sys
import time
from base import Controller
from inventory import Inventory
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
VALTIX_ACCOUNT_NAME = "<mutlicloudDefenseTenantID>"

def enable_inventory_flow(name: str, region: str):
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

    inventory = Inventory(valtix_controller)

    # Set inventory monitoring
    response = inventory.set_inventory_monitoring(
        csp_account_name=name,
        monitoring_state=True,
        region=region,
        refresh_inventory=True,
        refresh_inventory_interval_ns="3600000000000"
    ) 

if __name__ == "__main__":
    #friendly name that was used to onboard AWS account into Multicloud Defense controller
    name = "<aws_account_name>"
    region = "us-west-1" #example syntax, replace with appropriate region

    #this function has to be called each time a new region needs to be added for inventory purposes
    enable_inventory_flow(name, region)
    