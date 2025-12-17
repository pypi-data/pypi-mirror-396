from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings."""

    api_key: str = "change_me"
    secret_key: str = "change_me"
    escalation_policy_id: str = "AB1CD2E"

    class Config:
        """Config."""

        secrets_dir = "/etc/pagerduty-voys-webhook"


settings = Settings()
