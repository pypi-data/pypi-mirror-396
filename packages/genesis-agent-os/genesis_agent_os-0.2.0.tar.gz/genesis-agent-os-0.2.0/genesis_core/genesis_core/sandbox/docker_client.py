"""
Docker client for the Genesis Core sandbox functionality.

This module implements Docker SDK integration to provide isolated execution
environments for agents.
"""

import docker
import os
import tempfile
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

from ..errors import AgentExecutionError


class DockerClient:
    """
    Client for managing Docker containers for agent execution sandboxing.
    """

    def __init__(self, timeout: int = 300):
        """
        Initialize the Docker client.

        Args:
            timeout: Timeout in seconds for container execution
        """
        try:
            self.client = docker.from_env()
            self.timeout = timeout
            # Test connection to Docker daemon
            self.client.ping()
        except docker.errors.DockerException as e:
            raise AgentExecutionError(f"Docker connection failed: {str(e)}")

    def execute_code_in_container(
        self,
        code: str,
        language: str = "python",
        dependencies: Optional[List[str]] = None,
        files: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute code in an isolated Docker container.

        Args:
            code: The code to execute
            language: Programming language of the code
            dependencies: List of dependencies to install
            files: Additional files to include in the container

        Returns:
            Dictionary containing execution results
        """
        if dependencies is None:
            dependencies = []
        if files is None:
            files = {}

        # Determine the base image based on language
        if language == "python":
            base_image = "python:3.11-slim"
        else:
            base_image = "python:3.11-slim"  # Default to Python

        # Create a temporary directory for the execution context
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Write the main code file
            code_file = temp_path / f"main.{self._get_file_extension(language)}"
            code_file.write_text(code)

            # Write additional files if provided
            for filename, content in files.items():
                file_path = temp_path / filename
                file_path.write_text(content)

            # Create a requirements file if dependencies are specified
            if dependencies:
                req_file = temp_path / "requirements.txt"
                req_file.write_text("\n".join(dependencies))

            # Create Dockerfile
            dockerfile_content = self._create_dockerfile(base_image, dependencies)
            dockerfile_path = temp_path / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)

            # Build the image
            image_tag = f"genesis-agent-{int(time.time())}"
            try:
                image, build_logs = self.client.images.build(
                    path=str(temp_path),
                    tag=image_tag,
                    rm=True,  # Remove intermediate containers
                    timeout=self.timeout
                )
            except docker.errors.BuildError as e:
                raise AgentExecutionError(f"Docker build failed: {str(e)}")

            # Run the container
            try:
                container = self.client.containers.run(
                    image=image_tag,
                    command=f"{self._get_execution_command(language)} /main.{self._get_file_extension(language)}",
                    remove=True,
                    stdout=True,
                    stderr=True,
                    detach=False,
                    network_mode="none",  # No network access for security
                    working_dir="/",
                    # Set resource limits for security
                    mem_limit="512m",  # Limit memory to 512MB
                    nano_cpus=500000000,  # Limit to half a CPU
                    environment={
                        "PYTHONPATH": "/"
                    }
                )

                # Parse output
                output = container.decode('utf-8')

                return {
                    "success": True,
                    "output": output,
                    "error": None
                }
            except docker.errors.ContainerError as e:
                return {
                    "success": False,
                    "output": e.stderr.decode('utf-8') if e.stderr else "",
                    "error": f"Container execution failed: {str(e)}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Container execution error: {str(e)}"
                }
            finally:
                # Clean up the image after execution
                try:
                    self.client.images.remove(image=image_tag, force=True)
                except:
                    pass  # Ignore cleanup errors

    def _get_file_extension(self, language: str) -> str:
        """
        Get the file extension for a given language.

        Args:
            language: Programming language

        Returns:
            File extension
        """
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "go": "go",
            "rust": "rs",
            "java": "java",
            "c": "c",
            "cpp": "cpp"
        }
        return extensions.get(language.lower(), "py")

    def _get_execution_command(self, language: str) -> str:
        """
        Get the execution command for a given language.

        Args:
            language: Programming language

        Returns:
            Execution command
        """
        commands = {
            "python": "python3",
            "javascript": "node",
            "typescript": "ts-node",
            "go": "go run",
            "rust": "cargo run",
            "java": "java",
            "c": "gcc",
            "cpp": "g++"
        }
        return commands.get(language.lower(), "python3")

    def _create_dockerfile(self, base_image: str, dependencies: List[str]) -> str:
        """
        Create Dockerfile content with security and isolation measures.

        Args:
            base_image: Base Docker image to use
            dependencies: List of dependencies to install

        Returns:
            Dockerfile content as string
        """
        dockerfile = f"""
FROM {base_image}

# Create a non-root user for security
RUN groupadd -r sandbox && useradd -r -g sandbox sandbox

# Set working directory
WORKDIR /app

# Install dependencies if specified
"""

        if dependencies:
            # For Python, install requirements
            dockerfile += """
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
"""

        dockerfile += """
# Copy the code file
COPY main.* /main.*

# Copy additional files
COPY . .

# Change ownership to non-root user
RUN chown -R sandbox:sandbox /app

# Switch to non-root user
USER sandbox

# Security measures
# No network access (configured at runtime)
# Resource limits (configured at runtime)
# Read-only filesystem (partial) where possible

# Default command
CMD ["echo", "No command specified"]
"""

        return dockerfile.strip()

    def is_docker_available(self) -> bool:
        """
        Check if Docker is available and accessible.

        Returns:
            True if Docker is available, False otherwise
        """
        try:
            self.client.ping()
            return True
        except:
            return False

    def get_active_containers(self) -> List[Dict[str, Any]]:
        """
        Get a list of active containers created by Genesis.

        Returns:
            List of active container information
        """
        try:
            containers = self.client.containers.list(filters={"ancestor": "genesis-agent"})
            return [
                {
                    "id": container.id[:12],
                    "name": container.name,
                    "status": container.status,
                    "created": container.attrs.get("Created", ""),
                    "image": container.image.tags
                }
                for container in containers
            ]
        except:
            return []