from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mrglang",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="The Simple, Fast & Beautiful Programming Language for Everyone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mrglang",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "discord.py>=2.0.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "mrg=mrglang.cli:main",
        ],
    },
    keywords="programming-language discord bot simple thai",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mrglang/issues",
        "Source": "https://github.com/yourusername/mrglang",
    },
    include_package_data=True,
    zip_safe=False,
)