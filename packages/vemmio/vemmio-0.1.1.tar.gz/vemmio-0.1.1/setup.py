from setuptools import setup, find_packages

setup(
    name="vemmio",
    version="0.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "aiohttp",
        "backoff",
        "orjson",
        "mashumaro",
        "yarl",
    ],
)
