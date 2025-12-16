from setuptools import setup, find_packages

setup(
    name="scrapscraper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "colorama",
    ],
    entry_points={
        "console_scripts": [
            "scrapscraper=scrapscraper.main:main",
        ],
    },
)
