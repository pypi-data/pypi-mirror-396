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

### Basic Usage

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

### Interactive Flow

1. **Select a Service**: Browse through all services in your cluster
2. **Select a Task**: Choose from running tasks in the selected service
3. **Connect**: Automatically establishes a shell session to the task

```
🚀 ECS Interactive Shell
Profile: production | Cluster: my-cluster-staging

? Select a service: 
❯ api-service
  worker-service
  frontend-service
  
? Select a task:
❯ abc123def456 | 2024-11-05 10:30:15 | api-container
  xyz789ghi012 | 2024-11-05 09:15:42 | api-container

╭─ Connecting to ECS Task ─╮
│ Profile: production       │
│ Cluster: my-cluster       │
│ Task: abc123def456        │
╰───────────────────────────╯

Starting session with SessionId: ecs-execute-command-...
sh-4.2$
```

### Navigation

- **↑/↓ Arrow Keys**: Navigate through options
- **Enter**: Select the highlighted option
- **Ctrl+C**: Cancel and exit

## 🛠️ Development

### Setup

```sh
# Clone the repository
git clone https://github.com/yourusername/ecs-shell.git
cd ecs-shell

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
make help           # Show all available commands
make lint           # Run linting checks
make format         # Auto-format code
make local-install  # Install package locally (in active environment)
```

### Code Quality

This project uses:
- **[ruff](https://github.com/astral-sh/ruff)**: Fast Python linter and formatter
- **[pyright](https://github.com/microsoft/pyright)**: Static type checker

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### "ExecuteCommandException: Task must have 'enableExecuteCommand' enabled"

Your ECS tasks need to have ECS Exec enabled. Update your task definition:

```json
{
  "enableExecuteCommand": true
}
```

After updating, you'll need to deploy new tasks for the change to take effect.

### "Session Manager plugin not found"

Install the Session Manager plugin:

```sh
brew install --cask session-manager-plugin
```

### "Access Denied" errors

Ensure your IAM user/role has the required permissions:
- `ecs:ExecuteCommand`
- `ecs:ListServices`
- `ecs:ListTasks`
- `ecs:DescribeTasks`

### No services or tasks found

- Verify the cluster name is correct
- Ensure you're using the right AWS profile
- Check that services are running in the cluster

## 🔗 Related Resources

- [AWS ECS Exec Documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html)
- [AWS Session Manager Plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)

## ⭐ Acknowledgments

Built with:
- [boto3](https://github.com/boto/boto3) - AWS SDK for Python
- [inquirer](https://github.com/magmax/python-inquirer) - Interactive command line prompts
- [rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
