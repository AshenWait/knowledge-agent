from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    app_name: str = "Knowledge Agent"
    app_version: str = "0.1.0"
    environment: str = "local"
    database_url:str
    #告诉 Pydantic：请从项目根目录的 .env 文件读取配置，编码用 utf-8。
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

