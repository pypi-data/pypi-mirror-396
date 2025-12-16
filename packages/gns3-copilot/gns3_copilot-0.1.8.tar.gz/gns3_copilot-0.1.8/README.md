# GNS3 Copilot

![Python](https://img.shields.io/badge/python-3.8+-blue.svg) ![GNS3](https://img.shields.io/badge/GNS3-2.2+-green.svg) ![LangChain](https://img.shields.io/badge/LangChain-1.0.7-orange.svg) ![Nornir](https://img.shields.io/badge/Nornir-3.5.0-red.svg) ![Netmiko](https://img.shields.io/badge/Netmiko-4.6.0-blue.svg) ![LangGraph](https://img.shields.io/badge/LangGraph-1.0.0-purple.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

An AI-powered network automation assistant designed specifically for GNS3 network simulator, providing intelligent network device management and automated operations.

## Project Overview

GNS3 Copilot is a powerful network automation tool that integrates multiple AI models and network automation frameworks. It can interact with users through natural language and perform tasks such as network device configuration, topology management, and fault diagnosis.

<img src="https://raw.githubusercontent.com/yueguobin/gns3-copilot/refs/heads/master/demo.gif" alt="GNS3 Copilot Function demonstration" width="1280"/>

### Core Features

- 🤖 **AI-Powered Chat Interface**: Supports natural language interaction, understands network automation requirements
- 🔧 **Device Configuration Management**: Batch configuration of network devices, supports multiple vendor devices (currently tested with Cisco IOSv image only)
- 📊 **Topology Management**: Automatically create, modify, and manage GNS3 network topologies
- 🔍 **Network Diagnostics**: Intelligent network troubleshooting and performance monitoring
- 🌐 **LLM Support**: Integrated DeepSeek AI model for natural language processing



## Technical Architecture

[GNS3-Copilot Architecture](Architecture/gns3_copilot_architecture.md)

[Core Framework Detailed Design](Architecture/Core%20Framework%20Detailed%20Design.md)

## Installation Guide

### Environment Requirements

- Python 3.8+
- GNS3 Server (running on http://localhost:3080 or remote host)
- Supported operating systems: Windows, macOS, Linux

### Installation Steps

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

1. **Install GNS3 Copilot**
```bash
pip install gns3-copilot
```

1. **Start GNS3 Server**
Ensure GNS3 Server is running and can be accessed via its API interface: `http://x.x.x.x:3080`

1. **Launch the application**
```bash
gns3-copilot
```

## Usage Guide

### Startup

```bash
# Basic startup, default port 8501
gns3-copilot

# Specify custom port
gns3-copilot --server.port 8080

# Specify address and port
gns3-copilot --server.address 0.0.0.0 --server.port 8080

# Run in headless mode
gns3-copilot --server.headless true

# Get help
gns3-copilot --help

```

### Configure on Settings Page

GNS3 Copilot configuration is managed through a Streamlit interface, with all settings saved in the `.env` file in the project root directory. If the `.env` file doesn't exist on first run, the system will automatically create it.

#### 🔧 Main Configuration Content

##### 1. GNS3 Server Configuration
- **GNS3 Server Host**: GNS3 server host address (e.g., 127.0.0.1)
- **GNS3 Server URL**: Complete GNS3 server URL (e.g., http://127.0.0.1:3080)
- **API Version**: GNS3 API version (supports v2 and v3)
- **GNS3 Server Username**: GNS3 server username (required only for API v3)
- **GNS3 Server Password**: GNS3 server password (required only for API v3)

##### 2. LLM Model Configuration
- **Model Provider**: Model provider (supports: openai, anthropic, deepseek, xai, openrouter, etc.)
- **Model Name**: Specific model name (e.g., deepseek-chat, gpt-4o-mini, etc.)
- **Model API Key**: Model API key
- **Base URL**: Base URL for model service (required when using third-party platforms like OpenRouter)
- **Temperature**: Model temperature parameter (controls output randomness, range 0.0-1.0)

##### 3. Other Settings
- **Linux Console Username**: Linux console username (for Debian devices in GNS3)
- **Linux Console Password**: Linux console password

## Security Considerations

1. **API Key Protection**:
   - Do not commit `.env` file to version control
   - Regularly rotate API keys
   - Use principle of least privilege

## License

This project uses MIT License - see [LICENSE](LICENSE) file for details.

## Contact

- Project Homepage: https://github.com/yueguobin/gns3-copilot
- Issue Reporting: https://github.com/yueguobin/gns3-copilot/issues

---
