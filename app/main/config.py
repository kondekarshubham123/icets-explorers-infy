import os
import json

basedir = os.path.abspath(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))))

DEBUG = False

user_config_filepath = os.path.join(
    basedir, "configs","user_configs.json"
)

with open(user_config_filepath) as f:
    user_config = json.load(f)

cur_profile = os.environ['PROFILE'] if "PROFILE" in os.environ else user_config["profile"]
print(f"Using profile {cur_profile}")


class Config:

    @staticmethod
    def get_application_version():
        return user_config["version"]

    @staticmethod
    def get_value(key):
        profile = cur_profile or "dev"
        if key in user_config["profile"]:
            return user_config[profile][key]
        elif key in user_config["default"]:
            return user_config["default"][key]
        raise Exception(
            "Could not find "+ key + " in profile " + profile + " or default"
        )
    
    def __init__(self, app_id) -> None:
        
        self.BASEDIR = os.path.abspath(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))))

        self.CONFIGS_PATH = os.path.join(self.BASEDIR, "configs")
        self.CONFIG_FILE_NAME = os.path.join(self.CONFIGS_PATH,"config.json")

        with open(self.CONFIGS_PATH) as f:
            self.CONFIG_JSON = json.load(f)
            