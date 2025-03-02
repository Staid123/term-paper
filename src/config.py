from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra="ignore")


class PostgresDatabaseSettings(CommonSettings):
    postgres_host: str
    postgres_port: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    database_url: str


class SMTPSettings(CommonSettings):
    smtp_user: str
    smtp_password: str
    smtp_host: str
    smtp_port: str


class AWSSettings(CommonSettings):
    bucket_name: str
    aws_access_key_id: str
    aws_secret_access_key: str


class Settings:
    db: PostgresDatabaseSettings = PostgresDatabaseSettings()
    aws: AWSSettings = AWSSettings()
    smtp: SMTPSettings = SMTPSettings()


settings: Settings = Settings()

if __name__ == "__main__":
    print(settings.db.model_dump())
    print(settings.aws.model_dump())
    print(settings.smtp.model_dump())