#!/usr/bin/env python3
"""
📦 SMITE 2 Assault Advisor - Dependency Installer
Installs all required dependencies for Windows/Linux systems
"""

import subprocess
import sys
import platform
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_python_packages():
    """Install Python packages"""
    packages = [
        "opencv-python",
        "mss", 
        "pytesseract",
        "pyttsx3",
        "numpy",
        "aiohttp",
        "beautifulsoup4",
        "lxml",
        "requests",
        "pillow",
        "psutil"
    ]
    
    # Windows-specific packages
    if platform.system() == "Windows":
        packages.extend(["pywin32"])
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    
    print("✅ Python packages installation completed")

def install_tesseract():
    """Install Tesseract OCR"""
    system = platform.system()
    
    if system == "Windows":
        print("📋 Windows Tesseract Installation:")
        print("1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install to default location (C:\\Program Files\\Tesseract-OCR\\)")
        print("3. Add to PATH or the app will auto-detect")
        
    elif system == "Linux":
        # Try different package managers
        managers = [
            ("apt-get", "sudo apt-get update && sudo apt-get install -y tesseract-ocr"),
            ("yum", "sudo yum install -y tesseract"),
            ("dnf", "sudo dnf install -y tesseract"),
            ("pacman", "sudo pacman -S tesseract")
        ]
        
        for manager, command in managers:
            if subprocess.run(f"which {manager}", shell=True, capture_output=True).returncode == 0:
                if run_command(command, f"Installing Tesseract via {manager}"):
                    break
        else:
            print("⚠️  Could not install Tesseract automatically. Please install manually.")
    
    elif system == "Darwin":  # macOS
        if subprocess.run("which brew", shell=True, capture_output=True).returncode == 0:
            run_command("brew install tesseract", "Installing Tesseract via Homebrew")
        else:
            print("⚠️  Please install Homebrew first, then run: brew install tesseract")

def check_tesseract():
    """Check if Tesseract is properly installed"""
    try:
        result = subprocess.run("tesseract --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract is properly installed")
            return True
        else:
            print("❌ Tesseract not found in PATH")
            return False
    except Exception as e:
        print(f"❌ Error checking Tesseract: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "assault_data",
        "screenshots", 
        "logs",
        "cache"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def test_imports():
    """Test if all imports work"""
    print("🧪 Testing imports...")
    
    imports_to_test = [
        ("cv2", "OpenCV"),
        ("mss", "MSS"),
        ("pytesseract", "Pytesseract"),
        ("pyttsx3", "Text-to-Speech"),
        ("numpy", "NumPy"),
        ("aiohttp", "AsyncHTTP"),
        ("bs4", "BeautifulSoup"),
        ("requests", "Requests"),
        ("PIL", "Pillow"),
        ("psutil", "PSUtil")
    ]
    
    if platform.system() == "Windows":
        imports_to_test.append(("win32gui", "PyWin32"))
    
    failed_imports = []
    
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {name} import successful")
        except ImportError as e:
            print(f"❌ {name} import failed: {e}")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
        print("Please install missing packages manually")
        return False
    else:
        print("✅ All imports successful!")
        return True

def main():
    """Main installation process"""
    print("🎮 SMITE 2 Assault Advisor - Dependency Installer")
    print("=" * 60)
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()
    
    # Create directories
    create_directories()
    
    # Install Python packages
    install_python_packages()
    
    # Install Tesseract
    install_tesseract()
    
    # Check Tesseract
    tesseract_ok = check_tesseract()
    
    # Test imports
    imports_ok = test_imports()
    
    print("\n" + "=" * 60)
    print("📋 Installation Summary:")
    print(f"✅ Python packages: Installed")
    print(f"{'✅' if tesseract_ok else '❌'} Tesseract OCR: {'Ready' if tesseract_ok else 'Needs manual installation'}")
    print(f"{'✅' if imports_ok else '❌'} Import test: {'Passed' if imports_ok else 'Failed'}")
    
    if tesseract_ok and imports_ok:
        print("\n🎉 Installation completed successfully!")
        print("You can now run: python assault_brain_unified.py")
    else:
        print("\n⚠️  Installation completed with issues.")
        print("Please resolve the issues above before running the application.")
    
    print("\n📖 Next steps:")
    print("1. Run: python smite2_data_updater.py (to update game data)")
    print("2. Run: python assault_brain_unified.py (to start the advisor)")
    print("3. Start SMITE 2 and enter an Assault match")

if __name__ == "__main__":
    main()