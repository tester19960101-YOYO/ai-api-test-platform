from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI API Test Platform"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    environment: str = "local"
    log_level: str = "INFO"
    cors_origins: str = "*"
    database_url: str = "mysql+pymysql://ai_test:ai_test@127.0.0.1:3306/ai_api_test_platform"
    ai_provider: str = "openai"
    ai_api_base_url: str = "https://api.openai.com/v1"
    ai_api_key: str = ""
    ai_model_name: str = "gpt-4o-mini"
    ai_request_timeout: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
