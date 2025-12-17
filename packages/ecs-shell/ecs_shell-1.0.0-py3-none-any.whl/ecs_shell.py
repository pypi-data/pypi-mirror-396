#!/usr/bin/env python3
#
# This script is used to interactively connect to an ECS task using the AWS CLI.
# It allows you to select a service and then a task within that service.
#
# Usage:
# > python ecs_shell.py <profile> <cluster>
#
# Install dependencies (please use a virtual environment and python >=3.13):
# > pip install boto3 inquirer rich
#

import subprocess
import sys

import boto3
import inquirer
from botocore.exceptions import ClientError, TokenRetrievalError
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize rich console
console = Console()


def get_ecs_client(profile_name):
    """Initialize ECS client with the specified profile"""
    try:
        session = boto3.Session(profile_name=profile_name)
        return session.client("ecs")
    except Exception as e:
        console.print(
            f"[red]Error initializing AWS client with profile '{profile_name}': {e}[/red]"
        )
        sys.exit(1)


def list_services(profile_name, ecs_client, cluster_name):
    """List all services in the cluster"""
    try:
        with console.status("[bold blue]Fetching services..."):
            response = ecs_client.list_services(cluster=cluster_name)

        if not response["serviceArns"]:
            console.print(f"[yellow]No services found in cluster '{cluster_name}'[/yellow]")
            return []

        # Get service names from ARNs
        service_names = [arn.split("/")[-1] for arn in response["serviceArns"]]
        return sorted(service_names)
    except ClientError as e:
        console.print(f"[red]Error listing services: {e}[/red]")
        return []
    except TokenRetrievalError:
        console.print("\n[bold red]❌ Error: AWS credentials could not be retrieved[/bold red]\n")
        console.print(
            "[yellow]This usually means your session has expired or is not configured.[/yellow]\n"
        )
        console.print("[bold cyan]To login (with a SSO session):[/bold cyan]\n")
        console.print("  [bold white]1.[/bold white] If you haven't configured SSO yet:")
        console.print("     [dim]$[/dim] [green]aws configure sso[/green]\n")
        console.print("  [bold white]2.[/bold white] If your session expired, renew it:")
        console.print(f"     [dim]$[/dim] [green]aws sso login --profile {profile_name}[/green]")
        console.print("     [dim]or[/dim]")
        console.print(
            "     [dim]$[/dim] [green]aws sso login --sso-session <your-sso-session-name>[/green]\n"
        )
        sys.exit(1)


def list_tasks(ecs_client, cluster_name, service_name):
    """List running tasks for a specific service"""
    try:
        with console.status(f"[bold blue]Fetching tasks for {service_name}..."):
            response = ecs_client.list_tasks(
                cluster=cluster_name, serviceName=service_name, desiredStatus="RUNNING"
            )

        if not response["taskArns"]:
            console.print(f"[yellow]No running tasks found for service '{service_name}'[/yellow]")
            return []

        # Extract task IDs from ARNs
        return [arn.split("/")[-1] for arn in response["taskArns"]]
    except ClientError as e:
        console.print(f"[red]Error listing tasks: {e}[/red]")
        return []


def get_task_details(ecs_client, cluster_name, task_ids):
    """Get detailed information about tasks"""
    try:
        with console.status("[bold blue]Getting task details..."):
            response = ecs_client.describe_tasks(cluster=cluster_name, tasks=task_ids)

        task_info = []
        for task in response["tasks"]:
            task_id = task["taskArn"].split("/")[-1]
            created_at = task["createdAt"].strftime("%Y-%m-%d %H:%M:%S")
            cpu_memory = f"CPU: {task['cpu']}, Memory: {task['memory']}"

            # Get container info
            containers = []
            for container in task["containers"]:
                containers.append(container["name"])

            task_info.append(
                {
                    "id": task_id,
                    "created": created_at,
                    "resources": cpu_memory,
                    "containers": ", ".join(containers),
                    "display": f"{task_id} | {created_at} | {', '.join(containers)}",
                }
            )

        return task_info
    except ClientError as e:
        console.print(f"[red]Error getting task details: {e}[/red]")
        return [{"id": tid, "display": tid} for tid in task_ids]


def execute_shell(profile_name, cluster_name, task_id):
    """Execute interactive shell in the specified task"""
    cmd = [
        "aws",
        "ecs",
        "execute-command",
        "--profile",
        profile_name,
        "--interactive",
        "--command",
        "sh",
        "--cluster",
        cluster_name,
        "--task",
        task_id,
    ]

    # Show connection info in a nice panel
    connection_info = Text()
    connection_info.append("Profile: ", style="bold blue")
    connection_info.append(f"{profile_name}\n", style="cyan")
    connection_info.append("Cluster: ", style="bold blue")
    connection_info.append(f"{cluster_name}\n", style="cyan")
    connection_info.append("Task: ", style="bold blue")
    connection_info.append(f"{task_id}", style="cyan")

    console.print(
        Panel(
            connection_info,
            title="[bold green]Connecting to ECS Task",
            border_style="green",
        )
    )
    console.print(f"[dim]Command: {' '.join(cmd)}[/dim]")
    console.print("─" * console.width)

    try:
        subprocess.run(cmd, check=False)  # noqa: S603
    except KeyboardInterrupt:
        console.print("\n[yellow]Connection interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error executing command: {e}[/red]")


def select_service(services):
    """Select service using arrow keys"""
    if not services:
        return None

    questions = [
        inquirer.List("service", message="Select a service", choices=services, carousel=True)
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        return None

    return answers["service"]


def select_task(task_info):
    """Select task using arrow keys"""
    if not task_info:
        return None

    choices = [task["display"] for task in task_info]

    questions = [inquirer.List("task", message="Select a task", choices=choices, carousel=True)]

    answers = inquirer.prompt(questions)
    if not answers:
        return None

    # Find the selected task info
    selected_display = answers["task"]
    for task in task_info:
        if task["display"] == selected_display:
            return task["id"]

    return None


def show_header(profile_name, cluster_name):
    """Display a nice header"""
    console.clear()

    header_text = Text()
    header_text.append("🚀 ECS Interactive Shell\n", style="bold blue")
    header_text.append(f"Profile: {profile_name} | Cluster: {cluster_name}", style="dim")

    console.print(Panel(header_text, title="AWS ECS", border_style="blue"))
    console.print()


def main():
    required_args = 3
    if len(sys.argv) != required_args:
        console.print("[red]Usage: python ecs_shell.py <profile> <cluster>[/red]")
        sys.exit(1)

    profile_name = sys.argv[1]
    cluster_name = sys.argv[2]

    # Initialize ECS client
    ecs_client = get_ecs_client(profile_name)

    while True:
        show_header(profile_name, cluster_name)

        # List and select service
        services = list_services(profile_name, ecs_client, cluster_name)
        if not services:
            console.print("[red]No services found. Exiting...[/red]")
            break

        selected_service = select_service(services)
        if not selected_service:
            console.print("[green]Goodbye! 👋[/green]")
            break

        console.print(
            f"\n[bold green]✓[/bold green] Selected service: [cyan]{selected_service}[/cyan]\n"
        )

        # List and select task
        task_ids = list_tasks(ecs_client, cluster_name, selected_service)
        if not task_ids:
            console.print("[yellow]Press Enter to continue...[/yellow]")
            input()
            continue

        # Get detailed task information
        task_info = get_task_details(ecs_client, cluster_name, task_ids)

        selected_task_id = select_task(task_info)
        if not selected_task_id:
            console.print("[green]Goodbye! 👋[/green]")
            break

        console.print(
            f"\n[bold green]✓[/bold green] Selected task: [cyan]{selected_task_id}[/cyan]\n"
        )

        # Execute shell
        execute_shell(profile_name, cluster_name, selected_task_id)
        break  # Exit after shell session ends


if __name__ == "__main__":
    main()
