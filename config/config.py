# -----------------------------------------------------------
# Ryzobus v1.1
# Class to load config from YAML parameter file
# where the full suite of configuration settings for
# runtime are provided.
#
# Used by pid module and parameter module
#
# (C) 2021 Hayden Eastwood,
# Contact: hayden.eastwood@gmail.com, +263 779 451 256
# -----------------------------------------------------------

from yaml import load as yaml_loader
from yaml.loader import SafeLoader
from yaml.scanner import ScannerError
from yaml.parser import ParserError
import os


class Config:
    yaml_file_name = "config.yaml"
    yaml_directory = "config"
    _config = None

    def __new__(cls) -> dict:
        if cls._config is None:
            real_path = os.path.realpath(__file__)
            yaml_file_location = f"{os.path.dirname(real_path)}/{cls.yaml_file_name}"
            cls._config = cls.__read_yaml_config(yaml_file_location)
        return cls._config

    @staticmethod
    def __read_yaml_config(file_name: str) -> dict:
        """Open YAML parameter file

        Input: file name
        Output: dictionary of config
        """
        try:
            with open(file_name) as f:
                config = yaml_loader(f, Loader=SafeLoader)
        except FileNotFoundError:
            error_message = f"No parameter file found by name of {file_name}."
            raise FileNotFoundError(error_message)
        except ScannerError:
            error_message = "YAML parameter file has formatting errors in it."
            raise IOError(error_message)
        except ParserError:
            error_message = "YAML parameter file could not be read, it likely has indentation problems."
            raise IOError(error_message)
        return config


settings = Config()
