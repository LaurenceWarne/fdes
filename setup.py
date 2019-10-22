from setuptools import setup, find_packages


setup(
    name="fdes",
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3',
    url="https://github.com/jmh2012/fdes",
    author="jmh2012",
    entry_points={
        "console_scripts":
        [
            "fdes=fdes.fdes:main"
        ],
    },
    install_requires=[
        "prettytable",
        "configparser"
    ],
)
