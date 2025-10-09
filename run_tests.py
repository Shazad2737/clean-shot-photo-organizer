#!/usr/bin/env python3
"""
Test runner script for CLEAN SHOT Photo Organizer.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """Run all tests with coverage."""
    print("🧪 Running CLEAN SHOT Tests...")
    print("=" * 50)
    
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Run tests with coverage
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "--cov=src/",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "-v"
        ], cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            print("📊 Coverage report generated in htmlcov/")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest pytest-cov")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
