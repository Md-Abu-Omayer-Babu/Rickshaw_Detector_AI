"""
Installation verification script.
Run this to check if everything is set up correctly.
"""
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python version: {version.major}.{version.minor}.{version.micro} (Need 3.10+)")
        return False


def check_dependencies():
    """Check if all required packages are installed"""
    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "cv2",
        "ultralytics",
        "torch"
    ]
    
    missing = []
    for package in required:
        try:
            if package == "cv2":
                import cv2
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_file_structure():
    """Check if all required files and directories exist"""
    base_dir = Path(__file__).parent
    
    required_files = [
        "app/main.py",
        "app/core/config.py",
        "app/core/startup.py",
        "app/model/detector.py",
        "app/model/best.pt",
        "app/routes/detect_image.py",
        "app/routes/detect_video.py",
        "app/routes/history.py",
        "app/services/inference_service.py",
        "app/services/video_service.py",
        "app/db/database.py",
        "app/db/models.py",
        "app/utils/file_utils.py",
        "app/utils/draw_utils.py",
        "requirements.txt"
    ]
    
    required_dirs = [
        "app/outputs/images",
        "app/outputs/videos"
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - Missing")
            missing_dirs.append(dir_path)
    
    return len(missing_files) == 0 and len(missing_dirs) == 0


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("🔍 Rickshaw Detection Backend - Installation Verification")
    print("=" * 60)
    
    print("\n📌 Checking Python version...")
    print("-" * 60)
    python_ok = check_python_version()
    
    print("\n📦 Checking dependencies...")
    print("-" * 60)
    deps_ok, missing = check_dependencies()
    
    print("\n📁 Checking file structure...")
    print("-" * 60)
    structure_ok = check_file_structure()
    
    print("\n" + "=" * 60)
    print("📊 Verification Summary")
    print("=" * 60)
    
    all_ok = python_ok and deps_ok and structure_ok
    
    if all_ok:
        print("✅ All checks passed!")
        print("\n🚀 You're ready to run the application:")
        print("   python run.py")
        print("\n📚 Or check the documentation:")
        print("   - README.md for full documentation")
        print("   - QUICKSTART.md for quick start guide")
        return 0
    else:
        print("❌ Some checks failed!")
        
        if not python_ok:
            print("\n⚠️  Please upgrade to Python 3.10 or higher")
        
        if not deps_ok:
            print("\n⚠️  Install missing dependencies:")
            print("   pip install -r requirements.txt")
        
        if not structure_ok:
            print("\n⚠️  Some files or directories are missing")
            print("   Please ensure all files were created correctly")
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
