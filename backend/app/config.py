from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = "postgresql://postgres:postgres@postgres:5432/marketplace"
    jwt_secret: str = "marketplace-jwt-secret-key-change-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    model_config = {"env_file": ".env"}


settings = Settings()
