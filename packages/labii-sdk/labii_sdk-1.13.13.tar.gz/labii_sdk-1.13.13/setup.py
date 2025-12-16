import setuptools
import os
from labii_sdk_core.sdk import get_version

long_description = open("README.md").read()
required = ["requests>=2.27.1", "boto3>=1.20.38"] # Comma seperated dependent libraries name
version = get_version()

setuptools.setup(
    name="labii-sdk",
    version=version, # eg:1.0.0
    author="Labii Inc.",
    author_email="developer@labii.com",
    license="GNU GPLv3",
    description="An SDK for the Labii ELN & LIMS platform (https://www.labii.com) that provides interaction with the Labii API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/labii-dev/labii-sdk-python",
    packages = ['labii_sdk'],
    include_package_data=True,
    project_urls={
        "Bug Tracker": "https://gitlab.com/labii-dev/labii-sdk-python/-/issues",
    },
    key_words="Labii, Labii ELN & LIMS, ELN, LIMS, SDK, Electronic Lab Notebook, Laboratory Information Management System",
    install_requires=required,
    python_requires=">=3.8",
)
