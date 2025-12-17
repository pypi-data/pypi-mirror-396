from setuptools import setup, find_packages

setup(
    name="uniorm",
    version="1.0.0",
    author="oscoderuz",
    author_email="oscoderuz@gmail.com",
    description="Universal Async ORM for SQLite, MySQL, and PostgreSQL",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/oscoderuz/uniorm",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "sqlite": ["aiosqlite"],
        "mysql": ["asyncmy"],
        "postgres": ["psycopg[binary]"],
        "all": [
            "aiosqlite",
            "asyncmy",
            "psycopg[binary]"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Topic :: Database :: Front-Ends",
    ],
)