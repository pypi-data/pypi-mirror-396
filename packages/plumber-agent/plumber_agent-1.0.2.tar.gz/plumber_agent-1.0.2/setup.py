"""
Setup script for plumber-agent package
"""
from setuptools import setup

# Skip README reading to avoid potential hangs
long_description = "Local DCC Agent for Plumber Workflow Editor"

setup(
    name="plumber-agent",
    version="1.0.2",
    description="Local DCC Agent for Plumber Workflow Editor - Enables Maya, Blender, and Houdini operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Damn Ltd",
    author_email="info@damnltd.com",
    url="https://app.plumber.damnltd.com",
    packages=["plumber_agent", "plumber_agent.services", "plumber_agent.dcc_plugins"],
    package_dir={"plumber_agent": "src"},
    package_data={
        "plumber_agent": ["*.py"],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "websockets>=12.0",
        "pydantic>=2.5.0",
        "psutil>=5.9.6",
        "watchdog>=3.0.0",
        "cryptography>=42.0.0",
        "requests>=2.31.0",
        "aiofiles>=23.2.1",
        "python-multipart>=0.0.6",
        "aiohttp>=3.9.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "plumber-agent=plumber_agent.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    keywords=["workflow", "dcc", "maya", "blender", "houdini", "automation", "vfx"],
    project_urls={
        "Homepage": "https://app.plumber.damnltd.com",
        "Documentation": "https://app.plumber.damnltd.com/docs",
        "Repository": "https://github.com/damnvfx/plumber-editor",
        "Bug Tracker": "https://github.com/damnvfx/plumber-editor/issues",
    },
)
