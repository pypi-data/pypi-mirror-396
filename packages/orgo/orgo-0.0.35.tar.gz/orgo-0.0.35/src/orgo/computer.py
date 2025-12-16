"""Computer class for interacting with Orgo virtual environments"""
import os as operating_system
import base64
import logging
import uuid
import io
from typing import Dict, List, Any, Optional, Callable, Literal, Union
from PIL import Image
import requests
from requests.exceptions import RequestException

from .api.client import ApiClient
from .prompt import get_provider

logger = logging.getLogger(__name__)

class Computer:
    def __init__(self, 
                 project: Optional[Union[str, 'Project']] = None,
                 name: Optional[str] = None,
                 computer_id: Optional[str] = None,
                 api_key: Optional[str] = None, 
                 base_api_url: Optional[str] = None,
                 ram: Optional[Literal[1, 2, 4, 8, 16, 32, 64]] = None,
                 memory: Optional[Literal[1, 2, 4, 8, 16, 32, 64]] = None,
                 cpu: Optional[Literal[1, 2, 4, 8, 16]] = None,
                 os: Optional[Literal["linux", "windows"]] = None,
                 gpu: Optional[Literal["none", "a10", "l40s", "a100-40gb", "a100-80gb"]] = None,
                 image: Optional[Union[str, Any]] = None):
        """
        Initialize an Orgo virtual computer.
        
        Args:
            project: Project name (str) or Project instance. If not provided, creates a new project.
            name: Computer name within the project (optional, auto-generated if not provided)
            computer_id: Existing computer ID to connect to (optional)
            api_key: Orgo API key (defaults to ORGO_API_KEY env var)
            base_api_url: Custom API URL (optional)
            ram/memory: RAM in GB (1, 2, 4, 8, 16, 32, or 64) - only used when creating
            cpu: CPU cores (1, 2, 4, 8, or 16) - only used when creating
            os: Operating system ("linux" or "windows") - only used when creating
            gpu: GPU type - only used when creating
            image: Custom image reference (str) or Forge object - only used when creating
        
        Examples:
            # Create computer in new project
            computer = Computer(ram=4, cpu=2)
            
            # Create computer with custom image
            forge = Forge(org_id="myorg", project_id="myproj").base("ubuntu").run("echo hello")
            computer = Computer(image=forge)
            
            # Create computer in existing project
            computer = Computer(project="manus", ram=4, cpu=2)
            
            # Connect to existing computer by ID
            computer = Computer(computer_id="11c4fd46-e069-4c32-be65-f82d9f87b9b8")
        """
        self.api_key = api_key or operating_system.environ.get("ORGO_API_KEY")
        self.base_api_url = base_api_url
        self.api = ApiClient(self.api_key, self.base_api_url)
        
        # Handle memory parameter as an alias for ram
        if ram is None and memory is not None:
            ram = memory
        
        # Store configuration
        self.os = os or "linux"
        self.ram = ram or 2
        self.cpu = cpu or 2
        self.gpu = gpu or "none"
        
        # Handle image
        self.image = image
        if hasattr(self.image, 'build') and callable(self.image.build):
            logger.info("Building image from Forge object...")
            self.image = self.image.build()
        
        if computer_id:

            # Just store the computer ID, no API call needed
            self.computer_id = computer_id
            self.name = name
            self.project_id = None
            self.project_name = None
            logger.info(f"Connected to computer ID: {self.computer_id}")
        elif project:
            # Work with specified project
            if isinstance(project, str):
                # Project name provided
                self.project_name = project
                self._initialize_with_project_name(project, name)
            else:
                # Project instance provided
                from .project import Project as ProjectClass
                if isinstance(project, ProjectClass):
                    self.project_name = project.name
                    self.project_id = project.id
                    self._initialize_with_project_instance(project, name)
                else:
                    raise ValueError("project must be a string (project name) or Project instance")
        else:
            # No project specified, create a new one
            self._create_new_project_and_computer(name)
    
    def _initialize_with_project_name(self, project_name: str, computer_name: Optional[str]):
        """Initialize with a project name (create project if needed)"""
        try:
            # Try to get existing project
            project = self.api.get_project_by_name(project_name)
            self.project_id = project.get("id")
            
            # Check for existing computers
            computers = self.api.list_computers(self.project_id)
            
            if computer_name:
                # Look for specific computer
                existing = next((c for c in computers if c.get("name") == computer_name), None)
                if existing:
                    self._connect_to_existing_computer(existing)
                else:
                    # Create new computer with specified name
                    self._create_computer(self.project_id, computer_name)
            elif computers:
                # No name specified, use first available computer
                self._connect_to_existing_computer(computers[0])
            else:
                # No computers exist, create new one
                self._create_computer(self.project_id, computer_name)
                
        except Exception:
            # Project doesn't exist, create it
            logger.info(f"Project {project_name} not found, creating new project")
            project = self.api.create_project(project_name)
            self.project_id = project.get("id")
            self._create_computer(self.project_id, computer_name)
    
    def _initialize_with_project_instance(self, project: 'Project', computer_name: Optional[str]):
        """Initialize with a Project instance"""
        computers = project.list_computers()
        
        if computer_name:
            # Look for specific computer
            existing = next((c for c in computers if c.get("name") == computer_name), None)
            if existing:
                self._connect_to_existing_computer(existing)
            else:
                # Create new computer with specified name
                self._create_computer(project.id, computer_name)
        elif computers:
            # No name specified, use first available computer
            self._connect_to_existing_computer(computers[0])
        else:
            # No computers exist, create new one
            self._create_computer(project.id, computer_name)
    
    def _create_new_project_and_computer(self, computer_name: Optional[str]):
        """Create a new project and computer"""
        # Generate a unique project name
        project_name = f"project-{uuid.uuid4().hex[:8]}"
        
        # Create the project
        project = self.api.create_project(project_name)
        self.project_id = project.get("id")
        self.project_name = project_name
        
        # Create a computer in the new project
        self._create_computer(self.project_id, computer_name)
    
    def _connect_to_existing_computer(self, computer_info: Dict[str, Any]):
        """Connect to an existing computer"""
        self.computer_id = computer_info.get("id")
        self.name = computer_info.get("name")
        logger.info(f"Connected to existing computer {self.name} (ID: {self.computer_id})")
    
    def _create_computer(self, project_id: str, computer_name: Optional[str]):
        """Create a new computer in the project"""
        # Generate name if not provided
        if not computer_name:
            computer_name = f"desktop-{uuid.uuid4().hex[:8]}"
        
        self.name = computer_name
        
        # Validate parameters
        if self.ram not in [1, 2, 4, 8, 16, 32, 64]:
            raise ValueError("ram must be one of: 1, 2, 4, 8, 16, 32, 64 GB")
        if self.cpu not in [1, 2, 4, 8, 16]:
            raise ValueError("cpu must be one of: 1, 2, 4, 8, 16 cores")
        if self.os not in ["linux", "windows"]:
            raise ValueError("os must be either 'linux' or 'windows'")
        if self.gpu not in ["none", "a10", "l40s", "a100-40gb", "a100-80gb"]:
            raise ValueError("gpu must be one of: 'none', 'a10', 'l40s', 'a100-40gb', 'a100-80gb'")
            
        # Resolve image name if needed
        image_ref = self.image
        if image_ref and isinstance(image_ref, str) and not image_ref.startswith("registry.fly.io"):
            logger.info(f"Resolving image name '{image_ref}'...")
            try:
                # Try to get org_id from project info
                project_info = self.api.get_project(project_id)
                org_id = project_info.get("org_id", "orgo") # Default to 'orgo'
                
                response = self.api.get_latest_build(org_id, project_id, image_ref)
                if response and response.get("build"):
                    resolved_ref = response.get("build", {}).get("imageRef")
                    if resolved_ref:
                        logger.info(f"Resolved '{image_ref}' to '{resolved_ref}'")
                        image_ref = resolved_ref
                    else:
                        logger.warning(f"Build found for '{image_ref}' but no imageRef present.")
                else:
                    logger.warning(f"Could not resolve image name '{self.image}'. Using as is.")
            except Exception as e:
                logger.warning(f"Failed to resolve image name: {e}")
        
        computer = self.api.create_computer(
            project_id=project_id,
            computer_name=computer_name,
            os=self.os,
            ram=self.ram,
            cpu=self.cpu,
            gpu=self.gpu,
            image=image_ref
        )
        self.computer_id = computer.get("id")
        logger.info(f"Created new computer {self.name} (ID: {self.computer_id})")
    
    def status(self) -> Dict[str, Any]:
        """Get current computer status"""
        return self.api.get_computer(self.computer_id)
    
    def restart(self) -> Dict[str, Any]:
        """Restart the computer"""
        return self.api.restart_computer(self.computer_id)
    
    def destroy(self) -> Dict[str, Any]:
        """Terminate and delete the computer instance"""
        return self.api.delete_computer(self.computer_id)
    
    # Navigation methods
    def left_click(self, x: int, y: int) -> Dict[str, Any]:
        """Perform left mouse click at specified coordinates"""
        return self.api.left_click(self.computer_id, x, y)
    
    def right_click(self, x: int, y: int) -> Dict[str, Any]:
        """Perform right mouse click at specified coordinates"""
        return self.api.right_click(self.computer_id, x, y)
    
    def double_click(self, x: int, y: int) -> Dict[str, Any]:
        """Perform double click at specified coordinates"""
        return self.api.double_click(self.computer_id, x, y)
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             button: str = "left", duration: float = 0.5) -> Dict[str, Any]:
        """Perform a smooth drag operation from start to end coordinates"""
        return self.api.drag(self.computer_id, start_x, start_y, end_x, end_y, button, duration)
    
    def scroll(self, direction: str = "down", amount: int = 3) -> Dict[str, Any]:
        """Scroll in specified direction and amount"""
        return self.api.scroll(self.computer_id, direction, amount)
    
    # Input methods
    def type(self, text: str) -> Dict[str, Any]:
        """Type the specified text"""
        return self.api.type_text(self.computer_id, text)
    
    def key(self, key: str) -> Dict[str, Any]:
        """Press a key or key combination (e.g., "Enter", "ctrl+c")"""
        return self.api.key_press(self.computer_id, key)
    
    # View methods
    def screenshot(self) -> Image.Image:
        """Capture screenshot and return as PIL Image"""
        response = self.api.get_screenshot(self.computer_id)
        image_data = response.get("image", "")
        
        if image_data.startswith(('http://', 'https://')):
            img_response = requests.get(image_data)
            img_response.raise_for_status()
            return Image.open(io.BytesIO(img_response.content))
        else:
            img_data = base64.b64decode(image_data)
            return Image.open(io.BytesIO(img_data))
    
    def screenshot_base64(self) -> str:
        """Capture screenshot and return as base64 string"""
        response = self.api.get_screenshot(self.computer_id)
        image_data = response.get("image", "")
        
        if image_data.startswith(('http://', 'https://')):
            img_response = requests.get(image_data)
            img_response.raise_for_status()
            return base64.b64encode(img_response.content).decode('utf-8')
        else:
            return image_data
    
    # Execution methods
    def bash(self, command: str) -> str:
        """Execute a bash command and return output"""
        response = self.api.execute_bash(self.computer_id, command)
        return response.get("output", "")
    
    def exec(self, code: str, timeout: int = 10) -> Dict[str, Any]:
        """Execute Python code on the remote computer"""
        response = self.api.execute_python(self.computer_id, code, timeout)
        return response
    
    def wait(self, seconds: float) -> Dict[str, Any]:
        """Wait for specified number of seconds"""
        return self.api.wait(self.computer_id, seconds)
    
    # Streaming methods
    def start_stream(self, connection: str) -> Dict[str, Any]:
        """Start streaming the computer screen to an RTMP server"""
        return self.api.start_stream(self.computer_id, connection)
    
    def stop_stream(self) -> Dict[str, Any]:
        """Stop the active stream"""
        return self.api.stop_stream(self.computer_id)
    
    def stream_status(self) -> Dict[str, Any]:
        """Get the current streaming status"""
        return self.api.get_stream_status(self.computer_id)
    
    # AI control method
    def prompt(self, 
               instruction: str,
               provider: str = "anthropic",
               model: str = "claude-sonnet-4-5-20250929",
               display_width: int = 1024,
               display_height: int = 768,
               callback: Optional[Callable[[str, Any], None]] = None,
               thinking_enabled: bool = True,
               thinking_budget: int = 1024,
               max_tokens: int = 4096,
               max_iterations: int = 100,
               max_saved_screenshots: int = 3,
               api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Control the computer with natural language instructions using an AI assistant"""
        provider_instance = get_provider(provider)
        
        return provider_instance.execute(
            computer_id=self.computer_id,
            instruction=instruction,
            callback=callback,
            api_key=api_key,
            model=model,
            display_width=display_width,
            display_height=display_height,
            thinking_enabled=thinking_enabled,
            thinking_budget=thinking_budget,
            max_tokens=max_tokens,
            max_iterations=max_iterations,
            max_saved_screenshots=max_saved_screenshots,
            orgo_api_key=self.api_key,
            orgo_base_url=self.base_api_url
        )
    
    def __repr__(self):
        project_str = f", project='{self.project_name}'" if hasattr(self, 'project_name') and self.project_name else ""
        name_str = f"name='{self.name}'" if hasattr(self, 'name') and self.name else f"id='{self.computer_id}'"
        return f"Computer({name_str}{project_str})"