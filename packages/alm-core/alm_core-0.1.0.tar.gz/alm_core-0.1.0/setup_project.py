#!/usr/bin/env python3
"""
ALM Core - Cross-Platform Setup Script
Automatically sets up the project for Linux, Windows, and macOS
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

class ALMSetup:
    """Cross-platform setup manager for ALM Core"""
    
    def __init__(self):
        self.system = platform.system()
        self.project_root = Path(__file__).parent.resolve()
        self.python_cmd = self._get_python_command()
        
    def _get_python_command(self):
        """Detect the correct Python command"""
        for cmd in ['python3', 'python', 'py']:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return cmd
            except FileNotFoundError:
                continue
        return 'python'
    
    def print_header(self):
        """Print setup header"""
        print("=" * 70)
        print("🚀 ALM Core - Automated Setup")
        print("=" * 70)
        print(f"Platform: {self.system}")
        print(f"Python: {self.python_cmd}")
        print(f"Project: {self.project_root}")
        print("=" * 70)
        print()
    
    def check_python_version(self):
        """Ensure Python 3.8+"""
        print("✓ Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python 3.8+ required (found {version.major}.{version.minor})")
            sys.exit(1)
        print(f"  Python {version.major}.{version.minor}.{version.micro} ✓")
        print()
    
    def create_virtual_environment(self):
        """Create virtual environment"""
        print("✓ Creating virtual environment...")
        venv_path = self.project_root / 'venv'
        
        if venv_path.exists():
            print("  Virtual environment already exists")
        else:
            subprocess.run([self.python_cmd, '-m', 'venv', 'venv'], check=True)
            print("  Virtual environment created ✓")
        print()
        
        return venv_path
    
    def get_pip_command(self, venv_path):
        """Get the pip command for the virtual environment"""
        if self.system == "Windows":
            return str(venv_path / "Scripts" / "pip.exe")
        else:
            return str(venv_path / "bin" / "pip")
    
    def install_dependencies(self, pip_cmd):
        """Install Python dependencies"""
        print("✓ Installing dependencies...")
        
        # Upgrade pip
        print("  Upgrading pip...")
        subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], check=True)
        
        # Install requirements
        print("  Installing requirements...")
        subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
        
        # Install package in editable mode
        print("  Installing ALM Core in editable mode...")
        subprocess.run([pip_cmd, 'install', '-e', '.'], check=True)
        
        print("  Dependencies installed ✓")
        print()
    
    def setup_environment_file(self):
        """Create .env file if it doesn't exist"""
        print("✓ Setting up environment...")
        
        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'
        
        if not env_file.exists() and env_example.exists():
            shutil.copy(env_example, env_file)
            print("  Created .env file from template")
            print("  ⚠️  Remember to add your API keys to .env")
        elif env_file.exists():
            print("  .env file already exists")
        else:
            # Create basic .env
            with open(env_file, 'w') as f:
                f.write("# ALM Core Environment Variables\n")
                f.write("OPENAI_API_KEY=your-key-here\n")
                f.write("OPENAI_MODEL=gpt-3.5-turbo\n")
            print("  Created basic .env file")
            print("  ⚠️  Remember to add your API keys to .env")
        
        print()
    
    def make_scripts_executable(self):
        """Make shell scripts executable (Unix-like systems)"""
        if self.system in ['Linux', 'Darwin']:
            print("✓ Making scripts executable...")
            scripts_dir = self.project_root / 'scripts'
            if scripts_dir.exists():
                for script in scripts_dir.glob('*.sh'):
                    os.chmod(script, 0o755)
                print(f"  Made {len(list(scripts_dir.glob('*.sh')))} scripts executable ✓")
            print()
    
    def print_next_steps(self):
        """Print next steps for the user"""
        venv_activate = self._get_activation_command()
        
        print("=" * 70)
        print("✅ Setup Complete!")
        print("=" * 70)
        print()
        print("Next Steps:")
        print()
        print("1. Activate virtual environment:")
        print(f"   {venv_activate}")
        print()
        print("2. Set your API key in .env:")
        print("   OPENAI_API_KEY=sk-your-actual-key")
        print()
        print("3. Run examples:")
        print("   python examples/test_real_api.py")
        print("   python examples/interactive_browser_bot.py")
        print("   python examples/test_research_working.py")
        print()
        print("4. Run tests:")
        print("   pytest tests/")
        print()
        print("Documentation:")
        print("  README.md           - Main documentation")
        print("  docs/QUICKSTART.md  - Quick start guide")
        print("  docs/INSTALLATION.md - Detailed installation")
        print()
        print("=" * 70)
    
    def _get_activation_command(self):
        """Get the virtual environment activation command"""
        if self.system == "Windows":
            return "venv\\Scripts\\activate"
        else:
            return "source venv/bin/activate"
    
    def run(self):
        """Run the complete setup process"""
        try:
            self.print_header()
            self.check_python_version()
            venv_path = self.create_virtual_environment()
            pip_cmd = self.get_pip_command(venv_path)
            self.install_dependencies(pip_cmd)
            self.setup_environment_file()
            self.make_scripts_executable()
            self.print_next_steps()
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error during setup: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    setup = ALMSetup()
    setup.run()
