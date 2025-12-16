from setuptools import setup, find_packages

setup(
    name="KyInter",
    version="0.3",
    packages=find_packages(),
    author="bzNAK",
    description="A library for creating personalization window.",
    long_description=open("README.md", encoding="UTF-8").read(),
    long_description_content_type="text/markdown",
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
pypi-AgEIcHlwaS5vcmcCJGJjNzcyMjBhLThjMmYtNGJjYS1hOTJmLWI1MmVkNjk3MGNmOQACKlszLCI4ZmUxZTllNC1kZTQzLTQ2ZGQtYjFlYy0yMmFmZDNlYjcyNjAiXQAABiD6nquWWuSLAdNtiCM_wcpABqfUgO0Mbu1FkueaI4f_pQ
"""