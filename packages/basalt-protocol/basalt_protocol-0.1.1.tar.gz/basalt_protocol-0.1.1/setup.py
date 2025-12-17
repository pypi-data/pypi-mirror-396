from setuptools import setup, find_packages

setup(
    name="basalt-protocol",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "grpcio>=1.60.0",
        "grpcio-tools>=1.60.0",
        "protobuf>=4.25.0",
    ],
    python_requires=">=3.8",
    description="Basalt gRPC protocol definitions",
    url="https://github.com/psila-ai/basalt-protocol",
    license="MIT",
)
