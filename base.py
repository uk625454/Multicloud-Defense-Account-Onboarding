# from functools import lru_cache
# from retrying import retry
from timeit import default_timer as timer
from common import keepalive_session

# import ipaddress
import json
import logging
import requests

# import typing

logger = logging.getLogger()


class Base(object):
    def __str__(self) -> str:
        return json.dumps(self, default=self.convert_to_dict, indent=2, sort_keys=True)

    def convert_to_dict(self, obj: dict) -> dict:
        dict_copy = obj.__dict__.copy()
        excluded = ["controller", "account"]
        for k, v in obj.__dict__.items():
            if k in excluded:
                dict_copy.pop(k)
            if not v:
                dict_copy.pop(k)
        return dict_copy


class Controller(Base):
    def __init__(self, id: str, secret: str, acctname: str, url: str, verify_ssl: bool = True) -> None:
        self.apikeyid = id
        self.apikeysecret = secret
        self.acctname = acctname
        self.common_api_stanza = {
            "common": {"acctName": self.acctname, "source": "RESTAPI", "clientVersion": ""}
        }
        self.api_baseurl = url
        self.verify_ssl = verify_ssl
        self.token = None
        self.bearer = None
        self.version = None
        self.name = None
        self.upgrade_status = None

        self.https_session = keepalive_session()

    @property
    def apikeyid(self) -> str:
        return self._apikeyid

    @apikeyid.setter
    def apikeyid(self, apikeyid: str) -> None:
        if not isinstance(apikeyid, str):
            raise Exception(f"{apikeyid} is not a valid string")
        self._apikeyid = apikeyid

    @property
    def apikeysecret(self) -> str:
        return self._apikeysecret

    @apikeysecret.setter
    def apikeysecret(self, apikeysecret: str) -> None:
        if not isinstance(apikeysecret, str):
            raise Exception(f"{apikeysecret} is not a valid string")
        self._apikeysecret = apikeysecret

    @property
    def acctname(self) -> str:
        return self._acctname

    @acctname.setter
    def acctname(self, acctname: str) -> None:
        if not isinstance(acctname, str):
            raise Exception(f"{acctname} is not a valid string")
        self._acctname = acctname

    @property
    def verify_ssl(self) -> bool:
        return self._verify_ssl

    @verify_ssl.setter
    def verify_ssl(self, verify_ssl: bool) -> None:
        if not isinstance(verify_ssl, bool):
            raise Exception(f"{verify_ssl} is not a valid bool")
        self._verify_ssl = verify_ssl

    # @retry(wait_exponential_multiplier=1000, stop_max_delay=10000)
    def get(self, api_url: str, url_data: dict, timeout: int = 900) -> requests.Response:
        start_time = timer()

        # url = f"?action={action}"
        # for k, v in url_data.items():
        #    url += f"&{k}={v}"
        # Security: Log here so we don't log the CID
        logger.info(f"{api_url}")

        resp = self.https_session.get(
            self.api_baseurl + api_url, headers=self.bearer, verify=self.verify_ssl, timeout=timeout, stream=False
        )
        end_time = timer()
        logger.info(f"{api_url} action API Response Time: {(end_time - start_time)}")
        logger.info(f"{api_url} action {resp.json()}")
        if "error" in resp.json().keys() or resp.status_code >= 400:
            raise Exception(resp.json())
        return resp

    # s@retry(wait_exponential_multiplier=1000, stop_max_delay=10000)
    def post(
        self,
        api_url: str,
        form_data: dict,
        timeout: int = 900,
        no_log_req: bool = False,
        no_log_resp: bool = False,
        files: list = [],
    ) -> requests.Response:
        start_time = timer()

        # PCSS-4623 override logging if loglevel == DEBUG
        if logging.getLevelName(logger.level) == "DEBUG":
            logger.debug("overriding no_logging parameters for DEBUGGING")
            no_log_req = False
            no_log_resp = False

        # add common data
        form_data = dict(self.common_api_stanza, **form_data)

        if not no_log_req:
            logger.info(f"{api_url} request: {form_data}")
        else:
            logger.warning(f"{api_url} request surpressed")

        resp = self.https_session.post(
            f"{self.api_baseurl}/{api_url}",
            headers=self.bearer,
            json=form_data,
            verify=self.verify_ssl,
            timeout=timeout,
            files=files,
            stream=False,
        )

        end_time = timer()
        logger.info(f"{api_url} API Response Time: {(end_time - start_time)}")

        if not no_log_resp:
            logger.info(f"{api_url} response {resp.json()}")
        else:
            logger.warning(f"{api_url} response surpressed")

        if "error" in resp.json().keys() or resp.status_code >= 400:
            raise Exception(resp.json())
        return resp

    def login(self) -> bool:
        api_url = "user/gettoken"
        form_data = {
            "apiKeyID": self.apikeyid,
            "apiKeySecret": self.apikeysecret,
        }

        resp = self.post(api_url, form_data, no_log_req=True, no_log_resp=True)
        self.token = resp.json()["accessToken"]
        self.bearer = {"Authorization": f"Bearer {self.token}"}
        return True