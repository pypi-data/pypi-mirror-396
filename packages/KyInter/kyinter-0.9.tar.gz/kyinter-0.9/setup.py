from setuptools import setup, find_packages

setup(
    name="KyInter",
    version="0.9",
    packages=find_packages(),
    author="bzNAK",
    url="https://github.com/JimmyJimmy666/KyInter",
    description="A library for creating personalization window.",
    long_description=open("README.md", encoding="UTF-8").read(),
    long_description_content_type="text/markdown",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

"""
C:/Users/Administrator/.virtualenvs/Codes-QQlkIAcD/Scripts/python.exe setup.py sdist bdist_wheel
twine upload dist/*
"""