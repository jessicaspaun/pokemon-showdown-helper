from setuptools import setup, find_packages

setup(
    name="pokemon_showdown_helper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.1.0",
        "beautifulsoup4>=4.12.0",
        "streamlit>=1.29.0",
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
        "flake8>=6.1.0",
        "black>=23.11.0",
        "pytest>=7.4.0",
    ],
) 