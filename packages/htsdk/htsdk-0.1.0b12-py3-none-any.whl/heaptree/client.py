import os
import base64
from dataclasses import dataclass
from typing import List

import requests
import logging
from heaptree.enums import Language, NodeSize
from heaptree.exceptions import (
    HeaptreeException,
    InternalServerErrorException,
    MissingCredentialsException,
    raise_for_status,
    raise_for_auth_error,
)
from heaptree.response_wrappers import (
    CreateNodeResponse,
    DownloadResponse,
    ExecutionResponseWrapper,
    ReadFilesResponse,
    UploadResponse,
    WriteFilesResponse,
    GitStatus,
    GitFileStatus,
    GitBranches,
    FileInfo,
    PathPermissions,
    HealthResponse,
    ListNodesResponse,
    NodeInfo,
    NodeStatusResponse,
)

logger = logging.getLogger(__name__)


class Heaptree:
    def __init__(self, api_key: str | None = None, *, base_url: str | None = None):
        """Create a new Heaptree SDK client.

        Args:
            api_key: Your platform **X-Api-Key**.
            base_url: Override the base URL of the Heaptree API (useful for local
                testing). Defaults to the hosted production endpoint.
        """

        self.api_key: str | None = api_key
        self.token: str | None = None
        self.base_url: str = base_url or "https://api.heaptree.com"

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------


    def call_api(self, endpoint: str, data: dict):
        url = f"{self.base_url}{endpoint}"

        # ----- Auth headers -----
        headers: dict[str, str] = {"Content-Type": "application/json"}

        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        else:
            raise MissingCredentialsException(
                "No api key supplied. Please set api_key"
            )

        response = requests.post(url, json=data, headers=headers)
        
        try:
            response_json = response.json()
        except ValueError as e:
            # Response is not JSON (should not happen in normal operation)
            raise HeaptreeException(
                f"Invalid JSON response for {endpoint}: {response.text}"
            ) from e
        
        # Handle HTTP error status codes
        if response.status_code == 401:
            raise_for_auth_error(response_json, "Authentication")
        elif response.status_code >= 400:
            # Generic HTTP error
            detail = response_json.get("detail", f"HTTP {response.status_code} error")
            raise HeaptreeException(f"HTTP {response.status_code}: {detail}", response_json)
            
        return response_json

    # ------------------------------------------------------------------
    # Node management
    # ------------------------------------------------------------------

    def create_node(
        self,
        num_nodes: int = 1,
        node_size: NodeSize = NodeSize.SMALL,
        lifetime_seconds: int = 330,  # 5 minutes
    ) -> CreateNodeResponse:
        """
        Create one or more nodes.

        Returns CreateNodeResponse with convenient access:
        - result.node_id (for single node)
        - result.node_ids (for multiple nodes)
        - result.status (operation status)
        - result.execution_time_seconds (time taken to create)
            
        Raises:
            UsageLimitsExceededException: When usage limits are exceeded
            InvalidRequestParametersException: When request parameters are invalid
            InternalServerErrorException: When an internal server error occurs
        """
        data = {
            "num_nodes": num_nodes,
            "node_size": node_size.value,
            "lifetime_seconds": lifetime_seconds,
        }
        raw_response = self.call_api("/create-node", data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(raw_response, "Node creation")
        return CreateNodeResponse(raw_response)

    def terminate(self, node_id: str) -> None:
        """
        Terminate a node by terminating it and removing associated resources.
        
        Args:
            node_id: The ID of the node to terminate
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            AccessDeniedException: When access to the node is denied
            InvalidNodeStateException: When the node is in an invalid state
            InternalServerErrorException: When an internal server error occurs
        """
        data = {
            "node_id": node_id,
        }
        raw_response = self.call_api("/cleanup-node", data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(raw_response, "Node termination")
        logger.info(f"Node termination status: {raw_response.get('status')}")

    def terminate_nodes(self, node_ids: list[str]) -> None:
        """
        Terminate multiple nodes at once.
        
        Args:
            node_ids: List of node IDs to terminate
            
        Raises:
            InternalServerErrorException: When an internal server error occurs
        """
        data = {"node_ids": node_ids}
        raw_response = self.call_api("/terminate-nodes", data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(raw_response, "Bulk node termination")
        logger.info(f"Bulk node termination status: {raw_response.get('status')}")

    # ------------------------------------------------------------------
    # Remote command execution
    # ------------------------------------------------------------------

    def run_command(self, node_id: str, command: str) -> ExecutionResponseWrapper:
        """Execute a command on the remote node.
        
        Args:
            node_id: Target node.
            command: Command to execute.
            
        Returns:
            ExecutionResponseWrapper with convenient access to output, error, exit_code, etc.
        """
        data = {"node_id": node_id, "command": command}
        raw_response = self.call_api("/run-command", data)
        return ExecutionResponseWrapper(raw_response)

    def run_code(self, node_id: str, lang: "Language", code: str) -> ExecutionResponseWrapper:
        """Execute **code** on the remote *node*.

        Args:
            node_id: Target node.
            lang: :pyclass:`~heaptree.enums.Language` specifying the language
                runtime to use.
            code: Source code to execute.
            
        Returns:
            ExecutionResponseWrapper with convenient access to output, error, exit_code, etc.
        """
        data = {"node_id": node_id, "lang": lang.value, "code": code}
        raw_response = self.call_api("/run-code", data)
        return ExecutionResponseWrapper(raw_response)

    # ------------------------------------------------------------------
    # File management
    # ------------------------------------------------------------------

    def upload(self, node_id: str, file_path: str, destination_path: str = "/home/ubuntu/Desktop/MY_FILES/") -> UploadResponse:
        """
        Upload a file to a node and transfer it to the node's filesystem.

        Args:
            node_id: The ID of the node to upload to
            file_path: Local path of the file to upload
            destination_path: Optional path on the node where file should be placed
                            (defaults to /home/ubuntu/Desktop/MY_FILES/)

        Returns:
            UploadResponse(status, file_path, destination_path)
            
        Raises:
            FileNotFoundError: When the local file is not found
            InvalidRequestParametersException: When request parameters are invalid
            InstanceNotReadyException: When the instance is not ready for file transfer
            InvalidDestinationPathException: When the destination path is invalid
            TransferFailedException: When the file transfer fails
            InternalServerErrorException: When an internal server error occurs
        """

        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract filename from path
        filename = os.path.basename(file_path)

        # Step 1: Get presigned upload URL
        upload_url_data = {"node_id": node_id, "filename": filename}
        upload_response = self.call_api("/get-upload-url", upload_url_data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(upload_response, "Upload URL generation")

        # Step 2: Upload file to S3 using presigned URL
        upload_url = upload_response["upload_url"]
        fields = upload_response["fields"]

        try:
            with open(file_path, "rb") as file:
                # Prepare multipart form data
                files = {"file": (filename, file, "application/octet-stream")}

                # Upload to S3
                s3_response = requests.post(upload_url, data=fields, files=files)
                s3_response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise InternalServerErrorException(f"Failed to upload file: {str(e)}")

        # Step 3: Transfer file from S3 to node filesystem
        transfer_data = {"node_id": node_id}
        if destination_path:
            transfer_data["destination_path"] = destination_path

        transfer_response = self.call_api("/transfer-files", transfer_data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(transfer_response, "File transfer")
        
        logger.info("File uploaded successfully to %s", transfer_response.get("destination_path", "node"))

        return UploadResponse(
            status="SUCCESS",
            file_path=file_path,
            destination_path=transfer_response.get("destination_path", ""),
            node_id=node_id
        )

    def download(self, node_id: str, remote_path: str, local_path: str) -> DownloadResponse:
        """Download a file from a node to your local filesystem.
        
        Args:
            node_id: The ID of the node to download from
            remote_path: Path to the file on the remote node
            local_path: Local path where the file should be saved
            
        Returns:
            DownloadResponse(status, remote_path, local_path)
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            FileNotFoundException: When the remote file is not found
            InternalServerErrorException: When an internal server error occurs
        """
        data = {
            "node_id": node_id,
            "file_path": remote_path,  # API still expects 'file_path'
        }
        response_json = self.call_api("/download-files", data)
        raise_for_status(response_json, "File download")

        s3_url = response_json.get("download_url")

        if not s3_url:
            raise InternalServerErrorException("No download URL found in API response")

        try:
            download_response = requests.get(s3_url)
            download_response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(download_response.content)

            logger.info("File downloaded successfully to %s", local_path)
            return DownloadResponse(status="SUCCESS", remote_path=remote_path, local_path=local_path)

        except requests.exceptions.RequestException as e:
            raise InternalServerErrorException(f"Failed to download file: {e}")

    def write_files(self, node_id: str, file_path: str, content: str) -> WriteFilesResponse:
        """Write content to a file on a remote node.
        
        Args:
            node_id: The ID of the node to write to
            file_path: Path on the node where content should be written
            content: The content to write to the file
            
        Returns:
            WriteFilesResponse(status, message, file_path, node_id)
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            InvalidRequestParametersException: When request parameters are invalid
            InternalServerErrorException: When an internal server error occurs
        """
        data = {"node_id": node_id, "file_path": file_path, "content": content}
        response_json = self.call_api("/write-files", data)
        raise_for_status(response_json, "File write")
        
        return WriteFilesResponse(
            status=response_json.get("status", "SUCCESS"),
            message=response_json.get("message", ""),
            file_path=file_path,
            node_id=node_id
        )

    def read_files(self, node_id: str, file_path: str) -> ReadFilesResponse:
        """Read the contents of a file from a remote node.
        
        Args:
            node_id: The ID of the node to read from
            file_path: Path to the file on the remote node
            
        Returns:
            ReadFilesResponse(status, message, file_content, file_path, node_id)
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            FileNotFoundException: When the specified file is not found
            InvalidRequestParametersException: When request parameters are invalid
            InternalServerErrorException: When an internal server error occurs
        """
        data = {"node_id": node_id, "file_path": file_path}
        response_json = self.call_api("/read-files", data)
        raise_for_status(response_json, "File read")
        
        return ReadFilesResponse(
            status=response_json.get("status", "SUCCESS"),
            message=response_json.get("message", ""),
            file_content=response_json.get("file_content", ""),
            file_path=file_path,
            node_id=node_id
        )

    # ------------------------------------------------------------------
    # Convenience: standard node wrapper
    # ------------------------------------------------------------------
    def node(self, node_id: str) -> "Node":
        """Get a standard node wrapper for convenient operations."""
        return Node(self, node_id)

    # ------------------------------------------------------------------
    # Sandbox node operations
    # ------------------------------------------------------------------

    def create(
        self,
        lifetime_seconds: int = 300,
        memory_mb: int = 128,
        vcpu_count: int = 1,
        pip_install: list[str] | None = None,
        internet: bool = True,
    ) -> "SandboxNode":
        """
        Create a new sandbox node with sub-second startup time.
        
        Args:
            lifetime_seconds: How long the node should remain active (default: 300 seconds / 5 minutes)
            memory_mb: Memory allocation in MB (default: 128)
            vcpu_count: Number of virtual CPUs (default: 1)
            pip_install: Optional list of Python packages to install in the sandbox
            internet: Whether the node should have internet access (default: True)
            
        Returns:
            SandboxNode object with convenient methods for code execution
            
        Raises:
            InternalServerErrorException: When node creation fails
        """
        data = {
            "lifetime_seconds": lifetime_seconds,
            "memory_mb": memory_mb,
            "vcpu_count": vcpu_count,
            "internet": bool(internet),
        }
        if pip_install:
            data["pip_install"] = pip_install
        response_json = self.call_api("/create-firecracker-node", data)
        raise_for_status(response_json, "Node creation")
        
        node_id = response_json.get("node_id")
        logger.info(f"Created node {node_id} in {response_json.get('execution_time_seconds', 0):.3f}s")
        
        # Log warning if pip install failed for any packages
        if response_json.get("pip_install_errors"):
            warning_msg = response_json.get("warning", f"Failed to install packages: {', '.join(response_json['pip_install_errors'])}")
            logger.warning(f"Node {node_id}: {warning_msg}")
        
        return SandboxNode(self, node_id)

    def execute_code(
        self,
        node_id: str,
        code: str,
        timeout_seconds: int = 30,
    ) -> ExecutionResponseWrapper:
        """
        Execute Python code in a sandbox node.
        
        Args:
            node_id: The ID of the node
            code: Python code to execute
            timeout_seconds: Maximum execution time (default: 30 seconds)
            
        Returns:
            ExecutionResponseWrapper with output, error, and exit code
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            AccessDeniedException: When access to the node is denied
            InternalServerErrorException: When execution fails
        """
        data = {
            "node_id": node_id,
            "code": code,
            "timeout_seconds": timeout_seconds,
        }
        response_json = self.call_api("/run-firecracker-code", data)
        raise_for_status(response_json, "Code execution")
        
        return ExecutionResponseWrapper(response_json)

    def destroy_node(self, node_id: str) -> None:
        """
        Destroy a sandbox node and release its resources.
        
        Args:
            node_id: The ID of the node to destroy
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            AccessDeniedException: When access to the node is denied
            InternalServerErrorException: When cleanup fails
        """
        data = {"node_id": node_id}
        response_json = self.call_api("/cleanup-firecracker-node", data)
        raise_for_status(response_json, "Node cleanup")
        logger.info(f"Destroyed node {node_id}")

    def health(self) -> HealthResponse:
        """
        Check the health status of the Heaptree service.
        
        Returns:
            HealthResponse with daemon_healthy and vsock_support status
            
        Example:
            >>> health = client.health()
            >>> if health.daemon_healthy:
            ...     print("Service is running")
        """
        response_json = self.call_api_get("/firecracker/health")
        return HealthResponse(
            status=response_json.get("status", "UNKNOWN"),
            daemon_healthy=response_json.get("daemon_healthy", False),
            vsock_support=response_json.get("vsock_support", False),
        )

    def list_nodes(self) -> ListNodesResponse:
        """
        List all nodes belonging to the authenticated user.
        
        Returns:
            ListNodesResponse with list of nodes
            
        Example:
            >>> nodes = client.list_nodes()
            >>> for node in nodes.nodes:
            ...     print(f"Node {node.node_id} at {node.ip}")
        """
        response_json = self.call_api_get("/firecracker/list-vms")
        nodes = [
            NodeInfo(
                node_id=vm.get("vm_id", ""),
                cid=vm.get("cid", 0),
                ip=vm.get("ip", ""),
            )
            for vm in response_json.get("vms", [])
        ]
        return ListNodesResponse(
            status=response_json.get("status", "UNKNOWN"),
            nodes=nodes,
        )

    def node_status(self, node_id: str) -> NodeStatusResponse:
        """
        Get detailed status of a node.
        
        Args:
            node_id: The ID of the node
            
        Returns:
            NodeStatusResponse with detailed status including
            process_running, vsock_socket_exists, and guest_agent_reachable
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            AccessDeniedException: When access to the node is denied
            
        Example:
            >>> status = client.node_status("my-node-id")
            >>> if status.is_ready:
            ...     print("Node is ready for code execution")
        """
        response_json = self.call_api_get(f"/firecracker/vm/{node_id}/status")
        return NodeStatusResponse(
            status=response_json.get("status", "UNKNOWN"),
            node_id=response_json.get("vm_id", node_id),
            cid=response_json.get("cid"),
            ip=response_json.get("ip"),
            process_running=response_json.get("process_running", False),
            vsock_socket_exists=response_json.get("vsock_socket_exists", False),
            guest_agent_reachable=response_json.get("guest_agent_reachable", False),
        )

    def call_api_get(self, endpoint: str) -> dict:
        """Make a GET request to the API."""
        url = f"{self.base_url}{endpoint}"
        
        headers: dict[str, str] = {}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        else:
            raise MissingCredentialsException(
                "No api key supplied. Please set api_key"
            )

        response = requests.get(url, headers=headers)
        
        try:
            response_json = response.json()
        except ValueError as e:
            raise HeaptreeException(
                f"Invalid JSON response for {endpoint}: {response.text}"
            ) from e
        
        if response.status_code == 401:
            raise_for_auth_error(response_json, "Authentication")
        elif response.status_code >= 400:
            detail = response_json.get("detail", f"HTTP {response.status_code} error")
            raise HeaptreeException(f"HTTP {response.status_code}: {detail}", response_json)
            
        return response_json


class Node:
    """
    A standard Heaptree node wrapper for convenience methods like git operations.
    """
    def __init__(self, client: Heaptree, node_id: str):
        self._client = client
        self._node_id = node_id

    @property
    def node_id(self) -> str:
        return self._node_id

    def git_clone(
        self,
        url: str,
        path: str,
        *,
        username: str | None = None,
        password: str | None = None,
        branch: str | None = None,
    ) -> None:
        """
        Clone a Git repository into the node filesystem.
        Supports optional HTTPS basic auth and branch selection.
        """
        payload: dict = {
            "node_id": self._node_id,
            "url": url,
            "path": path,
        }
        if username:
            payload["username"] = username
        if password:
            payload["password"] = password
        if branch:
            payload["branch"] = branch

        response_json = self._client.call_api("/git-clone", payload)
        raise_for_status(response_json, "Git clone")

    def git_status(self, repo_path: str) -> GitStatus:
        """
        Get repository status including branch, ahead/behind, and modified files.
        """
        payload = {"node_id": self._node_id, "repo_path": repo_path}
        response_json = self._client.call_api("/git-status", payload)
        raise_for_status(response_json, "Git status")

        files: list[GitFileStatus] = [
            GitFileStatus(name=item.get("name", ""), status=item.get("status", ""))
            for item in response_json.get("file_status", []) or []
        ]
        return GitStatus(
            current_branch=response_json.get("current_branch", ""),
            ahead=int(response_json.get("ahead", 0)),
            behind=int(response_json.get("behind", 0)),
            file_status=files,
        )

    def git_branches(self, repo_path: str) -> GitBranches:
        """
        List branches in the repository.
        """
        payload = {"node_id": self._node_id, "repo_path": repo_path}
        response_json = self._client.call_api("/git-branches", payload)
        raise_for_status(response_json, "Git branches")

        return GitBranches(
            branches=response_json.get("branches", []) or [],
            current_branch=response_json.get("current_branch"),
        )


@dataclass
class FileUpload:
    """Helper type for multi-file uploads to sandbox nodes."""
    source: bytes
    destination: str


class SandboxNode:
    """
    A sandbox node for isolated code execution.
    
    This class provides a convenient interface for working with sandboxes.
    Nodes automatically terminate after their lifetime expires.
    
    Example:
        >>> from heaptree import Heaptree
        >>> client = Heaptree(api_key="your-api-key")
        >>> 
        >>> # Create a node (alive for 5 minutes by default)
        >>> node = client.create()
        >>> 
        >>> # Execute Python code
        >>> result = node.run_code("print('Hello from sandbox!')")
        >>> print(result.output)
        >>> 
        >>> # Destroy when done (optional - auto-destroys after lifetime)
        >>> node.destroy()
    """
    
    def __init__(self, client: Heaptree, node_id: str):
        """Initialize a SandboxNode instance.
        
        Args:
            client: The Heaptree client instance
            node_id: The unique identifier for this node
        """
        self._client = client
        self._node_id = node_id
        self._cleaned_up = False
    
    @property
    def node_id(self) -> str:
        """Get the node ID."""
        return self._node_id
    
    @property
    def id(self) -> str:
        """Get the node ID (alias for node_id)."""
        return self._node_id
    
    def run_code(self, code: str, timeout_seconds: int = 30) -> ExecutionResponseWrapper:
        """
        Execute Python code in this sandbox.
        
        Args:
            code: Python code to execute
            timeout_seconds: Maximum execution time (default: 30 seconds)
            
        Returns:
            ExecutionResponseWrapper with convenient access to:
            - result.output: Standard output from the code
            - result.error: Error message if execution failed
            - result.exit_code: Exit code (0 for success)
            - result.logs: Combined output for convenience
            
        Raises:
            InternalServerErrorException: When execution fails
            
        Example:
            >>> result = node.run_code("print('Hello World')")
            >>> print(result.logs)
            Hello World
        """
        if self._cleaned_up:
            raise InternalServerErrorException("Cannot run code on a destroyed node")
        
        return self._client.execute_code(
            self._node_id,
            code,
            timeout_seconds
        )
    
    def destroy(self) -> None:
        """
        Destroy this node and release its resources.
        
        Note: Nodes automatically destroy after their lifetime expires,
        so calling this method is optional. Use it when you're done with
        the node early to save resources.
        
        Raises:
            InternalServerErrorException: When destruction fails
        """
        if self._cleaned_up:
            logger.warning(f"Node {self._node_id} already destroyed")
            return
        
        self._client.destroy_node(self._node_id)
        self._cleaned_up = True
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically destroy."""
        if not self._cleaned_up:
            try:
                self.destroy()
            except Exception as e:
                logger.warning(f"Failed to destroy node {self._node_id} on exit: {e}")
        return False
    
    def __repr__(self) -> str:
        status = "destroyed" if self._cleaned_up else "active"
        return f"SandboxNode(id='{self._node_id}', status='{status}')"

    def status(self) -> NodeStatusResponse:
        """
        Get detailed status of this node.
        
        Returns:
            NodeStatusResponse with detailed status including:
            - process_running: Whether the node process is running
            - vsock_socket_exists: Whether the VSOCK socket exists
            - guest_agent_reachable: Whether the guest agent is reachable
            - is_ready: Convenience property for checking if node is ready
            
        Example:
            >>> status = node.status()
            >>> if status.is_ready:
            ...     print("Node is ready for code execution")
            >>> if status.guest_agent_reachable:
            ...     print(f"Guest agent reachable at IP {status.ip}")
        """
        if self._cleaned_up:
            return NodeStatusResponse(
                status="DESTROYED",
                node_id=self._node_id,
                process_running=False,
                vsock_socket_exists=False,
                guest_agent_reachable=False,
            )
        return self._client.node_status(self._node_id)

    def wait_until_ready(self, timeout_seconds: int = 60, poll_interval: float = 1.0) -> bool:
        """
        Wait until the node is ready for code execution.
        
        Args:
            timeout_seconds: Maximum time to wait (default: 60 seconds)
            poll_interval: Time between status checks (default: 1 second)
            
        Returns:
            True if the node became ready within the timeout, False otherwise
            
        Example:
            >>> node = client.create()
            >>> if node.wait_until_ready():
            ...     result = node.run_code("print('Hello!')")
        """
        import time
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            try:
                status = self.status()
                if status.is_ready:
                    return True
            except Exception:
                pass  # Ignore errors during polling
            time.sleep(poll_interval)
        return False

    # -----------------------------
    # File operations
    # -----------------------------

    def upload_file(self, content: bytes, destination: str) -> None:
        """Upload a single file into the sandbox.

        Args:
            content: File content as bytes
            destination: Absolute or relative path inside the sandbox
        """
        payload = {
            "node_id": self._node_id,
            "content": base64.b64encode(content).decode("ascii"),
            "destination": destination,
        }
        response_json = self._client.call_api("/firecracker/upload-file", payload)
        if str(response_json.get("status", "")).upper() != "SUCCESS":
            raise InternalServerErrorException(response_json.get("details", "Upload failed"))

    def upload_files(self, files: List[FileUpload]) -> None:
        """Upload multiple files into the sandbox."""
        payload = {
            "node_id": self._node_id,
            "files": [
                {
                    "content": base64.b64encode(item.source).decode("ascii"),
                    "destination": item.destination,
                }
                for item in files
            ],
        }
        response_json = self._client.call_api("/firecracker/upload-files", payload)
        if str(response_json.get("status", "")).upper() != "SUCCESS":
            raise InternalServerErrorException(response_json.get("details", "Bulk upload failed"))

    def download_file(self, source: str) -> bytes:
        """Download a file from the sandbox.

        Args:
            source: Path to the file inside the sandbox
        Returns:
            The file content as bytes
        """
        payload = {"node_id": self._node_id, "file_path": source}
        response_json = self._client.call_api("/firecracker/download-file", payload)
        if str(response_json.get("status", "")).upper() != "SUCCESS":
            raise InternalServerErrorException(response_json.get("details", "Download failed"))
        content_b64 = response_json.get("content", "")
        return base64.b64decode(content_b64)

    def delete_file(self, path: str) -> None:
        """Delete a file inside the sandbox."""
        payload = {"node_id": self._node_id, "file_path": path}
        response_json = self._client.call_api("/firecracker/delete-file", payload)
        if str(response_json.get("status", "")).upper() != "SUCCESS":
            raise InternalServerErrorException(response_json.get("details", "Delete failed"))

    # -----------------------------
    # File system utilities
    # -----------------------------

    def _run_python_json(self, code: str, timeout_seconds: int = 30) -> dict:
        """Run Python code in the sandbox and parse JSON from stdout."""
        result = self._client.execute_code(
            self._node_id,
            code,
            timeout_seconds=timeout_seconds,
        )
        if not result.success:
            raise InternalServerErrorException(
                result.error or f"Execution failed with exit code {result.exit_code}"
            )
        output = (result.output or "").strip()
        try:
            import json as _json  # local import to avoid dependency at module import-time
            return _json.loads(output)
        except Exception as exc:
            raise InternalServerErrorException(f"Failed to parse JSON output: {output}") from exc

    def list_files(self, directory: str) -> list[FileInfo]:
        """List files and directories in a given path inside the sandbox."""
        code = f"""
import os, json
from datetime import datetime, timezone
path = {directory!r}
def iso(ts): 
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
entries = []
for name in os.listdir(path):
    full = os.path.join(path, name)
    try:
        st = os.stat(full, follow_symlinks=False)
        entries.append({{
            "name": name,
            "is_dir": os.path.isdir(full),
            "size": int(st.st_size),
            "mod_time": iso(st.st_mtime),
        }})
    except FileNotFoundError:
        # File might disappear between listdir and stat; skip it
        pass
print(json.dumps({{"entries": entries}}))
""".strip()
        data = self._run_python_json(code)
        items = data.get("entries", []) or []
        return [
            FileInfo(
                name=str(item.get("name", "")),
                is_dir=bool(item.get("is_dir", False)),
                size=int(item.get("size", 0)),
                mod_time=str(item.get("mod_time", "")),
            )
            for item in items
        ]

    def create_folder(self, path: str, mode: str = "755") -> None:
        """Create a directory with specific permissions (octal string like '755')."""
        code = f"""
import os, json
target = {path!r}
mode = int({mode!r}, 8)
os.makedirs(target, exist_ok=True)
os.chmod(target, mode)
print(json.dumps({{"status":"SUCCESS"}}))
""".strip()
        self._run_python_json(code)

    def set_permissions(self, path: str, mode: str, recursive: bool = False) -> None:
        """Set file or directory permissions. If recursive=True and path is a directory, apply to all children."""
        code = f"""
import os, json
target = {path!r}
mode = int({mode!r}, 8)
recursive = {bool(recursive)}
if recursive and os.path.isdir(target):
    for root, dirs, files in os.walk(target):
        for d in dirs:
            os.chmod(os.path.join(root, d), mode)
        for f in files:
            os.chmod(os.path.join(root, f), mode)
else:
    os.chmod(target, mode)
print(json.dumps({{"status":"SUCCESS"}}))
""".strip()
        self._run_python_json(code)

    def set_directory_permissions_recursive(self, path: str, mode: str) -> None:
        """Convenience wrapper to set permissions recursively on a directory."""
        self.set_permissions(path, mode, recursive=True)

    def get_permissions(self, path: str) -> PathPermissions:
        """Get file or directory permissions as an octal string (e.g., '644', '755')."""
        code = f"""
import os, stat, json
target = {path!r}
st = os.stat(target, follow_symlinks=False)
perms = format(stat.S_IMODE(st.st_mode), 'o')
print(json.dumps({{"permissions": perms}}))
""".strip()
        data = self._run_python_json(code)
        return PathPermissions(permissions=str(data.get("permissions", "")))

    # -----------------------------
    # Git operations
    # -----------------------------

    def git_clone(
        self,
        url: str,
        path: str,
        username: str | None = None,
        password: str | None = None,
        branch: str | None = None,
    ) -> None:
        """Clone a Git repository into the sandbox.

        Args:
            url: Repository URL (HTTPS recommended)
            path: Destination directory inside the sandbox
            username: Optional username for HTTPS auth
            password: Optional password or personal access token for HTTPS auth
            branch: Optional branch name to clone
        """
        payload: dict[str, object] = {
            "node_id": self._node_id,
            "url": url,
            "path": path,
        }
        if username is not None:
            payload["username"] = username
        if password is not None:
            payload["password"] = password
        if branch is not None:
            payload["branch"] = branch

        response_json = self._client.call_api("/firecracker/git-clone", payload)
        if str(response_json.get("status", "")).upper() != "SUCCESS":
            raise InternalServerErrorException(response_json.get("details", "Git clone failed"))

    def git_status(self, repo_path: str) -> GitStatus:
        """Get repository status (branch, ahead/behind, changed files)."""
        payload = {"node_id": self._node_id, "repo_path": repo_path}
        response_json = self._client.call_api("/firecracker/git-status", payload)
        if str(response_json.get("status", "")).upper() != "SUCCESS":
            raise InternalServerErrorException(response_json.get("details", "Git status failed"))
        files: list[GitFileStatus] = [
            GitFileStatus(name=item.get("name", ""), status=item.get("status", ""))
            for item in response_json.get("file_status", []) or []
        ]
        return GitStatus(
            current_branch=response_json.get("current_branch", ""),
            ahead=int(response_json.get("ahead", 0)),
            behind=int(response_json.get("behind", 0)),
            file_status=files,
        )

    def git_branches(self, repo_path: str) -> GitBranches:
        """List branches for a repository."""
        payload = {"node_id": self._node_id, "repo_path": repo_path}
        response_json = self._client.call_api("/firecracker/git-branches", payload)
        if str(response_json.get("status", "")).upper() != "SUCCESS":
            raise InternalServerErrorException(response_json.get("details", "Git branches failed"))
        return GitBranches(
            branches=response_json.get("branches", []) or [],
            current_branch=response_json.get("current_branch"),
        )