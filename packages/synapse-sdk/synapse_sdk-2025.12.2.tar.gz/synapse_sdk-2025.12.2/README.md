# 🧠 Synapse SDK

![lint workflow](https://github.com/datamaker-kr/synapse-sdk/actions/workflows/lint.yml/badge.svg)
![test workflow](https://github.com/datamaker-kr/synapse-sdk/actions/workflows/test.yml/badge.svg)

A Python SDK for building and managing ML plugins, data annotation workflows, and AI agents.

## ✨ Features

- **🔌 Plugin System**: Create and manage ML plugins with categories like neural networks, data validation, and export tools
- **🤖 Agent Management**: Backend and Ray-based agent clients for distributed AI workflows  
- **🔄 Data Converters**: Convert between formats (COCO, Pascal VOC, YOLO) and annotation schemas
- **🛠️ Development Tools**: Interactive web dashboard for monitoring and debugging
- **⚡ CLI Interface**: Command-line tool for configuration, plugin management, and development

## 📅 Versioning

Synapse SDK uses **CalVer (Calendar Versioning)**.  
The version format is `YYYY.MM.PATCH`, based on the release year and month.

Examples:

- `2025.9.5` → 5th release in September 2025  
- `2025.10.1` → 1st release in October 2025  

We recommend using the latest monthly release.  
If needed, you can pin to a specific month, e.g. `2025.9.*`.

## 🚀 Quick Start

```bash
pip install synapse-sdk
synapse --help
```

## 🔍 Code Review

This repository uses systematic code review with P1-P4 priority rules:

### Using the Review-PR Command

Review pull requests using the integrated review system:

```bash
# Review a PR with English comments  
/review-pr 123

# Review a PR with Korean comments
/review-pr 123 ko
```

### Code Review Priority Levels

- **[P1_rules.md](P1_rules.md)** - Security and Stability (Critical) 🔴
- **[P2_rules.md](P2_rules.md)** - Core Functionality (High Priority) 🟡  
- **[P3_rules.md](P3_rules.md)** - Best Practices (Medium Priority) 🟠
- **[P4_rules.md](P4_rules.md)** - Code Style (Low Priority) 🔵

### Review Process

1. **Automated Analysis**: The review-pr command systematically applies P1-P4 rules
2. **Priority-Based Feedback**: Issues are categorized by severity and impact
3. **Actionable Comments**: Each issue includes specific recommendations and rule references
4. **Language Support**: Comments can be generated in English or Korean
5. **Decision Logic**:
   - P1, P2, or P3 violations → Request Changes
   - Only P4 violations or no issues → Approve

See [AGENT.md](AGENT.md) for complete development guidelines and code review rules.

## 📚 Documentation

*Docs [https://docs.synapse.sh](https://docs.synapse.sh)*
