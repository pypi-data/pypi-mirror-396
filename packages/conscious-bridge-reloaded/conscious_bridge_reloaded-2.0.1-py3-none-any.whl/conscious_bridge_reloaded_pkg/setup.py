from setuptools import setup

setup(
    name="conscious-bridge-reloaded",
    version="2.0.1",
    py_modules=["server", "test_server"],  # List your main modules here
    install_requires=["flask>=2.0.0"],
    entry_points={
        "console_scripts": [
            "cb-reloaded=server:main",  # Adjust based on your actual module
        ],
    },
)
