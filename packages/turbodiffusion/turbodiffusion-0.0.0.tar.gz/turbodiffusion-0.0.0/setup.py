# setup.py
from setuptools import setup, find_packages

setup(
    name="turbodiffusion",
    version="0.0.0",  # placeholder version
    description="Placeholder package for turbodiffusion (coming soon).",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Jintao Zhang, Kaiwen Zheng, Kai Jiang, Haoxu Wang",
    author_email="jtzhang6@gmail.com",
    url="https://github.com/thu-ml/TurboDiffusion",  # 
    license="Apache-2.0",
    packages=find_packages(),
    python_requires=">=3.9",
)
