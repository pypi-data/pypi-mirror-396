import httpx
import base64
import urllib.parse
from typing import Any, Optional, Dict, List
from typing_extensions import TypedDict 
from typing import TypedDict

# --- Models ---



class MetrcClient:
    def __init__(self, base_url: str, vendor_key: str, user_key: str, client: Optional[httpx.Client] = None):
        self.base_url = base_url.rstrip('/')
        self.vendor_key = vendor_key
        self.user_key = user_key
        self.client = client or httpx.Client()
        self.client.auth = (vendor_key, user_key)

    def _send(self, method: str, path: str, body: Any = None, query_params: Dict[str, Any] = None) -> Any:
        url = f"{self.base_url}{path}"
        response = self.client.request(method, url, json=body, params=query_params)
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    def sales_create_delivery_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Sales Delivery

        POST CreateDelivery V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records new sales delivery entries for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - WebApi Retail ID Read Write State (All or WriteOnly) - Required for RID only.
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write) - Required for RID only.

        POST CreateDelivery V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_retailer_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The DateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Retailer Delivery

        POST CreateDeliveryRetailer V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/retailer"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_retailer_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records retailer delivery data for a given License Number, including delivery destinations. Please note: The DateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - WebApi Retail ID Read Write State (All or WriteOnly) - Required for RID only.
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write) - Required for RID only.
          - Manage Retailer Delivery

        POST CreateDeliveryRetailer V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/retailer"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_retailer_depart_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Retailer Delivery

        POST CreateDeliveryRetailerDepart V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/retailer/depart"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_retailer_depart_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Processes the departure of retailer deliveries for a Facility using the provided License Number and delivery data.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - Manage Retailer Delivery

        POST CreateDeliveryRetailerDepart V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/retailer/depart"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_retailer_end_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The ActualArrivalDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Retailer Delivery

        POST CreateDeliveryRetailerEnd V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/retailer/end"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_retailer_end_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Ends retailer delivery records for a given License Number. Please note: The ActualArrivalDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - Manage Retailer Delivery

        POST CreateDeliveryRetailerEnd V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/retailer/end"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_retailer_restock_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The DateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Retailer Delivery

        POST CreateDeliveryRetailerRestock V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/retailer/restock"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_retailer_restock_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records restock deliveries for retailer facilities using the provided License Number. Please note: The DateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - Manage Retailer Delivery

        POST CreateDeliveryRetailerRestock V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/retailer/restock"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_retailer_sale_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Retailer Delivery

        POST CreateDeliveryRetailerSale V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/retailer/sale"
        return self._send("POST", path, body, query_params)

    def sales_create_delivery_retailer_sale_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records sales deliveries originating from a retailer delivery for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - WebApi Retail ID Read Write State (All or WriteOnly) - Required for RID only.
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write) - Required for RID only.

        POST CreateDeliveryRetailerSale V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/retailer/sale"
        return self._send("POST", path, body, query_params)

    def sales_create_receipt_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Sales

        POST CreateReceipt V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/receipts"
        return self._send("POST", path, body, query_params)

    def sales_create_receipt_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records a list of sales deliveries for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales (Write)
          - Industry/Facility Type/Consumer Sales or Industry/Facility Type/Patient Sales or Industry/Facility Type/External Patient Sales or Industry/Facility Type/Caregiver Sales
          - Industry/Facility Type/Advanced Sales
          - WebApi Sales Read Write State (All or WriteOnly)
          - WebApi Retail ID Read Write State (All or WriteOnly) - Required for RID only.
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write) - Required for RID only.

        POST CreateReceipt V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/receipts"
        return self._send("POST", path, body, query_params)

    def sales_create_transaction_by_date_v1(self, date: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        POST CreateTransactionByDate V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/transactions/{urllib.parse.quote(date)}"
        return self._send("POST", path, body, query_params)

    def sales_delete_delivery_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        DELETE DeleteDelivery V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def sales_delete_delivery_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Voids a sales delivery for a Facility using the provided License Number and delivery Id.
        
          Permissions Required:
          - Manage Sales Delivery

        DELETE DeleteDelivery V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def sales_delete_delivery_retailer_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Retailer Delivery

        DELETE DeleteDeliveryRetailer V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/retailer/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def sales_delete_delivery_retailer_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Voids a retailer delivery for a Facility using the provided License Number and delivery Id.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - Manage Retailer Delivery

        DELETE DeleteDeliveryRetailer V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/retailer/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def sales_delete_receipt_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        DELETE DeleteReceipt V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/receipts/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def sales_delete_receipt_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a sales receipt for a Facility using the provided License Number and receipt Id.
        
          Permissions Required:
          - Manage Sales

        DELETE DeleteReceipt V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/receipts/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def sales_get_counties_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetCounties V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/sales/v1/counties"
        return self._send("GET", path, body, query_params)

    def sales_get_counties_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Returns a list of counties available for sales deliveries.
        
          Permissions Required:
          - None

        GET GetCounties V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/sales/v2/counties"
        return self._send("GET", path, body, query_params)

    def sales_get_customertypes_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetCustomertypes V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/sales/v1/customertypes"
        return self._send("GET", path, body, query_params)

    def sales_get_customertypes_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Returns a list of customer types.
        
          Permissions Required:
          - None

        GET GetCustomertypes V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/sales/v2/customertypes"
        return self._send("GET", path, body, query_params)

    def sales_get_deliveries_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        GET GetDeliveriesActive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if sales_date_end is not None:
            query_params["salesDateEnd"] = sales_date_end
        if sales_date_start is not None:
            query_params["salesDateStart"] = sales_date_start
        path = f"/sales/v1/deliveries/active"
        return self._send("GET", path, body, query_params)

    def sales_get_deliveries_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Returns a list of active sales deliveries for a Facility, filtered by optional sales or last modified date ranges.
        
          Permissions Required:
          - View Sales Delivery
          - Manage Sales Delivery

        GET GetDeliveriesActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        if sales_date_end is not None:
            query_params["salesDateEnd"] = sales_date_end
        if sales_date_start is not None:
            query_params["salesDateStart"] = sales_date_start
        path = f"/sales/v2/deliveries/active"
        return self._send("GET", path, body, query_params)

    def sales_get_deliveries_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        GET GetDeliveriesInactive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if sales_date_end is not None:
            query_params["salesDateEnd"] = sales_date_end
        if sales_date_start is not None:
            query_params["salesDateStart"] = sales_date_start
        path = f"/sales/v1/deliveries/inactive"
        return self._send("GET", path, body, query_params)

    def sales_get_deliveries_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Returns a list of inactive sales deliveries for a Facility, filtered by optional sales or last modified date ranges.
        
          Permissions Required:
          - View Sales Delivery
          - Manage Sales Delivery

        GET GetDeliveriesInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        if sales_date_end is not None:
            query_params["salesDateEnd"] = sales_date_end
        if sales_date_start is not None:
            query_params["salesDateStart"] = sales_date_start
        path = f"/sales/v2/deliveries/inactive"
        return self._send("GET", path, body, query_params)

    def sales_get_deliveries_retailer_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Retailer Delivery

        GET GetDeliveriesRetailerActive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/retailer/active"
        return self._send("GET", path, body, query_params)

    def sales_get_deliveries_retailer_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Returns a list of active retailer deliveries for a Facility, optionally filtered by last modified date range
        
          Permissions Required:
          - View Retailer Delivery
          - Manage Retailer Delivery

        GET GetDeliveriesRetailerActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/sales/v2/deliveries/retailer/active"
        return self._send("GET", path, body, query_params)

    def sales_get_deliveries_retailer_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Retailer Delivery

        GET GetDeliveriesRetailerInactive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/retailer/inactive"
        return self._send("GET", path, body, query_params)

    def sales_get_deliveries_retailer_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Returns a list of inactive retailer deliveries for a Facility, optionally filtered by last modified date range
        
          Permissions Required:
          - View Retailer Delivery
          - Manage Retailer Delivery

        GET GetDeliveriesRetailerInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/sales/v2/deliveries/retailer/inactive"
        return self._send("GET", path, body, query_params)

    def sales_get_deliveries_returnreasons_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          -

        GET GetDeliveriesReturnreasons V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/returnreasons"
        return self._send("GET", path, body, query_params)

    def sales_get_deliveries_returnreasons_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Returns a list of return reasons for sales deliveries based on the provided License Number.
        
          Permissions Required:
          - Sales Delivery

        GET GetDeliveriesReturnreasons V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/sales/v2/deliveries/returnreasons"
        return self._send("GET", path, body, query_params)

    def sales_get_delivery_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        GET GetDelivery V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def sales_get_delivery_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a sales delivery record by its Id, with an optional License Number.
        
          Permissions Required:
          - View Sales Delivery
          - Manage Sales Delivery

        GET GetDelivery V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def sales_get_delivery_retailer_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Retailer Delivery

        GET GetDeliveryRetailer V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/retailer/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def sales_get_delivery_retailer_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a retailer delivery record by its ID, with an optional License Number.
        
          Permissions Required:
          - View Retailer Delivery
          - Manage Retailer Delivery

        GET GetDeliveryRetailer V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/retailer/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def sales_get_patient_registrations_locations_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          -

        GET GetPatientRegistrationsLocations V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/sales/v1/patientregistration/locations"
        return self._send("GET", path, body, query_params)

    def sales_get_patient_registrations_locations_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Returns a list of valid Patient registration locations for sales.
        
          Permissions Required:
          -

        GET GetPatientRegistrationsLocations V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/sales/v2/patientregistration/locations"
        return self._send("GET", path, body, query_params)

    def sales_get_paymenttypes_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        GET GetPaymenttypes V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/paymenttypes"
        return self._send("GET", path, body, query_params)

    def sales_get_paymenttypes_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Returns a list of available payment types for the specified License Number.
        
          Permissions Required:
          - View Sales Delivery
          - Manage Sales Delivery

        GET GetPaymenttypes V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/paymenttypes"
        return self._send("GET", path, body, query_params)

    def sales_get_receipt_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        GET GetReceipt V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/receipts/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def sales_get_receipt_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a sales receipt by its Id, with an optional License Number.
        
          Permissions Required:
          - View Sales
          - Manage Sales

        GET GetReceipt V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/receipts/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def sales_get_receipts_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        GET GetReceiptsActive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if sales_date_end is not None:
            query_params["salesDateEnd"] = sales_date_end
        if sales_date_start is not None:
            query_params["salesDateStart"] = sales_date_start
        path = f"/sales/v1/receipts/active"
        return self._send("GET", path, body, query_params)

    def sales_get_receipts_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Returns a list of active sales receipts for a Facility, filtered by optional sales or last modified date ranges.
        
          Permissions Required:
          - View Sales
          - Manage Sales

        GET GetReceiptsActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        if sales_date_end is not None:
            query_params["salesDateEnd"] = sales_date_end
        if sales_date_start is not None:
            query_params["salesDateStart"] = sales_date_start
        path = f"/sales/v2/receipts/active"
        return self._send("GET", path, body, query_params)

    def sales_get_receipts_external_by_external_number_v2(self, external_number: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Sales Receipt by its external number, with an optional License Number.
        
          Permissions Required:
          - View Sales
          - Manage Sales

        GET GetReceiptsExternalByExternalNumber V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/receipts/external/{urllib.parse.quote(external_number)}"
        return self._send("GET", path, body, query_params)

    def sales_get_receipts_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        GET GetReceiptsInactive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if sales_date_end is not None:
            query_params["salesDateEnd"] = sales_date_end
        if sales_date_start is not None:
            query_params["salesDateStart"] = sales_date_start
        path = f"/sales/v1/receipts/inactive"
        return self._send("GET", path, body, query_params)

    def sales_get_receipts_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Returns a list of inactive sales receipts for a Facility, filtered by optional sales or last modified date ranges.
        
          Permissions Required:
          - View Sales
          - Manage Sales

        GET GetReceiptsInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        if sales_date_end is not None:
            query_params["salesDateEnd"] = sales_date_end
        if sales_date_start is not None:
            query_params["salesDateStart"] = sales_date_start
        path = f"/sales/v2/receipts/inactive"
        return self._send("GET", path, body, query_params)

    def sales_get_transactions_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        GET GetTransactions V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/transactions"
        return self._send("GET", path, body, query_params)

    def sales_get_transactions_by_sales_date_start_and_sales_date_end_v1(self, sales_date_start: str, sales_date_end: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        GET GetTransactionsBySalesDateStartAndSalesDateEnd V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/transactions/{urllib.parse.quote(sales_date_start)}/{urllib.parse.quote(sales_date_end)}"
        return self._send("GET", path, body, query_params)

    def sales_update_delivery_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Sales Delivery

        PUT UpdateDelivery V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates sales delivery records for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Manage Sales Delivery

        PUT UpdateDelivery V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_complete_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        PUT UpdateDeliveryComplete V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/complete"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_complete_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Completes a list of sales deliveries for a Facility using the provided License Number and delivery data.
        
          Permissions Required:
          - Manage Sales Delivery

        PUT UpdateDeliveryComplete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/complete"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_hub_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Sales Delivery

        PUT UpdateDeliveryHub V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/hub"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_hub_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates hub transporter details for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Manage Sales Delivery, Manage Sales Delivery Hub

        PUT UpdateDeliveryHub V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/hub"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_hub_accept_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        PUT UpdateDeliveryHubAccept V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/hub/accept"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_hub_accept_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Accepts a list of hub sales deliveries for a Facility based on the provided License Number and delivery data.
        
          Permissions Required:
          - Manage Sales Delivery Hub

        PUT UpdateDeliveryHubAccept V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/hub/accept"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_hub_depart_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        PUT UpdateDeliveryHubDepart V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/hub/depart"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_hub_depart_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Processes the departure of hub sales deliveries for a Facility using the provided License Number and delivery data.
        
          Permissions Required:
          - Manage Sales Delivery Hub

        PUT UpdateDeliveryHubDepart V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/hub/depart"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_hub_verify_id_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        PUT UpdateDeliveryHubVerifyID V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/hub/verifyID"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_hub_verify_id_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Verifies identification for a list of hub sales deliveries using the provided License Number and delivery data.
        
          Permissions Required:
          - Manage Sales Delivery Hub

        PUT UpdateDeliveryHubVerifyID V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/hub/verifyID"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_retailer_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The DateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Retailer Delivery

        PUT UpdateDeliveryRetailer V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/deliveries/retailer"
        return self._send("PUT", path, body, query_params)

    def sales_update_delivery_retailer_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates retailer delivery records for a given License Number. Please note: The DateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - WebApi Retail ID Read Write State (All or WriteOnly) - Required for RID only.
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write) - Required for RID only.
          - Manage Retailer Delivery

        PUT UpdateDeliveryRetailer V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/deliveries/retailer"
        return self._send("PUT", path, body, query_params)

    def sales_update_receipt_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Sales

        PUT UpdateReceipt V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/receipts"
        return self._send("PUT", path, body, query_params)

    def sales_update_receipt_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates sales receipt records for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Manage Sales

        PUT UpdateReceipt V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/receipts"
        return self._send("PUT", path, body, query_params)

    def sales_update_receipt_finalize_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Finalizes a list of sales receipts for a Facility using the provided License Number and receipt data.
        
          Permissions Required:
          - Manage Sales

        PUT UpdateReceiptFinalize V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/receipts/finalize"
        return self._send("PUT", path, body, query_params)

    def sales_update_receipt_unfinalize_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Unfinalizes a list of sales receipts for a Facility using the provided License Number and receipt data.
        
          Permissions Required:
          - Manage Sales

        PUT UpdateReceiptUnfinalize V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v2/receipts/unfinalize"
        return self._send("PUT", path, body, query_params)

    def sales_update_transaction_by_date_v1(self, date: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        PUT UpdateTransactionByDate V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sales/v1/transactions/{urllib.parse.quote(date)}"
        return self._send("PUT", path, body, query_params)

    def sandbox_create_integrator_setup_v2(self, body: Any = None, user_key: Optional[str] = None) -> Any:
        """
        This endpoint is used to handle the setup of an external integrator for sandbox environments. It processes a request to create a new sandbox user for integration based on an external source's API key. It checks whether the API key is valid, manages the user creation process, and returns an appropriate status based on the current state of the request.
        
          Permissions Required:
          - None

        POST CreateIntegratorSetup V2
        """
        query_params = {}
        if user_key is not None:
            query_params["userKey"] = user_key
        path = f"/sandbox/v2/integrator/setup"
        return self._send("POST", path, body, query_params)

    def strains_create_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Strains

        POST Create V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/strains/v1/create"
        return self._send("POST", path, body, query_params)

    def strains_create_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new strain records for a specified Facility.
        
          Permissions Required:
          - Manage Strains

        POST Create V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/strains/v2"
        return self._send("POST", path, body, query_params)

    def strains_create_update_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Strains

        POST CreateUpdate V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/strains/v1/update"
        return self._send("POST", path, body, query_params)

    def strains_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Strains

        DELETE Delete V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/strains/v1/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def strains_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives an existing strain record for a Facility
        
          Permissions Required:
          - Manage Strains

        DELETE Delete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/strains/v2/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def strains_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Strains

        GET Get V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/strains/v1/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def strains_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Strain record by its Id, with an optional license number.
        
          Permissions Required:
          - Manage Strains

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/strains/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def strains_get_active_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Strains

        GET GetActive V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/strains/v1/active"
        return self._send("GET", path, body, query_params)

    def strains_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active strains for the current Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Strains

        GET GetActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/strains/v2/active"
        return self._send("GET", path, body, query_params)

    def strains_get_inactive_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive strains for the current Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Strains

        GET GetInactive V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/strains/v2/inactive"
        return self._send("GET", path, body, query_params)

    def strains_update_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing strain records for a specified Facility.
        
          Permissions Required:
          - Manage Strains

        PUT Update V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/strains/v2"
        return self._send("PUT", path, body, query_params)

    def items_create_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        NOTE: To include a photo with an item, first use POST /items/v1/photo to POST the photo, and then use the returned ID in the request body in this endpoint.
        
          Permissions Required:
          - Manage Items

        POST Create V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v1/create"
        return self._send("POST", path, body, query_params)

    def items_create_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates one or more new products for the specified Facility. NOTE: To include a photo with an item, first use POST /items/v2/photo to POST the photo, and then use the returned Id in the request body in this endpoint.
        
          Permissions Required:
          - Manage Items

        POST Create V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2"
        return self._send("POST", path, body, query_params)

    def items_create_brand_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates one or more new item brands for the specified Facility identified by the License Number.
        
          Permissions Required:
          - Manage Items

        POST CreateBrand V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2/brand"
        return self._send("POST", path, body, query_params)

    def items_create_file_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Uploads one or more image or PDF files for products, labels, packaging, or documents at the specified Facility.
        
          Permissions Required:
          - Manage Items

        POST CreateFile V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2/file"
        return self._send("POST", path, body, query_params)

    def items_create_photo_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        This endpoint allows only BMP, GIF, JPG, and PNG files and uploaded files can be no more than 5 MB in size.
        
          Permissions Required:
          - Manage Items

        POST CreatePhoto V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v1/photo"
        return self._send("POST", path, body, query_params)

    def items_create_photo_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        This endpoint allows only BMP, GIF, JPG, and PNG files and uploaded files can be no more than 5 MB in size.
        
          Permissions Required:
          - Manage Items

        POST CreatePhoto V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2/photo"
        return self._send("POST", path, body, query_params)

    def items_create_update_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        POST CreateUpdate V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v1/update"
        return self._send("POST", path, body, query_params)

    def items_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        DELETE Delete V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v1/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def items_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives the specified Product by Id for the given Facility License Number.
        
          Permissions Required:
          - Manage Items

        DELETE Delete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def items_delete_brand_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives the specified Item Brand by Id for the given Facility License Number.
        
          Permissions Required:
          - Manage Items

        DELETE DeleteBrand V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2/brand/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def items_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        GET Get V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v1/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def items_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves detailed information about a specific Item by Id.
        
          Permissions Required:
          - Manage Items

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def items_get_active_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        GET GetActive V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v1/active"
        return self._send("GET", path, body, query_params)

    def items_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Returns a list of active items for the specified Facility.
        
          Permissions Required:
          - Manage Items

        GET GetActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/items/v2/active"
        return self._send("GET", path, body, query_params)

    def items_get_brands_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        GET GetBrands V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v1/brands"
        return self._send("GET", path, body, query_params)

    def items_get_brands_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active item brands for the specified Facility.
        
          Permissions Required:
          - Manage Items

        GET GetBrands V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/items/v2/brands"
        return self._send("GET", path, body, query_params)

    def items_get_categories_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetCategories V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v1/categories"
        return self._send("GET", path, body, query_params)

    def items_get_categories_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of item categories.
        
          Permissions Required:
          - None

        GET GetCategories V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/items/v2/categories"
        return self._send("GET", path, body, query_params)

    def items_get_file_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a file by its Id for the specified Facility.
        
          Permissions Required:
          - Manage Items

        GET GetFile V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2/file/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def items_get_inactive_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        GET GetInactive V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v1/inactive"
        return self._send("GET", path, body, query_params)

    def items_get_inactive_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive items for the specified Facility.
        
          Permissions Required:
          - Manage Items

        GET GetInactive V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/items/v2/inactive"
        return self._send("GET", path, body, query_params)

    def items_get_photo_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        GET GetPhoto V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v1/photo/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def items_get_photo_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves an image by its Id for the specified Facility.
        
          Permissions Required:
          - Manage Items

        GET GetPhoto V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2/photo/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def items_update_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates one or more existing products for the specified Facility.
        
          Permissions Required:
          - Manage Items

        PUT Update V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2"
        return self._send("PUT", path, body, query_params)

    def items_update_brand_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates one or more existing item brands for the specified Facility.
        
          Permissions Required:
          - Manage Items

        PUT UpdateBrand V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/items/v2/brand"
        return self._send("PUT", path, body, query_params)

    def lab_tests_create_record_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateRecord V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/labtests/v1/record"
        return self._send("POST", path, body, query_params)

    def lab_tests_create_record_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Submits Lab Test results for one or more packages. NOTE: This endpoint allows only PDF files, and uploaded files can be no more than 5 MB in size. The Label element in the request is a Package Label.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateRecord V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/labtests/v2/record"
        return self._send("POST", path, body, query_params)

    def lab_tests_get_batches_v2(self, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of Lab Test batches.
        
          Permissions Required:
          - None

        GET GetBatches V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/labtests/v2/batches"
        return self._send("GET", path, body, query_params)

    def lab_tests_get_labtestdocument_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        GET GetLabtestdocument V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/labtests/v1/labtestdocument/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def lab_tests_get_labtestdocument_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a specific Lab Test result document by its Id for a given Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        GET GetLabtestdocument V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/labtests/v2/labtestdocument/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def lab_tests_get_results_v1(self, body: Any = None, license_number: Optional[str] = None, package_id: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET GetResults V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if package_id is not None:
            query_params["packageId"] = package_id
        path = f"/labtests/v1/results"
        return self._send("GET", path, body, query_params)

    def lab_tests_get_results_v2(self, body: Any = None, license_number: Optional[str] = None, package_id: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves Lab Test results for a specified Package.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        GET GetResults V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if package_id is not None:
            query_params["packageId"] = package_id
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/labtests/v2/results"
        return self._send("GET", path, body, query_params)

    def lab_tests_get_states_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetStates V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/labtests/v1/states"
        return self._send("GET", path, body, query_params)

    def lab_tests_get_states_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Returns a list of all lab testing states.
        
          Permissions Required:
          - None

        GET GetStates V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/labtests/v2/states"
        return self._send("GET", path, body, query_params)

    def lab_tests_get_types_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetTypes V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/labtests/v1/types"
        return self._send("GET", path, body, query_params)

    def lab_tests_get_types_v2(self, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Returns a list of Lab Test types.
        
          Permissions Required:
          - None

        GET GetTypes V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/labtests/v2/types"
        return self._send("GET", path, body, query_params)

    def lab_tests_update_labtestdocument_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateLabtestdocument V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/labtests/v1/labtestdocument"
        return self._send("PUT", path, body, query_params)

    def lab_tests_update_labtestdocument_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates one or more documents for previously submitted lab tests.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateLabtestdocument V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/labtests/v2/labtestdocument"
        return self._send("PUT", path, body, query_params)

    def lab_tests_update_result_release_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateResultRelease V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/labtests/v1/results/release"
        return self._send("PUT", path, body, query_params)

    def lab_tests_update_result_release_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Releases Lab Test results for one or more packages.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateResultRelease V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/labtests/v2/results/release"
        return self._send("PUT", path, body, query_params)

    def patients_create_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Adds new patients to a specified Facility.
        
          Permissions Required:
          - Manage Patients

        POST Create V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v2"
        return self._send("POST", path, body, query_params)

    def patients_create_add_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Patients

        POST CreateAdd V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v1/add"
        return self._send("POST", path, body, query_params)

    def patients_create_update_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Patients

        POST CreateUpdate V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v1/update"
        return self._send("POST", path, body, query_params)

    def patients_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Patients

        DELETE Delete V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v1/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def patients_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Removes a Patient, identified by an Id, from a specified Facility.
        
          Permissions Required:
          - Manage Patients

        DELETE Delete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v2/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def patients_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Patients

        GET Get V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v1/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def patients_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Patient by Id.
        
          Permissions Required:
          - Manage Patients

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def patients_get_active_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Patients

        GET GetActive V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v1/active"
        return self._send("GET", path, body, query_params)

    def patients_get_active_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active patients for a specified Facility.
        
          Permissions Required:
          - Manage Patients

        GET GetActive V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/patients/v2/active"
        return self._send("GET", path, body, query_params)

    def patients_update_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates Patient information for a specified Facility.
        
          Permissions Required:
          - Manage Patients

        PUT Update V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v2"
        return self._send("PUT", path, body, query_params)

    def patients_status_get_statuses_by_patient_license_number_v1(self, patient_license_number: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Data returned by this endpoint is cached for up to one minute.
        
          Permissions Required:
          - Lookup Patients

        GET GetStatusesByPatientLicenseNumber V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v1/statuses/{urllib.parse.quote(patient_license_number)}"
        return self._send("GET", path, body, query_params)

    def patients_status_get_statuses_by_patient_license_number_v2(self, patient_license_number: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a list of statuses for a Patient License Number for a specified Facility. Data returned by this endpoint is cached for up to one minute.
        
          Permissions Required:
          - Lookup Patients

        GET GetStatusesByPatientLicenseNumber V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patients/v2/statuses/{urllib.parse.quote(patient_license_number)}"
        return self._send("GET", path, body, query_params)

    def tags_get_package_available_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Returns a list of available package tags. NOTE: This is a premium endpoint.
        
          Permissions Required:
          - Manage Tags

        GET GetPackageAvailable V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/tags/v2/package/available"
        return self._send("GET", path, body, query_params)

    def tags_get_plant_available_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Returns a list of available plant tags. NOTE: This is a premium endpoint.
        
          Permissions Required:
          - Manage Tags

        GET GetPlantAvailable V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/tags/v2/plant/available"
        return self._send("GET", path, body, query_params)

    def tags_get_staged_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Returns a list of staged tags. NOTE: This is a premium endpoint.
        
          Permissions Required:
          - Manage Tags
          - RetailId.AllowPackageStaging Key Value enabled

        GET GetStaged V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/tags/v2/staged"
        return self._send("GET", path, body, query_params)

    def units_of_measure_get_active_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetActive V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/unitsofmeasure/v1/active"
        return self._send("GET", path, body, query_params)

    def units_of_measure_get_active_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves all active units of measure.
        
          Permissions Required:
          - None

        GET GetActive V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/unitsofmeasure/v2/active"
        return self._send("GET", path, body, query_params)

    def units_of_measure_get_inactive_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves all inactive units of measure.
        
          Permissions Required:
          - None

        GET GetInactive V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/unitsofmeasure/v2/inactive"
        return self._send("GET", path, body, query_params)

    def waste_methods_get_all_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves all available waste methods.
        
          Permissions Required:
          - None

        GET GetAll V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/wastemethods/v2"
        return self._send("GET", path, body, query_params)

    def facilities_get_all_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        This endpoint provides a list of facilities for which the authenticated user has access.
        
          Permissions Required:
          - None

        GET GetAll V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/facilities/v1"
        return self._send("GET", path, body, query_params)

    def facilities_get_all_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        This endpoint provides a list of facilities for which the authenticated user has access.
        
          Permissions Required:
          - None

        GET GetAll V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/facilities/v2"
        return self._send("GET", path, body, query_params)

    def processing_jobs_create_adjust_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManageProcessingJobs

        POST CreateAdjust V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/adjust"
        return self._send("POST", path, body, query_params)

    def processing_jobs_create_adjust_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Adjusts the details of existing processing jobs at a Facility, including units of measure and associated packages.
        
          Permissions Required:
          - Manage Processing Job

        POST CreateAdjust V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/adjust"
        return self._send("POST", path, body, query_params)

    def processing_jobs_create_jobtypes_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        POST CreateJobtypes V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/jobtypes"
        return self._send("POST", path, body, query_params)

    def processing_jobs_create_jobtypes_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new processing job types for a Facility, including name, category, description, steps, and attributes.
        
          Permissions Required:
          - Manage Processing Job

        POST CreateJobtypes V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/jobtypes"
        return self._send("POST", path, body, query_params)

    def processing_jobs_create_start_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManageProcessingJobs

        POST CreateStart V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/start"
        return self._send("POST", path, body, query_params)

    def processing_jobs_create_start_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Initiates new processing jobs at a Facility, including job details and associated packages.
        
          Permissions Required:
          - Manage Processing Job

        POST CreateStart V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/start"
        return self._send("POST", path, body, query_params)

    def processing_jobs_createpackages_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManageProcessingJobs

        POST Createpackages V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/createpackages"
        return self._send("POST", path, body, query_params)

    def processing_jobs_createpackages_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages from processing jobs at a Facility, including optional location and note assignments.
        
          Permissions Required:
          - Manage Processing Job

        POST Createpackages V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/createpackages"
        return self._send("POST", path, body, query_params)

    def processing_jobs_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        DELETE Delete V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def processing_jobs_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a Processing Job at a Facility by marking it as inactive and removing it from active use.
        
          Permissions Required:
          - Manage Processing Job

        DELETE Delete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def processing_jobs_delete_jobtypes_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        DELETE DeleteJobtypes V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/jobtypes/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def processing_jobs_delete_jobtypes_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a Processing Job Type at a Facility, making it inactive for future use.
        
          Permissions Required:
          - Manage Processing Job

        DELETE DeleteJobtypes V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/jobtypes/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def processing_jobs_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET Get V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a ProcessingJob by Id.
        
          Permissions Required:
          - Manage Processing Job

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetActive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/active"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves active processing jobs at a specified Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/processing/v2/active"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetInactive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/inactive"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves inactive processing jobs at a specified Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/processing/v2/inactive"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_jobtypes_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetJobtypesActive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/jobtypes/active"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_jobtypes_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of all active processing job types defined within a Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetJobtypesActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/processing/v2/jobtypes/active"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_jobtypes_attributes_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetJobtypesAttributes V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/jobtypes/attributes"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_jobtypes_attributes_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves all processing job attributes available for a Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetJobtypesAttributes V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/jobtypes/attributes"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_jobtypes_categories_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetJobtypesCategories V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/jobtypes/categories"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_jobtypes_categories_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves all processing job categories available for a specified Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetJobtypesCategories V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/jobtypes/categories"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_jobtypes_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetJobtypesInactive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/jobtypes/inactive"
        return self._send("GET", path, body, query_params)

    def processing_jobs_get_jobtypes_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of all inactive processing job types defined within a Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetJobtypesInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/processing/v2/jobtypes/inactive"
        return self._send("GET", path, body, query_params)

    def processing_jobs_update_finish_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        PUT UpdateFinish V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/finish"
        return self._send("PUT", path, body, query_params)

    def processing_jobs_update_finish_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Completes processing jobs at a Facility by recording final notes and waste measurements.
        
          Permissions Required:
          - Manage Processing Job

        PUT UpdateFinish V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/finish"
        return self._send("PUT", path, body, query_params)

    def processing_jobs_update_jobtypes_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        PUT UpdateJobtypes V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/jobtypes"
        return self._send("PUT", path, body, query_params)

    def processing_jobs_update_jobtypes_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing processing job types at a Facility, including their name, category, description, steps, and attributes.
        
          Permissions Required:
          - Manage Processing Job

        PUT UpdateJobtypes V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/jobtypes"
        return self._send("PUT", path, body, query_params)

    def processing_jobs_update_unfinish_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        PUT UpdateUnfinish V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v1/unfinish"
        return self._send("PUT", path, body, query_params)

    def processing_jobs_update_unfinish_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Reopens previously completed processing jobs at a Facility to allow further updates or corrections.
        
          Permissions Required:
          - Manage Processing Job

        PUT UpdateUnfinish V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/processing/v2/unfinish"
        return self._send("PUT", path, body, query_params)

    def sublocations_create_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new sublocation records for a Facility.
        
          Permissions Required:
          - Manage Locations

        POST Create V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sublocations/v2"
        return self._send("POST", path, body, query_params)

    def sublocations_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives an existing Sublocation record for a Facility.
        
          Permissions Required:
          - Manage Locations

        DELETE Delete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sublocations/v2/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def sublocations_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Sublocation by its Id, with an optional license number.
        
          Permissions Required:
          - Manage Locations

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sublocations/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def sublocations_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active sublocations for the current Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Locations

        GET GetActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/sublocations/v2/active"
        return self._send("GET", path, body, query_params)

    def sublocations_get_inactive_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive sublocations for the specified Facility.
        
          Permissions Required:
          - Manage Locations

        GET GetInactive V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/sublocations/v2/inactive"
        return self._send("GET", path, body, query_params)

    def sublocations_update_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing sublocation records for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        PUT Update V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/sublocations/v2"
        return self._send("PUT", path, body, query_params)

    def transfers_create_external_incoming_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        POST CreateExternalIncoming V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/external/incoming"
        return self._send("POST", path, body, query_params)

    def transfers_create_external_incoming_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates external incoming shipment plans for a Facility.
        
          Permissions Required:
          - Manage Transfers

        POST CreateExternalIncoming V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v2/external/incoming"
        return self._send("POST", path, body, query_params)

    def transfers_create_templates_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfer Templates

        POST CreateTemplates V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/templates"
        return self._send("POST", path, body, query_params)

    def transfers_create_templates_outgoing_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new transfer templates for a Facility.
        
          Permissions Required:
          - Manage Transfer Templates

        POST CreateTemplatesOutgoing V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v2/templates/outgoing"
        return self._send("POST", path, body, query_params)

    def transfers_delete_external_incoming_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        DELETE DeleteExternalIncoming V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/external/incoming/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def transfers_delete_external_incoming_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Voids an external incoming shipment plan for a Facility.
        
          Permissions Required:
          - Manage Transfers

        DELETE DeleteExternalIncoming V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v2/external/incoming/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def transfers_delete_templates_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfer Templates

        DELETE DeleteTemplates V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/templates/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def transfers_delete_templates_outgoing_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a transfer template for a Facility.
        
          Permissions Required:
          - Manage Transfer Templates

        DELETE DeleteTemplatesOutgoing V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v2/templates/outgoing/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def transfers_get_deliveries_packages_states_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetDeliveriesPackagesStates V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/deliveries/packages/states"
        return self._send("GET", path, body, query_params)

    def transfers_get_deliveries_packages_states_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Returns a list of available shipment Package states.
        
          Permissions Required:
          - None

        GET GetDeliveriesPackagesStates V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v2/deliveries/packages/states"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: that the {id} parameter above represents a Shipment Plan ID.
        
          Permissions Required:
          - Transfers

        GET GetDelivery V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/{urllib.parse.quote(id)}/deliveries"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of shipment deliveries for a given Transfer Id. Please note: The {id} parameter above represents a Transfer Id.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDelivery V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/{urllib.parse.quote(id)}/deliveries"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_package_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Delivery ID, not a Manifest Number.
        
          Permissions Required:
          - Transfers

        GET GetDeliveryPackage V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/deliveries/{urllib.parse.quote(id)}/packages"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_package_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of packages associated with a given Transfer Delivery Id. Please note: The {id} parameter above represents a Transfer Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDeliveryPackage V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/deliveries/{urllib.parse.quote(id)}/packages"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_package_requiredlabtestbatches_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Delivery Package ID, not a Manifest Number.
        
          Permissions Required:
          - Transfers

        GET GetDeliveryPackageRequiredlabtestbatches V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/deliveries/package/{urllib.parse.quote(id)}/requiredlabtestbatches"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_package_requiredlabtestbatches_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of required lab test batches for a given Transfer Delivery Package Id. Please note: The {id} parameter above represents a Transfer Delivery Package Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDeliveryPackageRequiredlabtestbatches V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/deliveries/package/{urllib.parse.quote(id)}/requiredlabtestbatches"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_package_wholesale_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Delivery ID, not a Manifest Number.
        
          Permissions Required:
          - Transfers

        GET GetDeliveryPackageWholesale V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/deliveries/{urllib.parse.quote(id)}/packages/wholesale"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_package_wholesale_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of wholesale shipment packages for a given Transfer Delivery Id. Please note: The {id} parameter above represents a Transfer Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDeliveryPackageWholesale V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/deliveries/{urllib.parse.quote(id)}/packages/wholesale"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_transporters_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: that the {id} parameter above represents a Shipment Delivery ID.
        
          Permissions Required:
          - Transfers

        GET GetDeliveryTransporters V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/deliveries/{urllib.parse.quote(id)}/transporters"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_transporters_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transporters for a given Transfer Delivery Id. Please note: The {id} parameter above represents a Transfer Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDeliveryTransporters V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/deliveries/{urllib.parse.quote(id)}/transporters"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_transporters_details_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Shipment Delivery ID.
        
          Permissions Required:
          - Transfers

        GET GetDeliveryTransportersDetails V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/deliveries/{urllib.parse.quote(id)}/transporters/details"
        return self._send("GET", path, body, query_params)

    def transfers_get_delivery_transporters_details_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transporter details for a given Transfer Delivery Id. Please note: The {id} parameter above represents a Transfer Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDeliveryTransportersDetails V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/deliveries/{urllib.parse.quote(id)}/transporters/details"
        return self._send("GET", path, body, query_params)

    def transfers_get_hub_v2(self, body: Any = None, estimated_arrival_end: Optional[str] = None, estimated_arrival_start: Optional[str] = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transfer hub shipments for a Facility, filtered by either last modified or estimated arrival date range.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetHub V2
        """
        query_params = {}
        if estimated_arrival_end is not None:
            query_params["estimatedArrivalEnd"] = estimated_arrival_end
        if estimated_arrival_start is not None:
            query_params["estimatedArrivalStart"] = estimated_arrival_start
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/hub"
        return self._send("GET", path, body, query_params)

    def transfers_get_incoming_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        GET GetIncoming V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/incoming"
        return self._send("GET", path, body, query_params)

    def transfers_get_incoming_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of incoming shipments for a Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetIncoming V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/incoming"
        return self._send("GET", path, body, query_params)

    def transfers_get_outgoing_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        GET GetOutgoing V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/outgoing"
        return self._send("GET", path, body, query_params)

    def transfers_get_outgoing_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of outgoing shipments for a Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetOutgoing V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/outgoing"
        return self._send("GET", path, body, query_params)

    def transfers_get_rejected_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        GET GetRejected V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/rejected"
        return self._send("GET", path, body, query_params)

    def transfers_get_rejected_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of shipments with rejected packages for a Facility.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetRejected V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/rejected"
        return self._send("GET", path, body, query_params)

    def transfers_get_templates_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfer Templates

        GET GetTemplates V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/templates"
        return self._send("GET", path, body, query_params)

    def transfers_get_templates_delivery_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfer Templates

        GET GetTemplatesDelivery V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/templates/{urllib.parse.quote(id)}/deliveries"
        return self._send("GET", path, body, query_params)

    def transfers_get_templates_delivery_package_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Template Delivery ID, not a Manifest Number.
        
          Permissions Required:
          - Transfers

        GET GetTemplatesDeliveryPackage V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/templates/deliveries/{urllib.parse.quote(id)}/packages"
        return self._send("GET", path, body, query_params)

    def transfers_get_templates_delivery_transporters_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Template Delivery ID, not a Manifest Number.
        
          Permissions Required:
          - Transfer Templates

        GET GetTemplatesDeliveryTransporters V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/templates/deliveries/{urllib.parse.quote(id)}/transporters"
        return self._send("GET", path, body, query_params)

    def transfers_get_templates_delivery_transporters_details_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Template Delivery ID, not a Manifest Number.
        
          Permissions Required:
          - Transfer Templates

        GET GetTemplatesDeliveryTransportersDetails V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v1/templates/deliveries/{urllib.parse.quote(id)}/transporters/details"
        return self._send("GET", path, body, query_params)

    def transfers_get_templates_outgoing_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transfer templates for a Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Transfer Templates
          - View Transfer Templates

        GET GetTemplatesOutgoing V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/templates/outgoing"
        return self._send("GET", path, body, query_params)

    def transfers_get_templates_outgoing_delivery_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of deliveries associated with a specific transfer template.
        
          Permissions Required:
          - Manage Transfer Templates
          - View Transfer Templates

        GET GetTemplatesOutgoingDelivery V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/templates/outgoing/{urllib.parse.quote(id)}/deliveries"
        return self._send("GET", path, body, query_params)

    def transfers_get_templates_outgoing_delivery_package_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of delivery package templates for a given Transfer Template Delivery Id. Please note: The {id} parameter above represents a Transfer Template Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfer Templates
          - View Transfer Templates

        GET GetTemplatesOutgoingDeliveryPackage V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/templates/outgoing/deliveries/{urllib.parse.quote(id)}/packages"
        return self._send("GET", path, body, query_params)

    def transfers_get_templates_outgoing_delivery_transporters_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transporter templates for a given Transfer Template Delivery Id. Please note: The {id} parameter above represents a Transfer Template Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfer Templates
          - View Transfer Templates

        GET GetTemplatesOutgoingDeliveryTransporters V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/templates/outgoing/deliveries/{urllib.parse.quote(id)}/transporters"
        return self._send("GET", path, body, query_params)

    def transfers_get_templates_outgoing_delivery_transporters_details_v2(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves detailed transporter templates for a given Transfer Template Delivery Id. Please note: The {id} parameter above represents a Transfer Template Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfer Templates
          - View Transfer Templates

        GET GetTemplatesOutgoingDeliveryTransportersDetails V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/transfers/v2/templates/outgoing/deliveries/{urllib.parse.quote(id)}/transporters/details"
        return self._send("GET", path, body, query_params)

    def transfers_get_types_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetTypes V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/types"
        return self._send("GET", path, body, query_params)

    def transfers_get_types_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of available transfer types for a Facility based on its license number.
        
          Permissions Required:
          - None

        GET GetTypes V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transfers/v2/types"
        return self._send("GET", path, body, query_params)

    def transfers_update_external_incoming_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        PUT UpdateExternalIncoming V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/external/incoming"
        return self._send("PUT", path, body, query_params)

    def transfers_update_external_incoming_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates external incoming shipment plans for a Facility.
        
          Permissions Required:
          - Manage Transfers

        PUT UpdateExternalIncoming V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v2/external/incoming"
        return self._send("PUT", path, body, query_params)

    def transfers_update_templates_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfer Templates

        PUT UpdateTemplates V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v1/templates"
        return self._send("PUT", path, body, query_params)

    def transfers_update_templates_outgoing_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing transfer templates for a Facility.
        
          Permissions Required:
          - Manage Transfer Templates

        PUT UpdateTemplatesOutgoing V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transfers/v2/templates/outgoing"
        return self._send("PUT", path, body, query_params)

    def caregivers_status_get_by_caregiver_license_number_v1(self, caregiver_license_number: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Data returned by this endpoint is cached for up to one minute.
        
          Permissions Required:
          - Lookup Caregivers

        GET GetByCaregiverLicenseNumber V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/caregivers/v1/status/{urllib.parse.quote(caregiver_license_number)}"
        return self._send("GET", path, body, query_params)

    def caregivers_status_get_by_caregiver_license_number_v2(self, caregiver_license_number: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves the status of a Caregiver by their License Number for a specified Facility. Data returned by this endpoint is cached for up to one minute.
        
          Permissions Required:
          - Lookup Caregivers

        GET GetByCaregiverLicenseNumber V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/caregivers/v2/status/{urllib.parse.quote(caregiver_license_number)}"
        return self._send("GET", path, body, query_params)

    def employees_get_all_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Employees

        GET GetAll V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/employees/v1"
        return self._send("GET", path, body, query_params)

    def employees_get_all_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of employees for a specified Facility.
        
          Permissions Required:
          - Manage Employees
          - View Employees

        GET GetAll V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/employees/v2"
        return self._send("GET", path, body, query_params)

    def employees_get_permissions_v2(self, body: Any = None, employee_license_number: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves the permissions of a specified Employee, identified by their Employee License Number, for a given Facility.
        
          Permissions Required:
          - Manage Employees

        GET GetPermissions V2
        """
        query_params = {}
        if employee_license_number is not None:
            query_params["employeeLicenseNumber"] = employee_license_number
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/employees/v2/permissions"
        return self._send("GET", path, body, query_params)

    def harvests_create_finish_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Finish/Discontinue Harvests

        POST CreateFinish V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/finish"
        return self._send("POST", path, body, query_params)

    def harvests_create_package_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Manage Harvests
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackage V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/create/packages"
        return self._send("POST", path, body, query_params)

    def harvests_create_package_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages from harvested products for a specified Facility.
        
          Permissions Required:
          - View Harvests
          - Manage Harvests
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackage V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v2/packages"
        return self._send("POST", path, body, query_params)

    def harvests_create_package_testing_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Manage Harvests
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackageTesting V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/create/packages/testing"
        return self._send("POST", path, body, query_params)

    def harvests_create_package_testing_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages for testing from harvested products for a specified Facility.
        
          Permissions Required:
          - View Harvests
          - Manage Harvests
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackageTesting V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v2/packages/testing"
        return self._send("POST", path, body, query_params)

    def harvests_create_remove_waste_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Manage Harvests

        POST CreateRemoveWaste V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/removewaste"
        return self._send("POST", path, body, query_params)

    def harvests_create_unfinish_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Finish/Discontinue Harvests

        POST CreateUnfinish V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/unfinish"
        return self._send("POST", path, body, query_params)

    def harvests_create_waste_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records Waste from harvests for a specified Facility. NOTE: The IDs passed in the request body are the harvest IDs for which you are documenting waste.
        
          Permissions Required:
          - View Harvests
          - Manage Harvests

        POST CreateWaste V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v2/waste"
        return self._send("POST", path, body, query_params)

    def harvests_delete_waste_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Discontinues a specific harvest waste record by Id for the specified Facility.
        
          Permissions Required:
          - View Harvests
          - Discontinue Harvest Waste

        DELETE DeleteWaste V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v2/waste/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def harvests_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests

        GET Get V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def harvests_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Harvest by its Id, optionally validated against a specified Facility License Number.
        
          Permissions Required:
          - View Harvests

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def harvests_get_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests

        GET GetActive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/active"
        return self._send("GET", path, body, query_params)

    def harvests_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active harvests for a specified Facility.
        
          Permissions Required:
          - View Harvests

        GET GetActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/harvests/v2/active"
        return self._send("GET", path, body, query_params)

    def harvests_get_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests

        GET GetInactive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/inactive"
        return self._send("GET", path, body, query_params)

    def harvests_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive harvests for a specified Facility.
        
          Permissions Required:
          - View Harvests

        GET GetInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/harvests/v2/inactive"
        return self._send("GET", path, body, query_params)

    def harvests_get_onhold_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests

        GET GetOnhold V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/onhold"
        return self._send("GET", path, body, query_params)

    def harvests_get_onhold_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of harvests on hold for a specified Facility.
        
          Permissions Required:
          - View Harvests

        GET GetOnhold V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/harvests/v2/onhold"
        return self._send("GET", path, body, query_params)

    def harvests_get_waste_v2(self, body: Any = None, harvest_id: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of Waste records for a specified Harvest, identified by its Harvest Id, within a Facility identified by its License Number.
        
          Permissions Required:
          - View Harvests

        GET GetWaste V2
        """
        query_params = {}
        if harvest_id is not None:
            query_params["harvestId"] = harvest_id
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/harvests/v2/waste"
        return self._send("GET", path, body, query_params)

    def harvests_get_waste_types_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetWasteTypes V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/harvests/v1/waste/types"
        return self._send("GET", path, body, query_params)

    def harvests_get_waste_types_v2(self, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of Waste types for harvests.
        
          Permissions Required:
          - None

        GET GetWasteTypes V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/harvests/v2/waste/types"
        return self._send("GET", path, body, query_params)

    def harvests_update_finish_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Marks one or more harvests as finished for the specified Facility.
        
          Permissions Required:
          - View Harvests
          - Finish/Discontinue Harvests

        PUT UpdateFinish V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v2/finish"
        return self._send("PUT", path, body, query_params)

    def harvests_update_location_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the Location of Harvest for a specified Facility.
        
          Permissions Required:
          - View Harvests
          - Manage Harvests

        PUT UpdateLocation V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v2/location"
        return self._send("PUT", path, body, query_params)

    def harvests_update_move_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Manage Harvests

        PUT UpdateMove V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/move"
        return self._send("PUT", path, body, query_params)

    def harvests_update_rename_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Manage Harvests

        PUT UpdateRename V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v1/rename"
        return self._send("PUT", path, body, query_params)

    def harvests_update_rename_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Renames one or more harvests for the specified Facility.
        
          Permissions Required:
          - View Harvests
          - Manage Harvests

        PUT UpdateRename V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v2/rename"
        return self._send("PUT", path, body, query_params)

    def harvests_update_restore_harvested_plants_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Restores previously harvested plants to their original state for the specified Facility.
        
          Permissions Required:
          - View Harvests
          - Finish/Discontinue Harvests

        PUT UpdateRestoreHarvestedPlants V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v2/restore/harvestedplants"
        return self._send("PUT", path, body, query_params)

    def harvests_update_unfinish_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Reopens one or more previously finished harvests for the specified Facility.
        
          Permissions Required:
          - View Harvests
          - Finish/Discontinue Harvests

        PUT UpdateUnfinish V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/harvests/v2/unfinish"
        return self._send("PUT", path, body, query_params)

    def packages_create_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST Create V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/create"
        return self._send("POST", path, body, query_params)

    def packages_create_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new packages for a specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST Create V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2"
        return self._send("POST", path, body, query_params)

    def packages_create_adjust_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateAdjust V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/adjust"
        return self._send("POST", path, body, query_params)

    def packages_create_adjust_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records a list of adjustments for packages at a specific Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateAdjust V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/adjust"
        return self._send("POST", path, body, query_params)

    def packages_create_change_item_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreateChangeItem V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/change/item"
        return self._send("POST", path, body, query_params)

    def packages_create_change_location_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreateChangeLocation V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/change/locations"
        return self._send("POST", path, body, query_params)

    def packages_create_finish_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateFinish V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/finish"
        return self._send("POST", path, body, query_params)

    def packages_create_plantings_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants
          - View Packages
          - Manage Packages Inventory

        POST CreatePlantings V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/create/plantings"
        return self._send("POST", path, body, query_params)

    def packages_create_plantings_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new plantings from packages for a specified Facility.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants
          - View Packages
          - Manage Packages Inventory

        POST CreatePlantings V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/plantings"
        return self._send("POST", path, body, query_params)

    def packages_create_remediate_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateRemediate V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/remediate"
        return self._send("POST", path, body, query_params)

    def packages_create_testing_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreateTesting V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/create/testing"
        return self._send("POST", path, body, query_params)

    def packages_create_testing_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new packages for testing for a specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreateTesting V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/testing"
        return self._send("POST", path, body, query_params)

    def packages_create_unfinish_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateUnfinish V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/unfinish"
        return self._send("POST", path, body, query_params)

    def packages_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Discontinues a Package at a specific Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        DELETE Delete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def packages_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET Get V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def packages_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Package by its Id.
        
          Permissions Required:
          - View Packages

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def packages_get_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET GetActive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/active"
        return self._send("GET", path, body, query_params)

    def packages_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active packages for a specified Facility.
        
          Permissions Required:
          - View Packages

        GET GetActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/packages/v2/active"
        return self._send("GET", path, body, query_params)

    def packages_get_adjust_reasons_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetAdjustReasons V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/adjust/reasons"
        return self._send("GET", path, body, query_params)

    def packages_get_adjust_reasons_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of adjustment reasons for packages at a specified Facility.
        
          Permissions Required:
          - None

        GET GetAdjustReasons V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/packages/v2/adjust/reasons"
        return self._send("GET", path, body, query_params)

    def packages_get_by_label_v1(self, label: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET GetByLabel V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/{urllib.parse.quote(label)}"
        return self._send("GET", path, body, query_params)

    def packages_get_by_label_v2(self, label: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Package by its label.
        
          Permissions Required:
          - View Packages

        GET GetByLabel V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/{urllib.parse.quote(label)}"
        return self._send("GET", path, body, query_params)

    def packages_get_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET GetInactive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/inactive"
        return self._send("GET", path, body, query_params)

    def packages_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive packages for a specified Facility.
        
          Permissions Required:
          - View Packages

        GET GetInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/packages/v2/inactive"
        return self._send("GET", path, body, query_params)

    def packages_get_intransit_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of packages in transit for a specified Facility.
        
          Permissions Required:
          - View Packages

        GET GetIntransit V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/packages/v2/intransit"
        return self._send("GET", path, body, query_params)

    def packages_get_labsamples_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of lab sample packages created or sent for testing for a specified Facility.
        
          Permissions Required:
          - View Packages

        GET GetLabsamples V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/packages/v2/labsamples"
        return self._send("GET", path, body, query_params)

    def packages_get_onhold_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET GetOnhold V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/onhold"
        return self._send("GET", path, body, query_params)

    def packages_get_onhold_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of packages on hold for a specified Facility.
        
          Permissions Required:
          - View Packages

        GET GetOnhold V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/packages/v2/onhold"
        return self._send("GET", path, body, query_params)

    def packages_get_source_harvest_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves the source harvests for a Package by its Id.
        
          Permissions Required:
          - View Package Source Harvests

        GET GetSourceHarvest V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/{urllib.parse.quote(id)}/source/harvests"
        return self._send("GET", path, body, query_params)

    def packages_get_transferred_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transferred packages for a specific Facility.
        
          Permissions Required:
          - View Packages

        GET GetTransferred V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/packages/v2/transferred"
        return self._send("GET", path, body, query_params)

    def packages_get_types_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetTypes V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/packages/v1/types"
        return self._send("GET", path, body, query_params)

    def packages_get_types_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves a list of available Package types.
        
          Permissions Required:
          - None

        GET GetTypes V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/packages/v2/types"
        return self._send("GET", path, body, query_params)

    def packages_update_adjust_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Set the final quantity for a Package.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateAdjust V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/adjust"
        return self._send("PUT", path, body, query_params)

    def packages_update_change_note_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory
          - Manage Package Notes

        PUT UpdateChangeNote V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v1/change/note"
        return self._send("PUT", path, body, query_params)

    def packages_update_decontaminate_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the Product decontaminate information for a list of packages at a specific Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateDecontaminate V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/decontaminate"
        return self._send("PUT", path, body, query_params)

    def packages_update_donation_flag_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Flags one or more packages for donation at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateDonationFlag V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/donation/flag"
        return self._send("PUT", path, body, query_params)

    def packages_update_donation_unflag_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Removes the donation flag from one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateDonationUnflag V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/donation/unflag"
        return self._send("PUT", path, body, query_params)

    def packages_update_externalid_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the external identifiers for one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Manage Package Inventory
          - External Id Enabled

        PUT UpdateExternalid V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/externalid"
        return self._send("PUT", path, body, query_params)

    def packages_update_finish_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates a list of packages as finished for a specific Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateFinish V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/finish"
        return self._send("PUT", path, body, query_params)

    def packages_update_item_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the associated Item for one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        PUT UpdateItem V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/item"
        return self._send("PUT", path, body, query_params)

    def packages_update_lab_test_required_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the list of required lab test batches for one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        PUT UpdateLabTestRequired V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/labtests/required"
        return self._send("PUT", path, body, query_params)

    def packages_update_location_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the Location and Sublocation for one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        PUT UpdateLocation V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/location"
        return self._send("PUT", path, body, query_params)

    def packages_update_note_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates notes associated with one or more packages for the specified Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory
          - Manage Package Notes

        PUT UpdateNote V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/note"
        return self._send("PUT", path, body, query_params)

    def packages_update_remediate_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates a list of Product remediations for packages at a specific Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateRemediate V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/remediate"
        return self._send("PUT", path, body, query_params)

    def packages_update_tradesample_flag_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Flags or unflags one or more packages at the specified Facility as trade samples.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateTradesampleFlag V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/tradesample/flag"
        return self._send("PUT", path, body, query_params)

    def packages_update_tradesample_unflag_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Removes the trade sample flag from one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateTradesampleUnflag V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/tradesample/unflag"
        return self._send("PUT", path, body, query_params)

    def packages_update_unfinish_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates a list of packages as unfinished for a specific Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateUnfinish V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/unfinish"
        return self._send("PUT", path, body, query_params)

    def packages_update_usebydate_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the use-by date for one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        PUT UpdateUsebydate V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/packages/v2/usebydate"
        return self._send("PUT", path, body, query_params)

    def patient_check_ins_create_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManagePatientsCheckIns

        POST Create V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patient-checkins/v1"
        return self._send("POST", path, body, query_params)

    def patient_check_ins_create_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records patient check-ins for a specified Facility.
        
          Permissions Required:
          - ManagePatientsCheckIns

        POST Create V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patient-checkins/v2"
        return self._send("POST", path, body, query_params)

    def patient_check_ins_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManagePatientsCheckIns

        DELETE Delete V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patient-checkins/v1/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def patient_check_ins_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a Patient Check-In, identified by its Id, for a specified Facility.
        
          Permissions Required:
          - ManagePatientsCheckIns

        DELETE Delete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patient-checkins/v2/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def patient_check_ins_get_all_v1(self, body: Any = None, checkin_date_end: Optional[str] = None, checkin_date_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManagePatientsCheckIns

        GET GetAll V1
        """
        query_params = {}
        if checkin_date_end is not None:
            query_params["checkinDateEnd"] = checkin_date_end
        if checkin_date_start is not None:
            query_params["checkinDateStart"] = checkin_date_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patient-checkins/v1"
        return self._send("GET", path, body, query_params)

    def patient_check_ins_get_all_v2(self, body: Any = None, checkin_date_end: Optional[str] = None, checkin_date_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a list of patient check-ins for a specified Facility.
        
          Permissions Required:
          - ManagePatientsCheckIns

        GET GetAll V2
        """
        query_params = {}
        if checkin_date_end is not None:
            query_params["checkinDateEnd"] = checkin_date_end
        if checkin_date_start is not None:
            query_params["checkinDateStart"] = checkin_date_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patient-checkins/v2"
        return self._send("GET", path, body, query_params)

    def patient_check_ins_get_locations_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetLocations V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/patient-checkins/v1/locations"
        return self._send("GET", path, body, query_params)

    def patient_check_ins_get_locations_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves a list of Patient Check-In locations.
        
          Permissions Required:
          - None

        GET GetLocations V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/patient-checkins/v2/locations"
        return self._send("GET", path, body, query_params)

    def patient_check_ins_update_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManagePatientsCheckIns

        PUT Update V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patient-checkins/v1"
        return self._send("PUT", path, body, query_params)

    def patient_check_ins_update_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates patient check-ins for a specified Facility.
        
          Permissions Required:
          - ManagePatientsCheckIns

        PUT Update V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/patient-checkins/v2"
        return self._send("PUT", path, body, query_params)

    def transporters_create_driver_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new driver records for a Facility.
        
          Permissions Required:
          - Manage Transporters

        POST CreateDriver V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transporters/v2/drivers"
        return self._send("POST", path, body, query_params)

    def transporters_create_vehicle_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new vehicle records for a Facility.
        
          Permissions Required:
          - Manage Transporters

        POST CreateVehicle V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transporters/v2/vehicles"
        return self._send("POST", path, body, query_params)

    def transporters_delete_driver_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a Driver record for a Facility.  Please note: The {id} parameter above represents a Driver Id.
        
          Permissions Required:
          - Manage Transporters

        DELETE DeleteDriver V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transporters/v2/drivers/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def transporters_delete_vehicle_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a Vehicle for a facility.  Please note: The {id} parameter above represents a Vehicle Id.
        
          Permissions Required:
          - Manage Transporters

        DELETE DeleteVehicle V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transporters/v2/vehicles/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def transporters_get_driver_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Driver by its Id, with an optional license number. Please note: The {id} parameter above represents a Driver Id.
        
          Permissions Required:
          - Transporters

        GET GetDriver V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transporters/v2/drivers/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def transporters_get_drivers_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of drivers for a Facility.
        
          Permissions Required:
          - Transporters

        GET GetDrivers V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transporters/v2/drivers"
        return self._send("GET", path, body, query_params)

    def transporters_get_vehicle_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Vehicle by its Id, with an optional license number. Please note: The {id} parameter above represents a Vehicle Id.
        
          Permissions Required:
          - Transporters

        GET GetVehicle V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transporters/v2/vehicles/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def transporters_get_vehicles_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of vehicles for a Facility.
        
          Permissions Required:
          - Transporters

        GET GetVehicles V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/transporters/v2/vehicles"
        return self._send("GET", path, body, query_params)

    def transporters_update_driver_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing driver records for a Facility.
        
          Permissions Required:
          - Manage Transporters

        PUT UpdateDriver V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transporters/v2/drivers"
        return self._send("PUT", path, body, query_params)

    def transporters_update_vehicle_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing vehicle records for a facility.
        
          Permissions Required:
          - Manage Transporters

        PUT UpdateVehicle V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/transporters/v2/vehicles"
        return self._send("PUT", path, body, query_params)

    def additives_templates_create_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new additive templates for a specified Facility.
        
          Permissions Required:
          - Manage Additives

        POST Create V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/additivestemplates/v2"
        return self._send("POST", path, body, query_params)

    def additives_templates_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves an Additive Template by its Id.
        
          Permissions Required:
          - Manage Additives

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/additivestemplates/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def additives_templates_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active additive templates for a specified Facility.
        
          Permissions Required:
          - Manage Additives

        GET GetActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/additivestemplates/v2/active"
        return self._send("GET", path, body, query_params)

    def additives_templates_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive additive templates for a specified Facility.
        
          Permissions Required:
          - Manage Additives

        GET GetInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/additivestemplates/v2/inactive"
        return self._send("GET", path, body, query_params)

    def additives_templates_update_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing additive templates for a specified Facility.
        
          Permissions Required:
          - Manage Additives

        PUT Update V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/additivestemplates/v2"
        return self._send("PUT", path, body, query_params)

    def locations_create_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        POST Create V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/locations/v1/create"
        return self._send("POST", path, body, query_params)

    def locations_create_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new locations for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        POST Create V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/locations/v2"
        return self._send("POST", path, body, query_params)

    def locations_create_update_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        POST CreateUpdate V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/locations/v1/update"
        return self._send("POST", path, body, query_params)

    def locations_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        DELETE Delete V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/locations/v1/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def locations_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a specified Location, identified by its Id, for a Facility.
        
          Permissions Required:
          - Manage Locations

        DELETE Delete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/locations/v2/{urllib.parse.quote(id)}"
        return self._send("DELETE", path, body, query_params)

    def locations_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        GET Get V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/locations/v1/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def locations_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Location by its Id.
        
          Permissions Required:
          - Manage Locations

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/locations/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def locations_get_active_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        GET GetActive V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/locations/v1/active"
        return self._send("GET", path, body, query_params)

    def locations_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active locations for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        GET GetActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/locations/v2/active"
        return self._send("GET", path, body, query_params)

    def locations_get_inactive_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive locations for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        GET GetInactive V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/locations/v2/inactive"
        return self._send("GET", path, body, query_params)

    def locations_get_types_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        GET GetTypes V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/locations/v1/types"
        return self._send("GET", path, body, query_params)

    def locations_get_types_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active location types for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        GET GetTypes V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/locations/v2/types"
        return self._send("GET", path, body, query_params)

    def locations_update_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing locations for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        PUT Update V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/locations/v2"
        return self._send("PUT", path, body, query_params)

    def plant_batches_create_additives_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Plants Additives

        POST CreateAdditives V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/additives"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_additives_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records Additive usage details for plant batches at a specific Facility.
        
          Permissions Required:
          - Manage Plants Additives

        POST CreateAdditives V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/additives"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_additives_usingtemplate_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records Additive usage for plant batches at a Facility using predefined additive templates.
        
          Permissions Required:
          - Manage Plants Additives

        POST CreateAdditivesUsingtemplate V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/additives/usingtemplate"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_adjust_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST CreateAdjust V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/adjust"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_adjust_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Applies Facility specific adjustments to plant batches based on submitted reasons and input data.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST CreateAdjust V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/adjust"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_changegrowthphase_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreateChangegrowthphase V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/changegrowthphase"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_growthphase_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the growth phase of plants at a specified Facility based on tracking information.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreateGrowthphase V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/growthphase"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_package_v2(self, body: Any = None, is_from_mother_plant: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages from plant batches at a Facility, with optional support for packaging from mother plants.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackage V2
        """
        query_params = {}
        if is_from_mother_plant is not None:
            query_params["isFromMotherPlant"] = is_from_mother_plant
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/packages"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_package_frommotherplant_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackageFrommotherplant V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/create/packages/frommotherplant"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_package_frommotherplant_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages from mother plants at the specified Facility.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackageFrommotherplant V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/packages/frommotherplant"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_plantings_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new plantings for a Facility by generating plant batches based on provided planting details.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST CreatePlantings V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/plantings"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_split_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST CreateSplit V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/split"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_split_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Splits an existing Plant Batch into multiple groups at the specified Facility.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST CreateSplit V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/split"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_waste_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Plants Waste

        POST CreateWaste V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/waste"
        return self._send("POST", path, body, query_params)

    def plant_batches_create_waste_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records waste information for plant batches based on the submitted data for the specified Facility.
        
          Permissions Required:
          - Manage Plants Waste

        POST CreateWaste V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/waste"
        return self._send("POST", path, body, query_params)

    def plant_batches_createpackages_v1(self, body: Any = None, is_from_mother_plant: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST Createpackages V1
        """
        query_params = {}
        if is_from_mother_plant is not None:
            query_params["isFromMotherPlant"] = is_from_mother_plant
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/createpackages"
        return self._send("POST", path, body, query_params)

    def plant_batches_createplantings_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST Createplantings V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/createplantings"
        return self._send("POST", path, body, query_params)

    def plant_batches_delete_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Destroy Immature Plants

        DELETE Delete V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1"
        return self._send("DELETE", path, body, query_params)

    def plant_batches_delete_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Completes the destruction of plant batches based on the provided input data.
        
          Permissions Required:
          - View Immature Plants
          - Destroy Immature Plants

        DELETE Delete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2"
        return self._send("DELETE", path, body, query_params)

    def plant_batches_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants

        GET Get V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def plant_batches_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Plant Batch by Id.
        
          Permissions Required:
          - View Immature Plants

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def plant_batches_get_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants

        GET GetActive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/active"
        return self._send("GET", path, body, query_params)

    def plant_batches_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active plant batches for the specified Facility, optionally filtered by last modified date.
        
          Permissions Required:
          - View Immature Plants

        GET GetActive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plantbatches/v2/active"
        return self._send("GET", path, body, query_params)

    def plant_batches_get_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants

        GET GetInactive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/inactive"
        return self._send("GET", path, body, query_params)

    def plant_batches_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive plant batches for the specified Facility, optionally filtered by last modified date.
        
          Permissions Required:
          - View Immature Plants

        GET GetInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plantbatches/v2/inactive"
        return self._send("GET", path, body, query_params)

    def plant_batches_get_types_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetTypes V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/plantbatches/v1/types"
        return self._send("GET", path, body, query_params)

    def plant_batches_get_types_v2(self, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of plant batch types.
        
          Permissions Required:
          - None

        GET GetTypes V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plantbatches/v2/types"
        return self._send("GET", path, body, query_params)

    def plant_batches_get_waste_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves waste details associated with plant batches at a specified Facility.
        
          Permissions Required:
          - View Plants Waste

        GET GetWaste V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plantbatches/v2/waste"
        return self._send("GET", path, body, query_params)

    def plant_batches_get_waste_reasons_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetWasteReasons V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/waste/reasons"
        return self._send("GET", path, body, query_params)

    def plant_batches_get_waste_reasons_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a list of valid waste reasons associated with immature plant batches for the specified Facility.
        
          Permissions Required:
          - None

        GET GetWasteReasons V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/waste/reasons"
        return self._send("GET", path, body, query_params)

    def plant_batches_update_location_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Moves one or more plant batches to new locations with in a specified Facility.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants

        PUT UpdateLocation V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/location"
        return self._send("PUT", path, body, query_params)

    def plant_batches_update_moveplantbatches_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants

        PUT UpdateMoveplantbatches V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v1/moveplantbatches"
        return self._send("PUT", path, body, query_params)

    def plant_batches_update_name_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Renames plant batches at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateName V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/name"
        return self._send("PUT", path, body, query_params)

    def plant_batches_update_strain_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Changes the strain of plant batches at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateStrain V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/strain"
        return self._send("PUT", path, body, query_params)

    def plant_batches_update_tag_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Replaces tags for plant batches at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateTag V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plantbatches/v2/tag"
        return self._send("PUT", path, body, query_params)

    def plants_create_additives_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Plants Additives

        POST CreateAdditives V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/additives"
        return self._send("POST", path, body, query_params)

    def plants_create_additives_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records additive usage details applied to specific plants at a Facility.
        
          Permissions Required:
          - Manage Plants Additives

        POST CreateAdditives V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/additives"
        return self._send("POST", path, body, query_params)

    def plants_create_additives_bylocation_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Plants
          - Manage Plants Additives

        POST CreateAdditivesBylocation V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/additives/bylocation"
        return self._send("POST", path, body, query_params)

    def plants_create_additives_bylocation_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records additive usage for plants based on their location within a specified Facility.
        
          Permissions Required:
          - Manage Plants
          - Manage Plants Additives

        POST CreateAdditivesBylocation V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/additives/bylocation"
        return self._send("POST", path, body, query_params)

    def plants_create_additives_bylocation_usingtemplate_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records additive usage for plants by location using a predefined additive template at a specified Facility.
        
          Permissions Required:
          - Manage Plants Additives

        POST CreateAdditivesBylocationUsingtemplate V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/additives/bylocation/usingtemplate"
        return self._send("POST", path, body, query_params)

    def plants_create_additives_usingtemplate_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records additive usage for plants using predefined additive templates at a specified Facility.
        
          Permissions Required:
          - Manage Plants Additives

        POST CreateAdditivesUsingtemplate V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/additives/usingtemplate"
        return self._send("POST", path, body, query_params)

    def plants_create_changegrowthphases_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreateChangegrowthphases V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/changegrowthphases"
        return self._send("POST", path, body, query_params)

    def plants_create_harvestplants_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        NOTE: If HarvestName is excluded from the request body, or if it is passed in as null, the harvest name is auto-generated.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manicure/Harvest Veg/Flower Plants

        POST CreateHarvestplants V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/harvestplants"
        return self._send("POST", path, body, query_params)

    def plants_create_manicure_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates harvest product records from plant batches at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manicure/Harvest Veg/Flower Plants

        POST CreateManicure V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/manicure"
        return self._send("POST", path, body, query_params)

    def plants_create_manicureplants_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants
          - Manicure/Harvest Veg/Flower Plants

        POST CreateManicureplants V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/manicureplants"
        return self._send("POST", path, body, query_params)

    def plants_create_moveplants_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreateMoveplants V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/moveplants"
        return self._send("POST", path, body, query_params)

    def plants_create_plantbatch_package_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePlantbatchPackage V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/create/plantbatch/packages"
        return self._send("POST", path, body, query_params)

    def plants_create_plantbatch_package_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages from plant batches at a specified Facility.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePlantbatchPackage V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/plantbatch/packages"
        return self._send("POST", path, body, query_params)

    def plants_create_plantings_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreatePlantings V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/create/plantings"
        return self._send("POST", path, body, query_params)

    def plants_create_plantings_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new plant batches at a specified Facility from existing plant data.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreatePlantings V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/plantings"
        return self._send("POST", path, body, query_params)

    def plants_create_waste_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Plants Waste

        POST CreateWaste V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/waste"
        return self._send("POST", path, body, query_params)

    def plants_create_waste_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Records waste events for plants at a Facility, including method, reason, and location details.
        
          Permissions Required:
          - Manage Plants Waste

        POST CreateWaste V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/waste"
        return self._send("POST", path, body, query_params)

    def plants_delete_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants
          - Destroy Veg/Flower Plants

        DELETE Delete V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1"
        return self._send("DELETE", path, body, query_params)

    def plants_delete_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Removes plants from a Facility’s inventory while recording the reason for their disposal.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Destroy Veg/Flower Plants

        DELETE Delete V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2"
        return self._send("DELETE", path, body, query_params)

    def plants_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET Get V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def plants_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Plant by Id.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET Get V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/{urllib.parse.quote(id)}"
        return self._send("GET", path, body, query_params)

    def plants_get_additives_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View/Manage Plants Additives

        GET GetAdditives V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/additives"
        return self._send("GET", path, body, query_params)

    def plants_get_additives_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves additive records applied to plants at a specified Facility.
        
          Permissions Required:
          - View/Manage Plants Additives

        GET GetAdditives V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/additives"
        return self._send("GET", path, body, query_params)

    def plants_get_additives_types_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          -

        GET GetAdditivesTypes V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/plants/v1/additives/types"
        return self._send("GET", path, body, query_params)

    def plants_get_additives_types_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves a list of all plant additive types defined within a Facility.
        
          Permissions Required:
          - None

        GET GetAdditivesTypes V2
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/plants/v2/additives/types"
        return self._send("GET", path, body, query_params)

    def plants_get_by_label_v1(self, label: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET GetByLabel V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/{urllib.parse.quote(label)}"
        return self._send("GET", path, body, query_params)

    def plants_get_by_label_v2(self, label: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Plant by label.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET GetByLabel V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/{urllib.parse.quote(label)}"
        return self._send("GET", path, body, query_params)

    def plants_get_flowering_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET GetFlowering V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/flowering"
        return self._send("GET", path, body, query_params)

    def plants_get_flowering_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves flowering-phase plants at a specified Facility, optionally filtered by last modified date.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET GetFlowering V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/flowering"
        return self._send("GET", path, body, query_params)

    def plants_get_growth_phases_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetGrowthPhases V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/growthphases"
        return self._send("GET", path, body, query_params)

    def plants_get_growth_phases_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves the list of growth phases supported by a specified Facility.
        
          Permissions Required:
          - None

        GET GetGrowthPhases V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/growthphases"
        return self._send("GET", path, body, query_params)

    def plants_get_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET GetInactive V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/inactive"
        return self._send("GET", path, body, query_params)

    def plants_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves inactive plants at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET GetInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/inactive"
        return self._send("GET", path, body, query_params)

    def plants_get_mother_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves mother-phase plants at a specified Facility.
        
          Permissions Required:
          - View Mother Plants

        GET GetMother V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/mother"
        return self._send("GET", path, body, query_params)

    def plants_get_mother_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves inactive mother-phase plants at a specified Facility.
        
          Permissions Required:
          - View Mother Plants

        GET GetMotherInactive V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/mother/inactive"
        return self._send("GET", path, body, query_params)

    def plants_get_mother_onhold_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves mother-phase plants currently marked as on hold at a specified Facility.
        
          Permissions Required:
          - View Mother Plants

        GET GetMotherOnhold V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/mother/onhold"
        return self._send("GET", path, body, query_params)

    def plants_get_onhold_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET GetOnhold V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/onhold"
        return self._send("GET", path, body, query_params)

    def plants_get_onhold_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves plants that are currently on hold at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET GetOnhold V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/onhold"
        return self._send("GET", path, body, query_params)

    def plants_get_vegetative_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET GetVegetative V1
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/vegetative"
        return self._send("GET", path, body, query_params)

    def plants_get_vegetative_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves vegetative-phase plants at a specified Facility, optionally filtered by last modified date.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET GetVegetative V2
        """
        query_params = {}
        if last_modified_end is not None:
            query_params["lastModifiedEnd"] = last_modified_end
        if last_modified_start is not None:
            query_params["lastModifiedStart"] = last_modified_start
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/vegetative"
        return self._send("GET", path, body, query_params)

    def plants_get_waste_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of recorded plant waste events for a specific Facility.
        
          Permissions Required:
          - View Plants Waste

        GET GetWaste V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/waste"
        return self._send("GET", path, body, query_params)

    def plants_get_waste_methods_all_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetWasteMethodsAll V1
        """
        query_params = {}
        if no is not None:
            query_params["No"] = no
        path = f"/plants/v1/waste/methods/all"
        return self._send("GET", path, body, query_params)

    def plants_get_waste_methods_all_v2(self, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of all available plant waste methods for use within a Facility.
        
          Permissions Required:
          - None

        GET GetWasteMethodsAll V2
        """
        query_params = {}
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/waste/methods/all"
        return self._send("GET", path, body, query_params)

    def plants_get_waste_package_v2(self, id: str, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of package records linked to the specified plantWasteId for a given facility.
        
          Permissions Required:
          - View Plants Waste

        GET GetWastePackage V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/waste/{urllib.parse.quote(id)}/package"
        return self._send("GET", path, body, query_params)

    def plants_get_waste_plant_v2(self, id: str, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of plants records linked to the specified plantWasteId for a given facility.
        
          Permissions Required:
          - View Plants Waste

        GET GetWastePlant V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/waste/{urllib.parse.quote(id)}/plant"
        return self._send("GET", path, body, query_params)

    def plants_get_waste_reasons_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetWasteReasons V1
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v1/waste/reasons"
        return self._send("GET", path, body, query_params)

    def plants_get_waste_reasons_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retriveves available reasons for recording mature plant waste at a specified Facility.
        
          Permissions Required:
          - None

        GET GetWasteReasons V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        if page_number is not None:
            query_params["pageNumber"] = page_number
        if page_size is not None:
            query_params["pageSize"] = page_size
        path = f"/plants/v2/waste/reasons"
        return self._send("GET", path, body, query_params)

    def plants_update_adjust_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Adjusts the recorded count of plants at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateAdjust V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/adjust"
        return self._send("PUT", path, body, query_params)

    def plants_update_growthphase_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Changes the growth phases of plants within a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateGrowthphase V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/growthphase"
        return self._send("PUT", path, body, query_params)

    def plants_update_harvest_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Processes whole plant Harvest data for a specific Facility. NOTE: If HarvestName is excluded from the request body, or if it is passed in as null, the harvest name is auto-generated.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manicure/Harvest Veg/Flower Plants

        PUT UpdateHarvest V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/harvest"
        return self._send("PUT", path, body, query_params)

    def plants_update_location_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Moves plant batches to new locations within a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateLocation V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/location"
        return self._send("PUT", path, body, query_params)

    def plants_update_merge_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Merges multiple plant groups into a single group within a Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manicure/Harvest Veg/Flower Plants

        PUT UpdateMerge V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/merge"
        return self._send("PUT", path, body, query_params)

    def plants_update_split_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Splits an existing plant group into multiple groups within a Facility.
        
          Permissions Required:
          - View Plant

        PUT UpdateSplit V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/split"
        return self._send("PUT", path, body, query_params)

    def plants_update_strain_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the strain information for plants within a Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateStrain V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/strain"
        return self._send("PUT", path, body, query_params)

    def plants_update_tag_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Replaces existing plant tags with new tags for plants within a Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateTag V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/plants/v2/tag"
        return self._send("PUT", path, body, query_params)

    def retail_id_create_associate_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Facilitate association of QR codes and Package labels. This will return the count of packages and QR codes associated that were added or replaced.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write)
          - WebApi Retail ID Read Write State (All or WriteOnly)
          - Industry/View Packages
          - One of the following: Industry/Facility Type/Can Receive Associate Product Label, Licensee/Receive Associate Product Label or Admin/Employees/Packages Page/Product Labels(Manage)

        POST CreateAssociate V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/retailid/v2/associate"
        return self._send("POST", path, body, query_params)

    def retail_id_create_generate_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Allows you to generate a specific quantity of QR codes. Id value returned (issuance ID) could be used for printing.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write)
          - WebApi Retail ID Read Write State (All or WriteOnly)
          - Industry/View Packages
          - One of the following: Industry/Facility Type/Can Download Product Label, Licensee/Download Product Label or Admin/Employees/Packages Page/Product Labels(Manage)

        POST CreateGenerate V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/retailid/v2/generate"
        return self._send("POST", path, body, query_params)

    def retail_id_create_merge_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Merge and adjust one source to one target Package. First Package detected will be processed as target Package. This requires an action reason with name containing the 'Merge' word and setup with 'Package adjustment' area.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write)
          - WebApi Retail ID Read Write State (All or WriteOnly)
          - Key Value Settings/Retail ID Merge Packages Enabled

        POST CreateMerge V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/retailid/v2/merge"
        return self._send("POST", path, body, query_params)

    def retail_id_create_package_info_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves Package information for given list of Package labels.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write)
          - WebApi Retail ID Read Write State (All or WriteOnly)
          - Industry/View Packages
          - Admin/Employees/Packages Page/Product Labels(Manage)

        POST CreatePackageInfo V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/retailid/v2/packages/info"
        return self._send("POST", path, body, query_params)

    def retail_id_get_receive_by_label_v2(self, label: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Get a list of eaches (Retail ID QR code URL) and sibling tags based on given Package label.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Manage RetailId
          - WebApi Retail ID Read Write State (All or ReadOnly)
          - Industry/View Packages
          - One of the following: Industry/Facility Type/Can Receive Associate Product Label, Licensee/Receive Associate Product Label or Admin/Employees/Packages Page/Product Labels(View or Manage)

        GET GetReceiveByLabel V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/retailid/v2/receive/{urllib.parse.quote(label)}"
        return self._send("GET", path, body, query_params)

    def retail_id_get_receive_qr_by_short_code_v2(self, short_code: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Get a list of eaches (Retail ID QR code URL) and sibling tags based on given short code value (first segment in Retail ID QR code URL).
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Manage RetailId
          - WebApi Retail ID Read Write State (All or ReadOnly)
          - Industry/View Packages
          - One of the following: Industry/Facility Type/Can Receive Associate Product Label, Licensee/Receive Associate Product Label or Admin/Employees/Packages Page/Product Labels(View or Manage)

        GET GetReceiveQrByShortCode V2
        """
        query_params = {}
        if license_number is not None:
            query_params["licenseNumber"] = license_number
        path = f"/retailid/v2/receive/qr/{urllib.parse.quote(short_code)}"
        return self._send("GET", path, body, query_params)

