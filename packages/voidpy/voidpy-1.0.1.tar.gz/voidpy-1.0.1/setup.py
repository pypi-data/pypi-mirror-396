from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="voidpy",
    version="1.0.0",
    author="MERO",
    author_email="mero@voidpy.dev",
    description="Void Execution Engine - Translates Python to Logic States",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MERO/voidpy",
    project_urls={
        "Telegram": "https://t.me/QP4RM",
        "Documentation": "https://github.com/MERO/voidpy#readme",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.6",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "voidpy=voidpy.cli:main",
        ],
    },
    keywords=["encryption", "obfuscation", "bytecode", "void", "logic-states", "protection", "security"],
)
