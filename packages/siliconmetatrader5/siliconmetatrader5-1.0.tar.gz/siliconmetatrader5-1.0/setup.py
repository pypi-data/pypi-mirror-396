from setuptools import setup, find_packages

setup(
    name="siliconmetatrader5",
    version="1.0",
    author="bahadirumutiscimen",
    author_email="buiscimen@gmail.com",
    description="SiliconMetaTrader5 for macOS Silicon Client",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/buiscimen/siliconmetatrader5",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "rpyc"
    ]
)