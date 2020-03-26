import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jumpscale11",
    version="11.0.0",
    author="Kristof",
    author_email="kristof@incubaid.com",
    description="the core library set for jumpscale X1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/threefoldtech/jumpscaleXI_core",
    packages=setuptools.find_packages(),
    install_requires=[
        "redis",
        "pyyaml",
        "click>=6.6",
        "ujson",
        "msgpack",
        "path.py>=10.3.1",
        "psutil>=5.4.3",
        "pudb>=2017.1.2",
        "pytoml>=0.1.2",
        "requests>=2.13.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
