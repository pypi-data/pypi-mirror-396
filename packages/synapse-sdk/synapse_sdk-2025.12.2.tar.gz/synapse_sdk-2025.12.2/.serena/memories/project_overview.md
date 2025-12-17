# Synapse SDK - Project Overview

## Purpose

Synapse SDK is a Python SDK for building and managing ML plugins, data annotation workflows, and AI agents. It provides:

- Plugin system for various ML operations (neural networks, export, upload, smart tools)
- Agent management for distributed AI workflows (Backend and Ray-based)
- Data converters for format conversion (COCO, Pascal VOC, YOLO)
- Development tools including interactive web dashboard
- CLI interface for configuration and plugin management

## Tech Stack

### Primary Language
- Python 3.10+ (tested with 3.12)

### Core Dependencies
- **Plugin System**: cookiecutter (template generation)
- **CLI**: click
- **Data Processing**: pydantic, pyyaml, openpyxl, pillow
- **Storage**: boto3, fsspec[gcs,s3,sftp], universal-pathlib
- **HTTP**: requests, websockets
- **Utilities**: tqdm, python-dotenv, inquirer, ffmpeg-python
- **Security**: pyjwt, sentry-sdk

### Optional Dependencies
- **Ray Integration**: ray[all]==2.50.0 (distributed computing)
- **Dev Tools**: streamlit, streamlit-ace (web dashboard)
- **HPO**: hyperopt, bayesian-optimization

### Development Tools
- **Package Manager**: uv (modern Python package manager)
- **Code Quality**: ruff (linting and formatting)
- **Testing**: pytest with multiple plugins
- **Pre-commit**: ruff hooks for automatic formatting
- **Documentation**: Docusaurus (Node.js-based)

## Project Type

This is a Python package/SDK distributed via PyPI with:
- CLI tool (`synapse` command)
- Importable library modules
- Plugin development framework
- Development dashboard

## Versioning

Uses **CalVer (Calendar Versioning)** with format `YYYY.MM.PATCH`
- Example: `2025.9.5` = 5th release in September 2025
- Recommend using latest monthly release or pin to specific month like `2025.9.*`
