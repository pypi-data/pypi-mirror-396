from setuptools import setup

# قراءة README.md بشكل صحيح
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="conscious-bridge-reloaded",
    version="2.0.2",
    author="Rite of Renaissance",
    author_email="riteofrenaissance@proton.me",
    description="Mobile AI Consciousness System for Android/Termux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/riteofrenaissance/conscious-bridge-reloaded",
    
    packages=["conscious_bridge_reloaded_pkg"],
    install_requires=["flask>=2.0.0"],
    
    entry_points={
        "console_scripts": [
            "cb-reloaded=conscious_bridge_reloaded_pkg.cli:main",
        ],
    },
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
