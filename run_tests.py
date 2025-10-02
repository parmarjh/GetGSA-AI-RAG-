#!/usr/bin/env python3
"""
Test runner for GetGSA application
"""
import subprocess
import sys
import os

def run_tests():
    """Run all tests"""
    print("Running GetGSA Test Suite...")
    print("=" * 50)
    
    # Change to the project root directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with verbose output
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        return e.returncode

if __name__ == "__main__":
    sys.exit(run_tests())
