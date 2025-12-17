from setuptools import setup, find_packages

setup(
    name="iotamine",
    version="0.1.1",
    author="Piyush Ladhar",
    author_email="corporate@iotamine.com",
    description="Iotamine Cloud API Python SDK",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/piyushladhar/iotamine",
    project_urls={
        "Documentation": "https://github.com/piyushladhar/iotamine",
        "Source": "https://github.com/piyushladhar/iotamine",
    },
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
