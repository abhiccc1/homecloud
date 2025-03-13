from setuptools import setup
import configparser

def load_dependencies():
    """Reads dependencies from config.ini and returns a list."""
    config = configparser.ConfigParser()
    config.read("config.ini")

    return [f"{pkg}{version}" for pkg, version in config["dependencies"].items()]

setup(
    name="homecloud",
    version="0.1.0",
    install_requires=load_dependencies(),
)
