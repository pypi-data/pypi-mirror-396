from setuptools import setup, find_packages

setup(
    name="KyInter",
    version="0.8",
    packages=find_packages(),
    author="bzNAK",
    url="https://github.com/JimmyJimmy666/KyInter",
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
pypi-AgEIcHlwaS5vcmcCJGE5ZmJlNzM4LTlkODUtNGEzMC1hMTA3LTc5NjBlYjE5MTg5ZQACD1sxLFsia3lpbnRlciJdXQACLFsyLFsiN2U5OTljYmItNjQ0YS00ODJmLThhMjktNjFjNjk4OGNjZWVjIl1dAAAGIIrTAnwIjdVijiMeZaoRMMZOrr3p2T0bLyLf7Xc6IR7E
"""