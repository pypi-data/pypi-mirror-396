from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nishkoder-ai-common",
    version="0.1.4",
    author="nishkoder",
    description="Common utilities for AI projects including logging and exceptions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain-google-genai",
        "langchain-groq",
        "python-dotenv",
        "PyYAML",
    ],
)
