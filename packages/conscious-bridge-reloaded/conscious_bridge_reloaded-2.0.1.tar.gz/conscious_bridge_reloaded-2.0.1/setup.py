from setuptools import setup

setup(
    name="conscious-bridge-reloaded",
    version="2.0.1",  # ✅ النسخة الصحيحة
    author="Rite of Renaissance",
    author_email="riteofrenaissance@proton.me",
    description="Mobile AI Consciousness System for Android/Termux",
    
    # الحزمة الوحيدة
    packages=["conscious_bridge_reloaded_pkg"],
    
    # ⭐⭐ هذا ينشئ أمر cb-reloaded ⭐⭐
    entry_points={
        "console_scripts": [
            "cb-reloaded=conscious_bridge_reloaded_pkg.cli:main",
        ],
    },
    
    install_requires=["flask>=2.0.0"],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
