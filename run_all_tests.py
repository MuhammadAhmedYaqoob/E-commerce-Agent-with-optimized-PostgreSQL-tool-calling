"""
Run all tests for the order tracking system
"""
import subprocess
import sys
import time
from pathlib import Path

def run_tests():
    """Run all test suites"""
    print("="*70)
    print("COMPREHENSIVE TEST SUITE - ORDER TRACKING SYSTEM")
    print("="*70)
    
    test_files = [
        "tests/test_agent_order_tracking.py",
        "tests/test_integration_order_tracking.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"⚠️  Test file not found: {test_file}")
            continue
        
        print(f"\n{'='*70}")
        print(f"Running: {test_file}")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "-s", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            elapsed = time.time() - start_time
            
            results[test_file] = {
                "success": result.returncode == 0,
                "elapsed": elapsed,
                "output": result.stdout + result.stderr
            }
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode == 0:
                print(f"\n✅ {test_file} PASSED in {elapsed:.2f}s")
            else:
                print(f"\n❌ {test_file} FAILED in {elapsed:.2f}s")
                
        except subprocess.TimeoutExpired:
            print(f"\n⏱️  {test_file} TIMED OUT after 5 minutes")
            results[test_file] = {"success": False, "elapsed": 300, "output": "Timeout"}
        except Exception as e:
            print(f"\n❌ Error running {test_file}: {e}")
            results[test_file] = {"success": False, "elapsed": 0, "output": str(e)}
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r["success"])
    total_time = sum(r["elapsed"] for r in results.values())
    
    for test_file, result in results.items():
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{status} - {test_file} ({result['elapsed']:.2f}s)")
    
    print(f"\n📊 Total: {passed_tests}/{total_tests} test suites passed")
    print(f"⏱️  Total time: {total_time:.2f}s")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test suite(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())

