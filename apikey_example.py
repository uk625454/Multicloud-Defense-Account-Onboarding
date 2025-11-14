import sys
from base import Controller
from model.user import User
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


VALTIX_CONTROLLER_URL = ""
VALTIX_API_KEY_ID = ""
VALTIX_API_KEY_SECRET = ""
VALTIX_ACCOUNT_NAME = ""

def apikey_example():
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

    user = User(valtix_controller)

    logger.info(f"list api keys")
    user.list_apikeys()

    apikey_name = "devkey"
    logger.info(f"generate api key")
    user.create_apikey(name=apikey_name,
                       role="admin_rw",
                       email="hardik@valtix.com",
                       days=180)

    logger.info(f"get api key")
    user.get_apikey(name=apikey_name)

    logger.info(f"delete api key")
    user.delete_apikey(name=apikey_name)

if __name__=="__main__":
    apikey_example()