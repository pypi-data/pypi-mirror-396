from setuptools import setup, find_packages

setup(
    name="EitaaSender",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.8",
    description="A Python library to send messages and files via Eitaa API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alireza-sadeghian/EitaaSender",
    author="Alireza Sadeghian",
    author_email="alireza.amid110@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)