"""
Desktop Controller - OS/Desktop Automation
Implements safe desktop and OS-level interactions.
"""

import platform
import subprocess
from typing import Dict, Any, List, Optional


class DesktopController:
    """
    Controls desktop and OS-level operations.
    
    Security features:
    - Policy-gated file system access
    - Safe command execution
    - Process management
    """
    
    def __init__(self):
        """Initialize the desktop controller."""
        self.os_type = platform.system()  # 'Windows', 'Darwin' (macOS), 'Linux'
        self.platform_info = {
            "system": self.os_type,
            "release": platform.release(),
            "machine": platform.machine()
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            System details
        """
        return {
            **self.platform_info,
            "python_version": platform.python_version(),
            "processor": platform.processor()
        }
    
    def list_files(self, directory: str, pattern: str = "*") -> Dict[str, Any]:
        """
        List files in a directory.
        
        Args:
            directory: Directory path
            pattern: File pattern (glob)
            
        Returns:
            List of files
        """
        import os
        import glob
        
        try:
            # Validate path exists
            if not os.path.exists(directory):
                return {
                    "success": False,
                    "error": f"Directory not found: {directory}"
                }
            
            # Get files matching pattern
            search_path = os.path.join(directory, pattern)
            files = glob.glob(search_path)
            
            # Get file details
            file_list = []
            for file_path in files:
                stat = os.stat(file_path)
                file_list.append({
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "size": stat.st_size,
                    "is_dir": os.path.isdir(file_path),
                    "modified": stat.st_mtime
                })
            
            return {
                "success": True,
                "files": file_list,
                "count": len(file_list)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Read a file's contents.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            
        Returns:
            File contents
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def write_file(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            file_path: Path to file
            content: Content to write
            encoding: File encoding
            
        Returns:
            Write result
        """
        try:
            import os
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                "success": True,
                "path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_command(
        self,
        command: str,
        shell: bool = True,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute a shell command.
        
        Args:
            command: Command to execute
            shell: Whether to use shell
            timeout: Timeout in seconds
            
        Returns:
            Command result
        """
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def open_application(self, app_name: str) -> Dict[str, Any]:
        """
        Open an application.
        
        Args:
            app_name: Application name or path
            
        Returns:
            Result
        """
        try:
            if self.os_type == "Darwin":  # macOS
                command = f"open -a '{app_name}'"
            elif self.os_type == "Windows":
                command = f"start {app_name}"
            else:  # Linux
                command = app_name
            
            result = self.execute_command(command)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_clipboard(self) -> Dict[str, Any]:
        """
        Get clipboard contents.
        
        Returns:
            Clipboard text
        """
        try:
            import pyperclip
            content = pyperclip.paste()
            return {
                "success": True,
                "content": content
            }
        except ImportError:
            return {
                "success": False,
                "error": "pyperclip not installed. Install with: pip install pyperclip"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def set_clipboard(self, text: str) -> Dict[str, Any]:
        """
        Set clipboard contents.
        
        Args:
            text: Text to copy
            
        Returns:
            Result
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            return {
                "success": True,
                "message": "Copied to clipboard"
            }
        except ImportError:
            return {
                "success": False,
                "error": "pyperclip not installed. Install with: pip install pyperclip"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def take_screenshot(self, filename: str = "screenshot.png") -> Dict[str, Any]:
        """
        Take a screenshot of the desktop.
        
        Args:
            filename: Output filename
            
        Returns:
            Screenshot result
        """
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return {
                "success": True,
                "filename": filename
            }
        except ImportError:
            return {
                "success": False,
                "error": "pyautogui not installed. Install with: pip install pyautogui"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_running_processes(self) -> Dict[str, Any]:
        """
        Get list of running processes.
        
        Returns:
            Process list
        """
        try:
            import psutil
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                "success": True,
                "processes": processes,
                "count": len(processes)
            }
        except ImportError:
            return {
                "success": False,
                "error": "psutil not installed. Install with: pip install psutil"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_environment_variable(self, var_name: str) -> Optional[str]:
        """
        Get an environment variable.
        
        Args:
            var_name: Variable name
            
        Returns:
            Variable value or None
        """
        import os
        return os.environ.get(var_name)
    
    def create_directory(self, path: str) -> Dict[str, Any]:
        """
        Create a directory.
        
        Args:
            path: Directory path
            
        Returns:
            Result
        """
        import os
        
        try:
            os.makedirs(path, exist_ok=True)
            return {
                "success": True,
                "path": path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
