# STS PayOne

A package that provides utility functions to send payment requests to STS PayOne and interpret the responses
Documentation coming soon.

STS PayOne Documentation: https://payone.document360.io/docs

Install: pip install python-sts-payone


Usage:

import uuid

from python_sts_payone.redirect_model.redirection_model_pay import redirect_model_pay

redirect_model_pay(merchant_id=YOUR_MERCHANT_ID, auth_token=YOUR_AUTH_TOKEN, transaction_id=str(uuid.uuid4()), amount=200, currency_iso_code='840', response_back_url=URL_OF_YOUR_CALLBACK_API)



[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
