from setuptools import find_packages, setup

setup(
    packages=find_packages(include=["tornadoapi_guard", "tornadoapi_guard.*"]),
    include_package_data=True,
    package_data={
        "tornadoapi_guard": ["py.typed"],
    },
)
