import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "ez-constructs",
    "version": "0.0.64",
    "description": "A collection of high level patterns for creating standard resources in every project",
    "license": "Apache-2.0",
    "url": "https://github.com/SavvyTools/ez-constructs.git",
    "long_description_content_type": "text/markdown",
    "author": "Biju Joseph<biju.joseph@semanticbits.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/SavvyTools/ez-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "ez_constructs",
        "ez_constructs._jsii"
    ],
    "package_data": {
        "ez_constructs._jsii": [
            "ez-constructs@0.0.64.jsii.tgz"
        ],
        "ez_constructs": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.170.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.112.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
