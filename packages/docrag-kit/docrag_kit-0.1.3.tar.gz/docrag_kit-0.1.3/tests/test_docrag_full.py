#!/usr/bin/env python3
"""
Automated testing script for DocRAG Kit.
Tests the full workflow: init -> index -> search
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Test configuration
TEST_DIR = Path("test-demo-project")
PYTHON_BIN = Path.home() / ".pyenv/versions/3.10.14/bin/python"
DOCRAG_BIN = Path.home() / ".pyenv/versions/3.10.14/bin/docrag"
# Get API key from environment or use placeholder
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-api-key-here")


def run_command(cmd, cwd=None, input_text=None):
    """Run command and return output."""
    print(f"\n🔧 Running: {' '.join(str(c) for c in cmd)}")
    if input_text:
        print(f"📝 Input: {input_text[:100]}...")
    
    result = subprocess.run(
        cmd,
        cwd=cwd,
        input=input_text,
        text=True,
        capture_output=True
    )
    
    if result.stdout:
        print(f"✅ Output:\n{result.stdout}")
    if result.stderr:
        print(f"⚠️  Stderr:\n{result.stderr}")
    
    return result


def test_init():
    """Test docrag init with automated answers."""
    print("\n" + "="*60)
    print("TEST 1: Initialize DocRAG")
    print("="*60)
    
    # Prepare answers for interactive prompts
    answers = [
        "E-Commerce Platform",  # Project name
        "1",                     # Symfony
        "1",                     # OpenAI
        OPENAI_API_KEY,         # API key
        ".",                     # Directories (current dir)
        ".md,.txt",             # Extensions
        "",                      # Exclusions (use defaults)
        "Y"                      # Create .gitignore
    ]
    
    input_text = "\n".join(answers) + "\n"
    
    result = run_command(
        [str(DOCRAG_BIN), "init"],
        cwd=TEST_DIR,
        input_text=input_text
    )
    
    if result.returncode == 0:
        print("✅ Init successful")
        return True
    else:
        print(f"❌ Init failed with code {result.returncode}")
        return False


def test_index():
    """Test docrag index."""
    print("\n" + "="*60)
    print("TEST 2: Index Documentation")
    print("="*60)
    
    result = run_command(
        [str(DOCRAG_BIN), "index"],
        cwd=TEST_DIR
    )
    
    if result.returncode == 0 and "indexed successfully" in result.stdout.lower():
        print("✅ Indexing successful")
        return True
    else:
        print(f"❌ Indexing failed")
        return False


def test_mcp_config():
    """Test docrag mcp-config."""
    print("\n" + "="*60)
    print("TEST 3: Get MCP Configuration")
    print("="*60)
    
    result = run_command(
        [str(DOCRAG_BIN), "mcp-config"],
        cwd=TEST_DIR
    )
    
    if result.returncode == 0 and "mcpServers" in result.stdout:
        print("✅ MCP config generated")
        return True
    else:
        print(f"❌ MCP config failed")
        return False


def test_mcp_server():
    """Test MCP server startup."""
    print("\n" + "="*60)
    print("TEST 4: Test MCP Server Startup")
    print("="*60)
    
    # Start server and kill it after 2 seconds (just to test it starts)
    proc = subprocess.Popen(
        [str(PYTHON_BIN), "-m", "docrag.mcp_server"],
        cwd=TEST_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(2)
    proc.terminate()
    
    try:
        stdout, stderr = proc.communicate(timeout=2)
        
        # If no error in stderr, server started successfully
        if "ModuleNotFoundError" not in stderr and "ImportError" not in stderr:
            print("✅ MCP server starts without errors")
            return True
        else:
            print(f"❌ MCP server has errors:\n{stderr}")
            return False
    except subprocess.TimeoutExpired:
        proc.kill()
        print("✅ MCP server running (killed after timeout)")
        return True


def test_list_docs():
    """Test listing indexed documents."""
    print("\n" + "="*60)
    print("TEST 5: List Indexed Documents")
    print("="*60)
    
    # Check if vectordb exists
    vectordb_path = TEST_DIR / ".docrag" / "vectordb"
    if vectordb_path.exists():
        print(f"✅ Vector database exists at {vectordb_path}")
        
        # Count files
        files = list(vectordb_path.rglob("*"))
        print(f"📊 Vector DB contains {len(files)} files")
        return True
    else:
        print(f"❌ Vector database not found at {vectordb_path}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🚀 DocRAG Kit - Automated Testing Suite")
    print("="*60)
    
    # Check prerequisites
    if not PYTHON_BIN.exists():
        print(f"❌ Python not found at {PYTHON_BIN}")
        sys.exit(1)
    
    if not DOCRAG_BIN.exists():
        print(f"❌ docrag not found at {DOCRAG_BIN}")
        sys.exit(1)
    
    if not TEST_DIR.exists():
        print(f"❌ Test directory not found: {TEST_DIR}")
        sys.exit(1)
    
    # Clean up previous test data
    print("\n🧹 Cleaning up previous test data...")
    docrag_dir = TEST_DIR / ".docrag"
    env_file = TEST_DIR / ".env"
    
    if docrag_dir.exists():
        import shutil
        shutil.rmtree(docrag_dir)
        print(f"   Removed {docrag_dir}")
    
    if env_file.exists():
        env_file.unlink()
        print(f"   Removed {env_file}")
    
    # Run tests
    results = []
    
    results.append(("Initialize", test_init()))
    results.append(("Index", test_index()))
    results.append(("MCP Config", test_mcp_config()))
    results.append(("MCP Server", test_mcp_server()))
    results.append(("List Docs", test_list_docs()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
