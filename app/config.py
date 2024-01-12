from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL : str
    MONGO_INITDB_DATABASE : str

    ACCESS_TOKEN_EXPIRES_IN : int
    REFRESH_TOKEN_EXPIRES_IN : int
    
    JWT_ALGORITHM : str
    JWT_SECRET_KEY : str
    
    CLIENT_ORIGIN : str

    class Config:
        env_file = ".env"


settings = Settings()