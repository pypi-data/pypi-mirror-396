from setuptools import setup, find_packages

setup(
    name="scrapscraper",  
    version="2.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "colorama"
    ],
    entry_points={
    "console_scripts": [
        "scraper=scrapscraper.scrapscraper:main",  # this is correct
    ],
},

    author="skelliyB/lemonsrC00l",  # your name or handle
    description="A fun Python web scraper if you need me comment on the github page lemonsrC00l is just my alt",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/skelliyB/scrapscraper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
