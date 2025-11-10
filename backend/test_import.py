"""Test script to identify blocking imports."""
import sys
import multiprocessing
import time

def test_import():
    """Try to import main module."""
    sys.path.insert(0, 'src')
    print("Starting import...")
    try:
        from main import app
        print("Import successful!")
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False

if __name__ == "__main__":
    # Use multiprocessing to test with timeout
    process = multiprocessing.Process(target=test_import)
    process.start()
    process.join(timeout=10)
    
    if process.is_alive():
        print("\nImport is hanging! Terminating...")
        process.terminate()
        process.join()
        print("Import hung for 10+ seconds - likely deadlock in initialization")
    else:
        print(f"\nProcess completed with exit code: {process.exitcode}")
