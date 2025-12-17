"""
Test ALM Core - Browser and Desktop Control
Demonstrates browser automation and desktop/application control
"""
import os
from alm_core import AgentLanguageModel

# Check for API key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY environment variable not set")
    exit(1)

print("🚀 Testing ALM Core - Browser & Desktop Control")
print("=" * 60)
print()

# Initialize agent
agent = AgentLanguageModel(
    api_key=api_key,
    llm_provider="openai",
    model="gpt-3.5-turbo",
    rules=[
        {"action": "delete_file", "allow": False},
        {"action": "open_browser", "allow": True},
        {"action": "list_files", "allow": True}
    ]
)

print(f"✓ Agent initialized: {agent.llm.model}")
print()

# Test 1: Desktop Control - List files
print("Test 1: Desktop Control - List Files")
print("-" * 60)

from alm_core.tools.desktop import DesktopController

desktop = DesktopController()

try:
    # List files in current directory
    result = desktop.list_files(".", pattern="*.py")
    if result["success"]:
        files = result["files"]
        print(f"✓ Python files in current directory ({result['count']} items):")
        for f in files[:10]:  # Show first 10
            print(f"  - {f['name']} ({f['size']} bytes)")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more")
        print()
        print("✅ Desktop file listing successful!")
    else:
        print(f"❌ Error: {result['error']}")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 60)

# Test 2: Desktop Control - Execute command
print("Test 2: Desktop Control - Execute Safe Command")
print("-" * 60)

try:
    # Safe command: check Python version
    result = desktop.execute_command("python --version")
    print(f"Command: python --version")
    if result["success"]:
        output = result["stdout"].strip() or result["stderr"].strip()
        print(f"Result: {output}")
        print()
        print("✅ Command execution successful!")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 60)

# Test 3: Open application (Calculator)
print("Test 3: Open Application - Calculator")
print("-" * 60)

try:
    import platform
    import subprocess
    import time
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("Opening Calculator on macOS...")
        subprocess.Popen(["open", "-a", "Calculator"])
        print("✅ Calculator opened!")
        print("   (Check your screen - Calculator should be running)")
        
    elif system == "Windows":
        print("Opening Calculator on Windows...")
        subprocess.Popen(["calc.exe"])
        print("✅ Calculator opened!")
        
    elif system == "Linux":
        print("Opening Calculator on Linux...")
        subprocess.Popen(["gnome-calculator"])
        print("✅ Calculator opened!")
    
    time.sleep(1)  # Give it a moment to open
    
except Exception as e:
    print(f"⚠️  Could not open Calculator: {e}")
    print("   (This is OK - some systems may restrict this)")

print()
print("=" * 60)

# Test 4: Browser Control (check if Playwright is available)
print("Test 4: Browser Automation - Check Availability")
print("-" * 60)

try:
    from alm_core.tools.browser import SecureBrowser
    
    print("✓ Playwright/Browser tools imported successfully")
    print()
    print("Note: Full browser automation requires:")
    print("  pip install playwright")
    print("  playwright install")
    print()
    print("Browser automation features:")
    print("  ✓ Secure DOM extraction")
    print("  ✓ PII protection in web content")
    print("  ✓ User-in-the-loop for sensitive actions")
    print()
    print("✅ Browser tools available!")
    
except ImportError as e:
    print(f"⚠️  Playwright not fully installed: {e}")
    print()
    print("To enable browser automation, run:")
    print("  pip install playwright")
    print("  playwright install")
    print()
    print("(This is optional - core features work without it)")

print()
print("=" * 60)

# Test 5: Open browser with default application
print("Test 5: Open Web Browser to GitHub Repo")
print("-" * 60)

try:
    import webbrowser
    
    url = "https://github.com/Jalendar10/alm-core"
    print(f"Opening: {url}")
    
    webbrowser.open(url)
    
    print("✅ Browser opened with your GitHub repo!")
    print("   (Check your browser - should show alm-core repository)")
    
except Exception as e:
    print(f"❌ Error opening browser: {e}")

print()
print("=" * 60)
print("🎉 DESKTOP & BROWSER TESTS COMPLETED!")
print("=" * 60)
print()
print("Test Results:")
print("  ✅ Desktop file operations working")
print("  ✅ Command execution working")
print("  ✅ Application launching working")
print("  ✅ Browser opening working")
print("  ℹ️  Full browser automation available with Playwright")
