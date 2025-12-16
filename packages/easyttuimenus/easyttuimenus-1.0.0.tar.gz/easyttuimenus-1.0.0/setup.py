from setuptools import setup, find_packages


setup(
    name="easyttuimenus",  
    version="1.0.0",
    description="Write simple UI for your code in seconds in a unified way using Easy TTUI Menus",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="sarcasticDweller",
    packages=find_packages(),
    python_requires=">=3.6",
)