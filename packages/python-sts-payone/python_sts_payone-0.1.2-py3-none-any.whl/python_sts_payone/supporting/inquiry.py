from requests.models import Response
from typing import Tuple
from ..base.request_handler import SmartRouteRequestHandler
from ..base.utils import SR_URL_SUPPORT_TEST, SR_URL_SUPPORT_LIVE, INQUIRY_MESSAGE_ID


def inquire(merchant_id: str, auth_token: str, transaction_id: str, version: float, live_mode: bool=True) -> Tuple[str, int]:
    params: dict = {
        'MessageID': INQUIRY_MESSAGE_ID,
        'OriginalTransactionID': transaction_id,
        'MerchantID': merchant_id,
        'Version': str(version)
    }
    
    sr_url: str = SR_URL_SUPPORT_LIVE if live_mode else SR_URL_SUPPORT_TEST
    res: Response = SmartRouteRequestHandler(sr_url, auth_token, params).send_request()
    return res.text, res.status_code