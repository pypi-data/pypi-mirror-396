# Synapse SDK - Codebase Structure

## Directory Organization

```
synapse-sdk/
├── synapse_sdk/          # Main package directory
│   ├── clients/          # Backend and Ray-based client implementations
│   ├── plugins/          # Plugin system core
│   │   ├── models.py     # PluginRelease and Run classes
│   │   ├── neural_net/   # Neural network plugins (deployment, inference, train, tune)
│   │   ├── export/       # Data export plugins
│   │   ├── upload/       # File upload plugins
│   │   ├── smart_tool/   # Automated labeling tools
│   │   ├── pre_annotation/
│   │   ├── post_annotation/
│   │   └── data_validation/
│   ├── cli/              # Command-line interface implementation
│   ├── devtools/         # Development tools and dashboard
│   │   └── docs/         # Docusaurus documentation site
│   ├── utils/            # Utility functions
│   │   ├── converters/   # Data format converters (COCO, VOC, YOLO)
│   │   └── storage/      # Storage provider abstractions
│   ├── shared/           # Shared utilities and types
│   ├── loggers.py        # Logging configuration
│   ├── types.py          # Type definitions
│   └── i18n.py           # Internationalization
├── tests/                # Test suite
│   ├── clients/          # Client tests
│   ├── plugins/          # Plugin tests
│   ├── utils/            # Utility tests
│   └── loggers/          # Logger tests
├── docs/                 # Documentation content (markdown)
│   ├── i18n/ko/          # Korean translations
│   └── [various .md files]
├── locale/               # Locale files for i18n
├── .github/workflows/    # CI/CD workflows
├── synapse-sample-plugin/# Sample plugin for reference
├── pyproject.toml        # Package configuration
├── Makefile              # Development commands
└── [config files]        # .pre-commit-config.yaml, pytest.ini, etc.
```

## Key Components

### Plugin System
- **Models**: `synapse_sdk/plugins/models.py` - PluginRelease and Run classes
- **Categories**: neural_net, export, upload, smart_tool, pre_annotation, post_annotation, data_validation
- **Execution Methods**: Job (Ray Job), Task (Ray Task), REST API (Ray Serve)
- **Template System**: Cookiecutter-based plugin scaffolding

### Clients
- Backend client for API communication with Synapse backend
- Ray-based agent clients for distributed workflows
- API root: `https://api.test.synapse.sh/`

### CLI
- Entry point: `synapse` command (defined in pyproject.toml)
- Commands: config, plugin management, devtools
- Implementation: Click-based in `synapse_sdk/cli/`

### Development Tools
- Interactive web dashboard (Streamlit-based)
- Documentation site (Docusaurus)
- Debugging and monitoring utilities

## Configuration Storage

User configuration stored at: `~/.config/synapse/devtools.json`
Contains: backend host/token, agent details, plugin storage location
