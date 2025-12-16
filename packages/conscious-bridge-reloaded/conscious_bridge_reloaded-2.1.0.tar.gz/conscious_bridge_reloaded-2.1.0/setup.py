from setuptools import setup, find_packages
import os

# قراءة README
readme_path = os.path.join(os.path.dirname(__file__), "Readme.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Conscious Bridge RELOADED v2.1.0 - Mobile AI Consciousness System"

setup(
    name="conscious-bridge-reloaded",
    version="2.1.0",  # ⭐⭐ الإصدار الجديد ⭐⭐
    author="Rite of Renaissance",
    author_email="riteofrenaissance@proton.me",
    description="Mobile AI Consciousness System for Android/Termux - Evolution Ready v2.1.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/riteofrenaissance/conscious-bridge-reloaded",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Android",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 4 - Beta",
        "Framework :: Flask",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=4.0.0",
        "sqlalchemy>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'conscious-bridge=api.server:main',
        ],
    },
    include_package_data=True,
    keywords="ai consciousness mobile android termux bridge evolution",
)
