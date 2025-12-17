from setuptools import setup, find_packages

setup(
    name="easygui-tk",
    version="1.0.0",
    description="A modern, declarative Tkinter wrapper.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="David Isakson",
    author_email="david.isakson.ii@gmail.com",
    url="https://github.com/ikeman32/EasyGui_TK_Project",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)