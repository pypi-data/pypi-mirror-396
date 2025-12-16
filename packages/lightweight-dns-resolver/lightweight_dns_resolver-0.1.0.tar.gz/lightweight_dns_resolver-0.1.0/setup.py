from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="lightweight-dns-resolver",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dns-resolve=dns_resolver.cli:main', 
        ],
    },
    author="MissyTech",
    description="A pure Python DNS resolver supporting multiple record types",
    long_description=README,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    include_package_data=True,
    install_requires=[]
)
