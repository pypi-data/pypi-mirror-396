import sys
import inspect
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

def main():
    print("🚀 Verifying DroidRun MCP Tools (Static Check)...")

    try:
        from server import execute_task, get_trajectory, get_single_screenshot, get_screenshots
    except ImportError as e:
        print(f"❌ Could not import server: {e}")
        print("Make sure 'fastmcp' and 'droidrun' are installed/available in your environment.")
        sys.exit(1)

    # check param
    def verify_signature(func, required_params):
        sig = inspect.signature(func)
        missing = [p for p in required_params if p not in sig.parameters]
        if missing:
            print(f"   ❌ {func.__name__}: Missing parameters {missing}")
        else:
            print(f"   ✅ {func.__name__}: Found parameters {required_params}")

    # 1. execute_task check
    print("\nChecking execute_task...")
    verify_signature(execute_task, ["instruction", "apk_path"])
    
    # 2. check get_screenshots
    print("\nChecking get_screenshots...")
    verify_signature(get_screenshots, ["session_id", "max_screenshots", "scale"])

    # 3. check get_single_screenshot
    print("\nChecking get_single_screenshot...")
    verify_signature(get_single_screenshot, ["session_id", "step", "scale"])

    # 4. check get_trajectory
    print("\nChecking get_trajectory...")
    verify_signature(get_trajectory, ["session_id"])

    print("\n✨ Verification Complete.")

if __name__ == "__main__":
    main()
