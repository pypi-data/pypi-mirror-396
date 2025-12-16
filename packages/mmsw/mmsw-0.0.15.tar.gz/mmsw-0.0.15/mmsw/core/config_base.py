"""
Config Base

author: Hyungkoo.kim
"""

import os

class ConfigBase():

    __configBaseInstance = None

    @classmethod
    def get_config(cls):
        return cls.__configBaseInstance

    @classmethod
    def set_config(cls, config):
        cls.__configBaseInstance = config


    APP_ENV: str = os.getenv("APP_ENV", "dev")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    
    DB_SCHEME: str = os.getenv("DB_SCHEME")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_USER: str = os.getenv("DB_USER")
    DB_PWD: str = os.getenv("DB_PWD")
    DB_NAME: str = os.getenv("DB_NAME")

    MODEL_NAME: str = os.getenv("MODEL_NAME")
    MODEL_WORKER: str = os.getenv("MODEL_WORKER")

    IMAGE_ROOT: str = os.getenv("IMAGE_ROOT")
    IMAGE_HOST: str = os.getenv("IMAGE_HOST")

    RESULT_URL: str = os.getenv("RESULT_URL")

    SLACK_URL: str = os.getenv("SLACK_URL")

    #SQLALCHEMY_DATABASE_URI: str = None

    class Config:
        case_sensitive = True


def get_config_base() -> ConfigBase:
    return ConfigBase.get_config()


def set_config_base(config: ConfigBase):
    ConfigBase.set_config(config)

