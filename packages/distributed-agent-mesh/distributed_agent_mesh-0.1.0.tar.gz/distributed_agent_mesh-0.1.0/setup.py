from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

setup(
    name="distributed-agent-mesh",
    version="0.1.0",
    author="Abhishek Kumar",
    author_email="ipsabhi420@gmail.com",  # Replace with your actual email
    description="A framework for autonomous agents that collaborate via P2P communication",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Kumar123ips/distributed-agent-mesh",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - pure Python!
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
    },
    keywords="agents, distributed, p2p, autonomous, collaboration, mesh, multi-agent, ai",
    project_urls={
        "Bug Reports": "https://github.com/Kumar123ips/distributed-agent-mesh/issues",
        "Source": "https://github.com/Kumar123ips/distributed-agent-mesh",
        "Documentation": "https://github.com/Kumar123ips/distributed-agent-mesh#readme",
    },
)
