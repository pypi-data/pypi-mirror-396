# setup.py

from setuptools import find_packages, setup

setup(
    name="pcp_serversdk_python",
    version="1.5.0",
    author="PAYONE-GmbH",
    author_email="",
    description="",
    long_description=open("README.md").read(),  # noqa: SIM115
    long_description_content_type="text/markdown",
    url="https://github.com/PAYONE-GmbH/PCP-ServerSDK-python",
    keywords="payone, pcp, server, python, sdk",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),  # noqa: SIM115
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
