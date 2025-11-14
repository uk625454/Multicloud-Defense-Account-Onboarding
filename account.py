from base import Base, Controller
import logging

logger = logging.getLogger()

class Account(Base):
    def __init__(self, controller: Controller) -> None:
        self.controller = controller
        self.api_base = "cspaccount"

    def list(self,
             get_count: bool = False,
             page_size: int = 0,
             start_page_token: str = "") -> dict:
        api_url = f"{self.api_base}/list"
        form_data = {}
        if get_count:
            form_data["getCount"] = True
        else:
            if page_size and start_page_token:
                form_data["pageInfo"] = {
                    "pageSize": page_size,
                    "startPageToken": start_page_token
                }
        resp = self.controller.post(api_url, form_data)
        return resp.json()

    def get_count(self) -> int:
        """
        api to get CSP Account Count
        returns number of account
        """
        return int(self.list(get_count=True).get("count", 0))

    def list_iter(self,
                  page_size: int = 100) -> list:
        """
        iterator to list csp account , it's highly recommended to use list iterator to get list of account in scaled env
        kwargs:
        :page_size: page size integer
        returns list of cspAccounts
        """
        csp_account_count = self.get_count()
        current_page_token = 0
        while current_page_token < csp_account_count:
            resp = self.list(page_size=page_size,
                            start_page_token=str(current_page_token))
            current_page_token = int(resp["pageInfo"]["nextPageToken"])
            yield resp["cspAccounts"]

    def find_aws_account_name_by_number(self, account_number):
        """
        api to find account name by account number
        args:
            :account_number: aws account number
        returns account name if found else returns empty string
        """
        account_name = ""
        for csp_accounts in self.list_iter():
            for csp_account in csp_accounts:
                if csp_account["csp"] == "AWS":
                    csp_account_details = self.read(csp_account_name=csp_account["name"])
                    if csp_account_details["accountNumber"] == account_number:
                        return csp_account_details["name"]
        return account_name

    def find_azure_account_name_by_subscription_id(self, subscription_id):
        """
        api to find azure account name by subscription id
        args:
            :subscription_id: azure subscription id
        returns account name if found else returns empty string
        """
        account_name = ""
        for csp_accounts in self.list_iter():
            for csp_account in csp_accounts:
                if csp_account["csp"] == "AZURE":
                    csp_account_details = self.read(csp_account_name=csp_account["name"])
                    if csp_account_details["subscriptionID"] == subscription_id:
                        return csp_account_details["name"]
        return account_name

    def find_gcp_account_name_by_project_id(self, project_id):
        """
        api to find gcp account name by subscription id
        args:
            :project_id: gcp project id
        returns account name if found else returns empty string
        """
        account_name = ""
        for csp_accounts in self.list_iter():
            for csp_account in csp_accounts:
                if csp_account["csp"] == "GCP":
                    csp_account_details = self.read(csp_account_name=csp_account["name"])
                    if csp_account_details["gcpProjectID"] == project_id:
                        return csp_account_details["name"]
        return account_name

    def read(self, csp_account_name: str) -> dict:
        api_url = f"{self.api_base}/get"
        form_data = {"name": csp_account_name}

        # Return the AO stanza from the Controller or an empty dictionary
        try:
            resp = self.controller.post(api_url, form_data)
        except Exception:
            return {}
        return resp.json()

    def delete(self, csp_account_name: str) -> bool:
        api_url = f"{self.api_base}/delete"

        form_data = {"name": csp_account_name}
        self.controller.post(api_url, form_data)
        return True

    def _create(self, csp_account_form_data: dict) -> dict:
        api_url = f"{self.api_base}/create"

        if not self.read(csp_account_form_data["name"]):
            resp = self.controller.post(api_url, csp_account_form_data)
            return resp.json()

        return {}

    def create_aws(self,
                    name: str,
                    aws_iam_role: str,
                    account_number: str,
                    aws_iam_role_external_id: str,
                   aws_inventory_role: str = ""
                   ) -> dict:
        """
        api to onboard aws csp account
        args:
            :name: csp account name
            :aws_iam_role: aws iam role
            :account_number: aws account number
            :aws_iam_role_external_id: aws iam role external id
        kwargs:
            :aws_inventory_role: aws inventory role
        """
        form_data = {
            "name": name,
            "credentialsType": "AWS_IAM_ROLE",
            "csp": "AWS",
            "awsIAMRole": aws_iam_role,
            "accountNumber": account_number,
            "awsIAMRoleExternalID": aws_iam_role_external_id
        }
        if aws_inventory_role:
            form_data["awsInventoryIAMRole"] = aws_inventory_role
        return self._create(csp_account_form_data=form_data)

    def create_azure(self,
                    name: str,
                    application_id: str,
                    tenant_id: str,
                    secret: str,
                    subscription_id: str) -> dict:
        """
        api to onboard azure csp account
        args:
            :name: csp account name
            :application_id: azure application id
            :secret: azure application secret
            :tenant_id: azure tenant id
            :subscription_id: azure subscription id number
        """
        form_data = {
            "name": name,
            "credentialsType": "AZURE_CLIENT_CREDENTIALS",
            "csp": "AZURE",
            "applicationID": application_id,
            "accountNumber": tenant_id,
            "clientSecret": secret,
            "subscriptionID": subscription_id
        }
        return self._create(csp_account_form_data=form_data)

    def create_gcp(self,
                    name: str,
                    gcp_client_email: str,
                    gcp_project_id: str,
                    private_key: str) -> dict:
        """
        api to onboard gcp csp account
        args:
            :name: csp account name
            :gcp_client_email: gcp client email id
            :gcp_project_id: gcp project id
            :private_key: gcp private key
        """
        form_data = {
            "name": name,
            "credentialsType": "GCP_SERVICE_ACCOUNT",
            "csp": "GCP",
            "gcpClientEmail": gcp_client_email,
            "gcpProjectID": gcp_project_id,
            "privateKey": private_key
        }
        return self._create(csp_account_form_data=form_data)

    def _update(self,
                name: str,
                new_csp_data: dict) -> dict:
        """
        internal api to update csp account
        args:
            :name: csp account name
            :new_csp_data: csp data dict
        :return:
        """
        api_url = f"{self.api_base}/update"

        current_csp_data = self.read(name)
        if not current_csp_data:
            raise Exception(f"Unable to find csp account {name}")

        for parameter in new_csp_data:
            current_csp_data[parameter] = new_csp_data[parameter]

        resp = self.controller.post(api_url=api_url,
                             form_data=current_csp_data)
        return resp.json()

    def update_aws(self,
                   name: str,
                   aws_iam_role: str = "",
                   aws_inventory_role: str = "") -> dict:
        """
        api to update aws csp account
        args:
            :name: csp account name
        kwargs:
            :aws_iam_role: aws iam role
            :aws_inventory_role: aws inventory role
        """
        form_data = {}
        if aws_iam_role:
            form_data["awsIAMRole"] = aws_iam_role
        if aws_inventory_role:
            form_data["awsInventoryIAMRole"] = aws_inventory_role
        return self._update(name=name,
                            new_csp_data=form_data)

    def update_azure(self,
                     name: str,
                     application_id: str = "",
                     secret: str = "") -> dict:
        """
        api to update azure csp account
        args:
            :name: csp account name
        kwargs:
            :application_id: azure application/client id
            :secret: azure application/client secret
        """
        form_data = {}
        if application_id:
            form_data["applicationID"] = application_id
        if secret:
            form_data["clientSecret"] = secret
        return self._update(name=name,
                            new_csp_data=form_data)

    def update_gcp(self,
                   name: str,
                   gcp_client_email: str = "",
                   private_key: str = "") -> dict:
        """
        api to update gcp csp account
        args:
            :name: csp account name
        kwargs:
            :gcp_client_email: gcp client email
            :private_key: gcp private key
        """
        form_data = {}
        if gcp_client_email:
            form_data["gcpClientEmail"] = gcp_client_email
        if private_key:
            form_data["privateKey"] = private_key
        return self._update(name=name,
                            new_csp_data=form_data)