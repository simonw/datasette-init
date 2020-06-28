from setuptools import setup
import os

VERSION = "0.1a2"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-init",
    description="Ensure specific tables and views exist on startup",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-init",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-init/issues",
        "CI": "https://github.com/simonw/datasette-init/actions",
        "Changelog": "https://github.com/simonw/datasette-init/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_init"],
    entry_points={"datasette": ["init = datasette_init"]},
    install_requires=["datasette>=0.45a3", "sqlite-utils"],
    extras_require={"test": ["pytest", "pytest-asyncio", "httpx"]},
    tests_require=["datasette-init[test]"],
)
