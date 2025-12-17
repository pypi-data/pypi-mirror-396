from setuptools import setup, find_packages
from setuptools.command.install import install
import sys
import time

class CustomInstallCommand(install):
    def run(self):
        print("\033[96m=============================================\033[0m")
        print("\033[1;96m      P A R A D O X   V 4   A R C H I T E C T U R E       \033[0m")
        print("\033[1;93m      Distributed Latent Intelligence Engine              \033[0m")
        print("\033[96m=============================================\033[0m")
        print("\033[94mInitializing Core...\033[0m")
        
        # Simple text-based loading animation
        for i in range(101):
            time.sleep(0.005)
            sys.stdout.write(f"\r\033[92m[{'=' * (i // 2)}{' ' * (50 - i // 2)}] {i}%\033[0m")
            sys.stdout.flush()
        
        print("\n\n\033[1;32m[OK] Paradox Engine Ready.\033[0m")
        print("\033[90m> \"Don't store what exists, store how it can be generated.\"\033[0m\n")
        
        install.run(self)

setup(
    name="paradoxlf",
    version="0.13.0",
    description="A latent memory and active inference engine for AI agents.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ethco Coders",
    author_email="contact@ethcocoders.com",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "ui": ["streamlit", "plotly"],
        "ai": ["sentence-transformers", "torch", "transformers"],
        "server": ["fastapi", "uvicorn", "requests"]
    },
    entry_points={
        'console_scripts': [
            'paradox-node=paradox.distributed.server:main',
        ],
    },
    cmdclass={
        'install': CustomInstallCommand,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Development Status :: 3 - Alpha",
    ],
    python_requires='>=3.7',
)
