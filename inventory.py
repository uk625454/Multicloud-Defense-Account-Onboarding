from base import Base, Controller
import logging

logger = logging.getLogger()


class Inventory(Base):
    def __init__(self, controller: Controller) -> None:
        self.controller = controller
        self.api_base = "inventory"

    def set_inventory_monitoring(self,
                                 csp_account_name: str,
                                 monitoring_state: bool,
                                 region: str,
                                 refresh_inventory: bool = True,
                                 refresh_inventory_interval_ns: str = "3600000000000") -> dict:
        """
        API to set inventory monitoring for a CSP account
        args:
            :csp_account_name: CSP account name
            :monitoring_state: Enable or disable monitoring (True/False)
            :region: Region to monitor
        kwargs:
            :refresh_inventory: Whether to refresh inventory (default: True)
            :refresh_inventory_interval_ns: Refresh interval in nanoseconds (default: 3600000000000 = 1 hour)
        returns: API response as dict
        """
        api_url = f"{self.api_base}/set_inventory_monitoring"
        form_data = {
            "cspAcctName": csp_account_name,
            "monitoringState": monitoring_state,
            "region": region,
            "refreshInventory": refresh_inventory,
            "refreshInventoryIntervalNS": refresh_inventory_interval_ns
        }
        resp = self.controller.post(api_url, form_data)
        return resp.json() 