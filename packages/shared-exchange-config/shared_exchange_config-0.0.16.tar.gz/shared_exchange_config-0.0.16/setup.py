from setuptools import setup, find_packages
import os

setup(
    name="shared-exchange-config",
    version="0.0.16",
    description="Python library for managing cryptocurrency exchange configurations",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="Dmitrii",
    author_email="dp@exan.tech",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "exchange_config": ["data/*.json"]
    },
    install_requires=[
        # No external dependencies needed
    ],
    license='EULA',
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
) 
