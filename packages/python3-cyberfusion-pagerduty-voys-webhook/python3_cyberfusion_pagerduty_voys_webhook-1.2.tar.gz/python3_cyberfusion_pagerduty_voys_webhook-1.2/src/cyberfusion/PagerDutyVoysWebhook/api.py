from fastapi import FastAPI

from cyberfusion.PagerDutyVoysWebhook.pagerduty import PagerDutyAPI
from cyberfusion.PagerDutyVoysWebhook.settings import settings
from cyberfusion.PagerDutyVoysWebhook.voys import (
    construct_webhook_response_destination,
    construct_webhook_response_wrong_input,
)
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/voys-webhook", response_class=PlainTextResponse)  # type: ignore[untyped-decorator]
def voys_webhook(secret_key: str) -> PlainTextResponse:
    """Return destination in Voys' webhook format."""
    if secret_key != settings.secret_key:
        return PlainTextResponse(
            construct_webhook_response_wrong_input(), status_code=401
        )

    pagerduty_api = PagerDutyAPI(api_key=settings.api_key)

    random_on_call_user = pagerduty_api.get_random_on_call(
        escalation_policy_id=settings.escalation_policy_id
    )
    random_phone_contact_method = pagerduty_api.get_random_phone_contact_method(
        random_on_call_user["user"]["id"]
    )

    phone_number = (
        "+"
        + str(random_phone_contact_method["country_code"])
        + random_phone_contact_method["address"]
    )

    return PlainTextResponse(
        construct_webhook_response_destination(phone_number), status_code=200
    )
