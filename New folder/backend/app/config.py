from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    app_name: str = "HIVCare AI"
    secret_key: str = "change-me-in-production-use-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./hivcare.db"
    ml_model_path: str = "../ml/artifacts/model.pkl"
    ml_metrics_path: str = "../ml/artifacts/metrics.json"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def model_path(self) -> str:
        return self.ml_model_path

    @property
    def metrics_path(self) -> str:
        return self.ml_metrics_path


settings = Settings()
