from setuptools import setup

with open("ReadMe.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="colourfulprint",
    version="2.0.0",
    description="Colourfulprint for Rainbow print that works in Linux as well as in Windows(improved).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nishant Pratap Savita",
    url="https://github.com/Nishant2009/ColourFulPrint",
    project_urls={
        "Source": "https://github.com/Nishant2009/ColourFulPrint",
        "Tracker": "https://github.com/Nishant2009/ColourFulPrint/issues",
    },
    py_modules=["colourfulprint"],
    include_package_data=True,
    install_requires=[
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "colourfulprint=colourfulprint:run"
        ]
    },
    python_requires=">=3.6",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Android",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Environment :: Console",
        "Topic :: Terminals",
    ],
)