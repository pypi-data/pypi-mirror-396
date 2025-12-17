#!/usr/bin/env python3
"""
Cross-platform test for the terminal tool.
Tests platform detection, shell selection, and basic functionality.
"""

import os
import sys
import tempfile
import shutil
import platform
from orchestral.tools.terminal_tool import RunCommandTool, PEXPECT_AVAILABLE

def test_platform_detection():
    """Test platform detection and shell selection."""
    print("🔍 Testing platform detection...")
    print(f"Platform: {platform.system()}")
    print(f"Architecture: {platform.machine()}")
    print(f"pexpect available: {PEXPECT_AVAILABLE}")

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir)

    try:
        shell_cmd = tool._get_shell_command()
        print(f"Selected shell: {shell_cmd}")

        # Test if shell is actually available
        shell_binary = shell_cmd.split()[0]
        available = shutil.which(shell_binary) is not None
        print(f"Shell available: {available}")

    finally:
        shutil.rmtree(base_dir)

def test_basic_cross_platform_commands():
    """Test basic commands that work across platforms."""
    print("\n🧪 Testing cross-platform commands...")

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir)

    try:
        # Create some test files first
        import os
        with open(os.path.join(base_dir, "test1.txt"), "w") as f:
            f.write("test file 1")
        with open(os.path.join(base_dir, "test2.txt"), "w") as f:
            f.write("test file 2")

        # Test echo (works on all platforms)
        result = tool.execute(command="echo 'Cross-platform test'")
        print("✅ Echo test:")
        print(result)
        print("-" * 50)

        # Test directory listing (platform-specific commands)
        if platform.system().lower() == "windows":
            result = tool.execute(command="dir")
        else:
            result = tool.execute(command="ls")
        print("✅ Directory listing:")
        print(result)
        print("-" * 50)

        # Test Python (should work on all platforms)
        result = tool.execute(command="python --version")
        print("✅ Python version:")
        print(result)
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error during cross-platform test: {e}")
    finally:
        shutil.rmtree(base_dir)

def test_persistent_mode_cross_platform():
    """Test persistent mode across platforms."""
    print("\n🧪 Testing persistent mode cross-platform...")

    if not PEXPECT_AVAILABLE:
        print("⚠️ Skipping persistent mode test - pexpect not available")
        return

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

    try:
        # Create directory
        if platform.system().lower() == "windows":
            result = tool.execute(command="mkdir test_dir")
        else:
            result = tool.execute(command="mkdir test_dir")
        print("✅ Create directory:")
        print(result)
        print("-" * 50)

        # Change to directory
        result = tool.execute(command="cd test_dir")
        print("✅ Change directory:")
        print(result)
        print("-" * 50)

        # Test if we're in the directory (platform-specific)
        if platform.system().lower() == "windows":
            result = tool.execute(command="cd")  # Windows cd without args shows current dir
        else:
            result = tool.execute(command="pwd")
        print("✅ Current directory:")
        print(result)
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error during persistent mode test: {e}")
    finally:
        tool.close_session()
        shutil.rmtree(base_dir)

def test_fallback_behavior():
    """Test fallback to one-shot mode when needed."""
    print("\n🧪 Testing fallback behavior...")

    base_dir = tempfile.mkdtemp()

    try:
        # Force one-shot mode
        tool_oneshot = RunCommandTool(base_directory=base_dir, persistent_mode=False)
        result = tool_oneshot.execute(command="echo 'One-shot mode test'")
        print("✅ One-shot mode:")
        print(result)
        print("-" * 50)

        # Test auto-fallback (should work even if persistent fails)
        tool_auto = RunCommandTool(base_directory=base_dir, persistent_mode=True, auto_fallback=True)
        result = tool_auto.execute(command="echo 'Auto-fallback test'")
        print("✅ Auto-fallback mode:")
        print(result)
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error during fallback test: {e}")
    finally:
        shutil.rmtree(base_dir)

def main():
    """Run all cross-platform tests."""
    print("🚀 Starting cross-platform terminal tool tests...")
    print(f"Running on: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 60)

    try:
        test_platform_detection()
        test_basic_cross_platform_commands()
        test_persistent_mode_cross_platform()
        test_fallback_behavior()

        print("\n🎉 All cross-platform tests completed!")

    except Exception as e:
        print(f"\n❌ Cross-platform test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()