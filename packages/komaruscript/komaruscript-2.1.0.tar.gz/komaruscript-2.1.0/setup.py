from setuptools import setup, find_packages

setup(
    name="komaruscript",
    version="2.1.0",
    author="KomaruEat",
    description="A Python-based programming language with cat commands! \U0001f431",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "pyTelegramBotAPI"
    ],
    entry_points={
        "console_scripts": [
            "komaru=komaruscript.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
