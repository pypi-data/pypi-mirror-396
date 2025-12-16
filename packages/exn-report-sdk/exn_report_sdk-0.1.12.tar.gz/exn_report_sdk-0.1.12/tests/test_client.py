from exn_salon_report_sdk.client import ReportClient
from exn_salon_report_sdk.utils import serialize_payload

client = ReportClient(
    api_key="api_key",
    secret_key="secret_key",
    # base_url="http://192.168.1.4:8000",
    ref_id=2153,
    offset=7,
)

res = client.get_list_report(
    body=None,
    params={"from_date": "2024-12-01", "to_date": "2024-12-24", "report_type": "SALE"},
)
print("response: ", res)

data = {
    "id": 19163,
    "obj_type": "BOOKING",
    "invoice_id": 14960,
    "payment_status": "PAID",
    "customer": None,
    "contact": None,
    "branch": 2612,
    "quick_discount": 0.0,
    "voucher_discount": 0,
    "loyalty_discount": 0,
    "transaction": {
        "id": 17069,
        "creator": 3467,
        "updater": 3467,
        "isDeleted": False,
        "deletedAt": None,
        "payloadData": {
            "merchant_defined_fields": {
                "1": "BB1737600741",
                "2": 19163,
                "3": "PAYMENT",
                "4": [],
                "9": 0,
                "11": 3467,
            },
            "requested_amount": 20,
            "tip": 0,
        },
        "transactionId": "259321162038",
        "status": "COMPLETE",
        "type": "PAYMENT",
        "amount": 20.0,
        "tip": 0.0,
        "tax": 0.0,
        "change": 0.0,
        "total_amount": 20.0,
        "currency": "USD",
        "sourceType": "CASH",
        "note": None,
        "originalTransaction": None,
        "paymentGateway": None,
        "signature": None,
        "transaction_type": "BOOKING",
        "terminalName": None,
        "closeDate": None,
        "batchNumber": None,
        "isBatched": None,
        "batchInfo": None,
    },
    "details": [
        {
            "id": 1001,
            "price": 20.0,
            "productCharge": 0.0,
            "productChargeType": "FIXED_AMOUNT",
            "addons": [],
        }
    ],
}

post_res = client.push_data_report(
    body=data,
    params={},
)
print("post response: ", post_res.content)
