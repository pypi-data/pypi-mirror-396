# GNS3 Copilot

![Python](https://img.shields.io/badge/python-3.8+-blue.svg) ![GNS3](https://img.shields.io/badge/GNS3-2.2+-green.svg) ![LangChain](https://img.shields.io/badge/LangChain-1.0.7-orange.svg) ![Nornir](https://img.shields.io/badge/Nornir-3.5.0-red.svg) ![Netmiko](https://img.shields.io/badge/Netmiko-4.6.0-blue.svg) ![LangGraph](https://img.shields.io/badge/LangGraph-1.0.0-purple.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

一个基于AI的网络自动化助手，专为GNS3网络模拟器设计，提供智能化的网络设备管理和自动化操作。

## 项目简介

GNS3 Copilot 是一个强大的网络自动化工具，集成了多种AI模型和网络自动化框架，能够通过自然语言与用户交互，执行网络设备配置、拓扑管理和故障诊断等任务。

<img src="https://raw.githubusercontent.com/yueguobin/gns3-copilot/refs/heads/master/demo.gif" alt="GNS3 Copilot 功能演示" width="1280"/>


### 核心功能

- 🤖 **AI驱动的对话界面**: 支持自然语言交互，理解网络自动化需求
- 🔧 **设备配置管理**: 批量配置网络设备，支持多种厂商设备（目前仅测试了Cisco IOSv镜像）
- 📊 **拓扑管理**: 自动创建、修改和管理GNS3网络拓扑
- 🔍 **网络诊断**: 智能网络故障排查和性能监控
- 🌐 **LLM支持**: 集成DeepSeek AI模型进行自然语言处理




## 技术架构

[GNS3-Copilot Architecture](Architecture/gns3_copilot_architecture.md)

[Core Framework Detailed Design](Architecture/Core%20Framework%20Detailed%20Design.md)

## 安装指南

### 环境要求

- Python 3.8+
- GNS3 Server (运行在 http://localhost:3080或远程主机)
- 支持的操作系统: Windows, macOS, Linux

### 安装步骤

1. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

1. **安装 GNS3 Copilot**
```bash
pip install gns3-copilot
```

1. **启动 GNS3 Server**
确保 GNS3 Server 运行并可以通过网络访问其 API 接口：`http://x.x.x.x:3080`

1. **启动应用程序**
```bash
gns3-copilot
```


## 使用指南

### 启动

```bash
# 基本启动，默认端口8501
gns3-copilot

# 指定自定义端口
gns3-copilot --server.port 8080

# 指定地址和端口
gns3-copilot --server.address 0.0.0.0 --server.port 8080

# 无头模式运行
gns3-copilot --server.headless true

# 获取帮助
gns3-copilot --help

```


### 配置参数详解


#### 🔧 主要配置内容

##### 1. GNS3 服务器配置
- **GNS3 Server Host**: GNS3 服务器主机地址（如：127.0.0.1）
- **GNS3 Server URL**: GNS3 服务器完整 URL（如：http://127.0.0.1:3080）
- **API Version**: GNS3 API 版本（支持 v2 和 v3）
- **GNS3 Server Username**: GNS3 服务器用户名（仅 API v3 需要）
- **GNS3 Server Password**: GNS3 服务器密码（仅 API v3 需要）

##### 2. LLM 模型配置
- **Model Provider**: 模型提供商（支持：openai, anthropic, deepseek, xai, openrouter 等）
- **Model Name**: 具体模型名称（如：deepseek-chat, gpt-4o-mini 等）
- **Model API Key**: 模型 API 密钥
- **Base URL**: 模型服务的基础 URL（使用 OpenRouter 等第三方平台时必需）
- **Temperature**: 模型温度参数（控制输出随机性，范围 0.0-1.0）

##### 3. 其他设置
- **Linux Console Username**: Linux 控制台用户名（用于 GNS3 中的 Debian 设备）
- **Linux Console Password**: Linux 控制台密码


## 安全注意事项

**API密钥保护**: 
   - 不要将 `.env` 文件提交到版本控制
   - 定期轮换API密钥
   - 使用最小权限原则


## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页: https://github.com/yueguobin/gns3-copilot
- 问题反馈: https://github.com/yueguobin/gns3-copilot/issues


---
