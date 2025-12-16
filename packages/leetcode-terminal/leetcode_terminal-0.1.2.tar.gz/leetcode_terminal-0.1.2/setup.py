from setuptools import setup, find_packages

setup(
    name="leetcode-terminal",  # CLI command
    version="0.1.2",
    description="LeetCLI - Solve, practice, and fetch LeetCode challenges from your terminal",
     long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Chitransh Saxena",
    author_email="geniussaxena007@gmail.com",
    url="https://github.com/Chitransh2309",  # optional, GitHub repo URL if any
    packages=find_packages(include=["*", "leet*"]),
    python_requires=">=3.7",
    install_requires=[
        "typer[all]>=0.9.0",
        "requests>=2.30.0",
        "rich>=13.0.0",
        "html2text",
    ],
    entry_points={
        "console_scripts": [
            "lc=leetcli.main:app",  # CLI command points to main.py Typer app
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # change if needed
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    include_package_data=True,
)
