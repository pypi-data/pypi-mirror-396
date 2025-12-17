# ecs-shell

[![PyPI version ecs-shell](https://img.shields.io/pypi/v/ecs-shell.svg)](https://pypi.python.org/pypi/ecs-shell/)

**ecs-shell** is yet another interactive CLI tool for connecting to AWS ECS (Elastic Container Service) tasks. It provides a user-friendly interface to browse services, select tasks, and establish shell sessions - all without having to remember complex AWS CLI commands or task IDs.

I have created this as an utility for me in the past, and only later found that there are plenty
of others out there. I think the CLI UX with this one is better, so I decided to publish it anyways.

https://github.com/user-attachments/assets/065ad13e-38fc-4e71-a9bc-d57973d347f7

## ✨ Features

- 🎯 **Interactive Selection**: Browse and select ECS services and tasks using arrow keys
- 🎨 **Rich UI**: Beautiful terminal interface with color-coded output
- ⚡ **Fast Navigation**: Quickly filter through services and tasks
- 📊 **Task Details**: View task creation time, CPU/Memory allocation, and container information
- 🔄 **Session Management**: Seamless shell session establishment with AWS ECS Exec
- 🔐 **Profile Support**: Use any AWS CLI profile for multi-account workflows

## 📋 Requirements

Before using ecs-shell, ensure you have the following installed and configured:

### 1. AWS CLI

The AWS CLI must be installed and authenticated with appropriate permissions.

```sh
# Install AWS CLI (macOS)
brew install awscli

# Configure your AWS credentials
aws configure
```

**Required AWS Permissions:**
- `ecs:ListServices`
- `ecs:ListTasks`
- `ecs:DescribeTasks`
- `ecs:ExecuteCommand`

### 2. Session Manager Plugin

The Session Manager plugin is required for establishing interactive sessions with ECS tasks.

```sh
# Install Session Manager plugin (macOS)
brew install --cask session-manager-plugin

# Verify installation
session-manager-plugin --version
```

For other operating systems, see the [AWS Session Manager Plugin installation guide](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html).

### 3. Python

Python 3.10 or higher is required.

```sh
# Check your Python version
python3 --version
```

### 4. ECS Task Configuration

Your ECS tasks must have **ECS Exec** enabled. This is configured in your task definition:

```json
{
  "enableExecuteCommand": true
}
```

## 🚀 Installation

### Using pipx (Recommended)

[pipx](https://github.com/pypa/pipx) installs CLI tools in isolated environments, avoiding conflicts:

```sh
# Install pipx if you haven't already
brew install pipx
pipx ensurepath

# Install ecs-shell
pipx install ecs-shell
```

### Using pip

```sh
# Install globally
pip install ecs-shell

# Or in a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install ecs-shell
```

### Upgrade

```sh
# With pipx
pipx upgrade ecs-shell

# With pip
pip install --upgrade ecs-shell
```

## 📖 Usage

```sh
ecs-shell <profile> <cluster>
```

**Arguments:**
- `profile`: AWS CLI profile name (from `~/.aws/credentials`)
- `cluster`: ECS cluster name

### Examples

```sh
# Connect to staging cluster using 'production' profile
ecs-shell production my-cluster-staging

# Connect to development cluster
ecs-shell dev-profile dev-cluster

# Use default profile
ecs-shell default my-cluster
```

## 🛠️ Development

### Setup

```sh
# Clone the repo
# Create and activate virtual environment
make setup-venv
source venv/bin/activate

# Install dependencies
make install-deps

# Install ecs-shell in development mode
make local-install
```

### Commands

```sh
make lint           # Run linting checks
make format         # Auto-format code
make local-install  # Install package locally (in active environment)
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
