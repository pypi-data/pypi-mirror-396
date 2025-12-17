from setuptools import setup, find_packages

setup(
    name="keviusdb",
    version="1.0.9",
    description="Persistent Memory for AI Agents | Fast Key-Value Storage with Agent Memory capabilities",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/iv4n-ga6l/KeviusDB',  
    author="Ivan APEDO",
    author_email='apedoivan@gmail.com',
    packages=find_packages(),
    install_requires=[
        "lz4>=4.0.0",  # Fast compression
        "sortedcontainers>=2.4.0",  # Efficient sorted data structures
        "pycache-handler",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
