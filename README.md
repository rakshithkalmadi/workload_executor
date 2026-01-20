# 🚀 LexAI - AI Workload Executor Agent

**LexAI** is an intelligent AI agent that automatically discovers, executes, and validates workloads on remote servers. It reads documentation, runs workloads via SSH, troubleshoots errors autonomously, and reports results back to users.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Roadmap](#roadmap)

---

## 🔍 Overview

LexAI solves the challenge of manually testing workloads across different environments. Instead of engineers manually SSHing into servers, reading documentation, and troubleshooting issues, LexAI automates the entire process using an AI agent.

### Problem Statement
- Manual workload execution is time-consuming
- Debugging failures requires expertise and context switching
- Scaling workload testing across multiple servers is complex

### Solution
An AI agent that:
1. **Reads** workload documentation automatically
2. **Connects** to remote servers via SSH
3. **Executes** workloads with the correct configuration
4. **Diagnoses** issues when failures occur
5. **Reports** results (pass/fail) back to users

---

## ✨ Key Features

### 🤖 Intelligent Documentation Parser
- Automatically reads and understands workload documentation
- Extracts execution commands, options, and configurations
- Identifies prerequisites and dependencies

### 🔌 Remote Server Connectivity
- Secure SSH connection to remote VMs/servers (AWS EC2, etc.)
- Key-based authentication support
- Connection pooling for efficient command execution

### ⚡ Workload Execution Engine
- Runs workloads on remote servers
- Captures stdout, stderr, and exit codes
- Supports multiple workload types (Docker, binaries, scripts)

### 🔧 Self-Healing & Error Resolution
- Automatically detects execution failures
- Searches for solutions in documentation and online resources
- Attempts to fix issues and retry execution

### 📊 Result Reporting
- Clear pass/fail status reporting
- Execution logs and metrics collection
- Notification support (future: Slack, Email, Webhooks)

### 🎯 Workload Discovery (Planned)
- Browse trending workloads from Docker Hub, GitHub, Ollama
- One-click workload testing
- Performance benchmarking

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         LexAI Agent                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   LangChain  │  │  Doc Parser  │  │  Error Resolver      │  │
│  │   AI Agent   │──│  (LLM-based) │──│  (Search + Fix)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    SSH Executor                           │  │
│  │  - Connect to remote servers                              │  │
│  │  - Execute commands                                       │  │
│  │  - Stream output in real-time                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│         │                                                       │
└─────────│───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Remote Server     │
│   (EC2/VM/Cloud)    │
│   - Run workloads   │
│   - Collect metrics │
└─────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **AI Framework** | LangChain |
| **LLM Provider** | OpenAI GPT-4 / Local LLMs |
| **Language** | Python 3.10+ |
| **SSH Client** | Paramiko |
| **Configuration** | YAML |
| **CLI Interface** | Click / Typer |
| **Logging** | Loguru |

---

## 📁 Project Structure

```
workload_executor/
├── config/
│   ├── system_configuration.yaml   # Server connection settings
│   └── rsakey.pem                  # SSH private key
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── lexai_agent.py           # Main LangChain agent
│   │   └── tools/
│   │       ├── ssh_tool.py         # SSH execution tool
│   │       ├── doc_parser_tool.py  # Documentation parser
│   │       ├── search_tool.py      # Web search for solutions
│   ├── ssh/
│   │   ├── __init__.py
│   │   └── connection.py           # SSH connection manager
│   ├── workloads/
│   │   ├── __init__.py
│   │   └── executor.py             # Workload execution logic
│   └── utils/
│       ├── __init__.py
│       └── config.py               # Configuration loader
├── tests/
│   └── test_agent.py
├── .env.example                    # Environment variables template
├── requirements.txt                # Python dependencies
├── main.py                         # Entry point
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- SSH key for remote server access
- OpenAI API key (or local LLM setup)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/workload_executor.git
cd workload_executor
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Step 5: Configure Server Connection
Edit `config/system_configuration.yaml`:
```yaml
remote_ip: "your-server-hostname.compute.amazonaws.com"
username: "ec2-user"
key_file: "./rsakey.pem"
```

### Step 6: Place SSH Key
Copy your SSH private key to `config/rsakey.pem` and set permissions:
```bash
chmod 400 config/rsakey.pem
```

---

## ⚙️ Configuration

### Server Configuration (`config/system_configuration.yaml`)

| Field | Description | Example |
|-------|-------------|---------|
| `remote_ip` | Hostname/IP of remote server | `ec2-xx-xx-xx.amazonaws.com` |
| `username` | SSH username | `ec2-user`, `ubuntu` |
| `key_file` | Path to SSH private key | `./rsakey.pem` |

### Environment Variables (`.env`)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models |
| `LOG_LEVEL` | Logging verbosity (DEBUG, INFO, WARN) |

---

## 💻 Usage

### Run a Workload
```bash
python main.py run --workload "docker pull nginx && docker run -d nginx"
```

### Test with Documentation
```bash
python main.py run --docs "./workload_docs/nginx.md" --auto-execute
```

### Interactive Mode
```bash
python main.py agent
# AI Agent will prompt you for workload details
```

---

## 🗺️ Roadmap

### Phase 1: Core Agent (MVP) ✅
- [x] Project structure setup
- [ ] SSH connection manager
- [ ] Basic LangChain agent
- [ ] Simple workload execution
- [ ] Pass/fail result reporting

### Phase 2: Intelligence Layer
- [ ] Documentation parser (LLM-based)
- [ ] Error detection and diagnosis
- [ ] Web search for solutions
- [ ] Auto-retry with fixes

### Phase 3: Advanced Features
- [ ] Workload discovery (Docker Hub, GitHub, Ollama)
- [ ] Performance metrics collection (KPIs)
- [ ] Multi-server parallel execution
- [ ] Web dashboard for results

### Phase 4: Enterprise
- [ ] User authentication
- [ ] Team workspaces
- [ ] Scheduled workload runs
- [ ] Notification integrations

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) before submitting PRs.

---

**Built with ❤️ using LangChain and Python**
