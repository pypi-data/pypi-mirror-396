from setuptools import setup, find_packages

setup(
    name="suficloud",
    version="2.0.0",
    author="Sufiyan",
    author_email="abcdxyz@email.com",
    description="Secure Cloud Storage Service",
    long_description="Secure Cloud Storage Service By Sufiyan",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Android",
    ],
    python_requires='>=3.6',
)
