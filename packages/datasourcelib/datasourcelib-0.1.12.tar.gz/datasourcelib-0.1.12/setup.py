from setuptools import setup, find_packages

setup(
    name="datasourcelib",
    version="0.1.12",
    packages=find_packages(where="src", exclude=["tests.*", "tests", "examples.*", "examples"]),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.68.0",
        "pydantic>=1.10.0",
        "uvicorn>=0.17.0"
    ],
    description="Data source sync strategies for vector DBs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Akash Kumar Maurya",
    author_email="mrelectronicsarduino@gmail.com",
    url="https://github.com/akashmaurya0217/datasourcelib",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
)