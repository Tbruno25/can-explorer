from setuptools import setup

setup(
    name="CanoPy",
    version="0.1",
    description="visualize CAN bus payloads in real time",
    long_description="",
    classifiers=[],
    keywords="CAN canbus ",
    author="TJ Bruno",
    author_email="tbruno25@gmail.com",
    url="",
    license="MIT",
    packages=["canopy"],
    zip_safe=False,
    install_requires=[
        "PyQT5",
        "pyqtgraph",
        "pyserial",
        "python-can",
    ],
    entry_points="""
      [console_scripts]
      canopy = canopy.cli:main
      """,
)
