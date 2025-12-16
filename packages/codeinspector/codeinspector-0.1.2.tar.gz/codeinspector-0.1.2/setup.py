from setuptools import setup, find_packages

setup(
    name="codeinspector",
    version="0.1.2",
    packages=find_packages(),
    author="Pranay & Gnanesh",
    author_email="pranaykesava@gmail.com",
    description="An AI-powered Senior Engineer Agent for your terminal.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pranaykesava/code-inspector-ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "click",
        "gitpython",
        "pygithub",
        "google-generativeai",
        "flake8",
        "pytest",
        "coverage",
        "PyYAML",
    ],
    entry_points={
        "console_scripts": [
            "codeinspector=codeinspector.cli:codeinspector",
        ],
    },
)
