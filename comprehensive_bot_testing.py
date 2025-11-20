"""
Comprehensive Bot Testing Script
Acts as a human tester, performs queries, logs everything, and evaluates results
"""
import sys
from pathlib import Path
import json
from datetime import datetime
import traceback

sys.path.insert(0, str(Path(__file__).parent))

from src.agent.ecommerce_agent import ECommerceAgent

class BotTester:
    def __init__(self):
        self.agent = ECommerceAgent()
        self.log_file = f"bot_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.results = {
            "test_start_time": datetime.now().isoformat(),
            "test_cases": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "issues_found": []
            }
        }
        
    def log_test_case(self, test_name, query, user_email, expected_behavior, actual_result):
        """Log a test case with results"""
        test_case = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "user_email": user_email or "NOT PROVIDED",
            "expected_behavior": expected_behavior,
            "actual_result": {
                "answer": actual_result.get("answer", ""),
                "steps": actual_result.get("steps", ""),
                "iterations": actual_result.get("iterations", 0),
                "tool_usage": actual_result.get("tool_usage", 0),
                "tool_calls": actual_result.get("debug_info", {}).get("tool_calls", [])
            },
            "passed": False,
            "issues": []
        }
        
        # Evaluate if test passed
        answer_lower = test_case["actual_result"]["answer"].lower()
        tool_calls = test_case["actual_result"]["tool_calls"]
        tool_names = [tc.get("tool", "") for tc in tool_calls]
        
        # Check expected behavior
        if "should use search_orders" in expected_behavior.lower():
            if "search_orders" in tool_names:
                test_case["passed"] = True
            else:
                test_case["issues"].append("Expected search_orders tool to be called but it wasn't")
        
        elif "should ask for order number" in expected_behavior.lower():
            if "order number" in answer_lower and ("can you" in answer_lower or "share" in answer_lower):
                test_case["passed"] = True
            else:
                test_case["issues"].append("Expected bot to ask for order number but it didn't")
        
        elif "should use get_order" in expected_behavior.lower():
            if "get_order" in tool_names:
                test_case["passed"] = True
            else:
                test_case["issues"].append("Expected get_order tool to be called but it wasn't")
        
        elif "should provide answer" in expected_behavior.lower():
            if len(test_case["actual_result"]["answer"]) > 20:
                test_case["passed"] = True
            else:
                test_case["issues"].append("Expected meaningful answer but got short/empty response")
        
        # Check for common issues
        if not test_case["passed"]:
            if "apologize" in answer_lower and "couldn't process" in answer_lower:
                test_case["issues"].append("Bot returned error message")
            if test_case["actual_result"]["iterations"] == 0:
                test_case["issues"].append("No iterations completed - workflow may have failed")
        
        # Update summary
        self.results["summary"]["total_tests"] += 1
        if test_case["passed"]:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
            self.results["summary"]["issues_found"].extend(test_case["issues"])
        
        self.results["test_cases"].append(test_case)
        self.save_log()
        
        return test_case
    
    def save_log(self):
        """Save current test results to log file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
    
    def print_test_result(self, test_case):
        """Print test result in readable format"""
        status = "[PASSED]" if test_case["passed"] else "[FAILED]"
        print(f"\n{status} - {test_case['test_name']}")
        print(f"  Query: {test_case['query']}")
        print(f"  User: {test_case['user_email']}")
        print(f"  Answer: {test_case['actual_result']['answer'][:150]}...")
        print(f"  Tools called: {len(test_case['actual_result']['tool_calls'])}")
        if test_case['actual_result']['tool_calls']:
            for tc in test_case['actual_result']['tool_calls']:
                print(f"    - {tc.get('tool', 'unknown')}")
        if test_case['issues']:
            print(f"  Issues: {', '.join(test_case['issues'])}")
    
    def run_test(self, test_name, query, user_email=None, expected_behavior=""):
        """Run a single test case"""
        print(f"\n{'='*80}")
        print(f"TEST: {test_name}")
        print(f"{'='*80}")
        print(f"Query: {query}")
        print(f"User Email: {user_email or 'NOT PROVIDED'}")
        print(f"Expected: {expected_behavior}")
        print("\nProcessing...")
        
        try:
            result = self.agent.process_query(
                query=query,
                user_email=user_email,
                thread_id=f"test_{test_name.replace(' ', '_').lower()}"
            )
            
            test_case = self.log_test_case(
                test_name, query, user_email, expected_behavior, result
            )
            
            self.print_test_result(test_case)
            return test_case
            
        except Exception as e:
            print(f"\n[ERROR] in test: {e}")
            traceback.print_exc()
            test_case = {
                "test_name": test_name,
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "user_email": user_email or "NOT PROVIDED",
                "expected_behavior": expected_behavior,
                "actual_result": {
                    "answer": f"ERROR: {str(e)}",
                    "error": str(e),
                    "traceback": traceback.format_exc()
                },
                "passed": False,
                "issues": [f"Test failed with exception: {str(e)}"]
            }
            self.results["test_cases"].append(test_case)
            self.results["summary"]["total_tests"] += 1
            self.results["summary"]["failed"] += 1
            self.results["summary"]["issues_found"].append(f"{test_name}: {str(e)}")
            self.save_log()
            return test_case
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n" + "="*80)
        print("COMPREHENSIVE BOT TESTING - ACTING AS HUMAN TESTER")
        print("="*80)
        print(f"Log file: {self.log_file}")
        
        # Test Case 1: Logged-in user asking about all orders
        self.run_test(
            "Logged-in: How many orders in my account",
            "I want to know that how many orders are belong to my account currently",
            user_email="john@example.com",
            expected_behavior="Should use search_orders tool with user_email parameter"
        )
        
        # Test Case 2: Logged-in user asking about "my orders"
        self.run_test(
            "Logged-in: List my orders",
            "Show me all my orders",
            user_email="john@example.com",
            expected_behavior="Should use search_orders tool with user_email parameter"
        )
        
        # Test Case 3: Logged-in user asking about orders count
        self.run_test(
            "Logged-in: Count my orders",
            "How many orders do I have?",
            user_email="john@example.com",
            expected_behavior="Should use search_orders tool with user_email parameter"
        )
        
        # Test Case 4: Non-logged-in user asking about orders
        self.run_test(
            "Not logged-in: How many orders",
            "I want to know that how many orders are belong to my account currently",
            user_email=None,
            expected_behavior="Should ask for order number or login"
        )
        
        # Test Case 5: Logged-in user tracking specific order
        self.run_test(
            "Logged-in: Track order ORD-12345",
            "What is the status of order ORD-12345?",
            user_email="john@example.com",
            expected_behavior="Should use get_order tool with order number"
        )
        
        # Test Case 6: Non-logged-in user tracking order
        self.run_test(
            "Not logged-in: Track order",
            "I want to track my order ORD-12345",
            user_email=None,
            expected_behavior="Should use get_user_email_from_order, then send_2fa_code, then verify"
        )
        
        # Test Case 7: Logged-in user asking about return policy
        self.run_test(
            "Logged-in: Return policy",
            "What is your return policy?",
            user_email="john@example.com",
            expected_behavior="Should provide answer about return policy"
        )
        
        # Test Case 8: Memory test - follow-up query
        self.run_test(
            "Memory: Follow-up after order query",
            "What about my other orders?",
            user_email="john@example.com",
            expected_behavior="Should use search_orders tool (remembering previous context)"
        )
        
        # Test Case 9: Logged-in user asking about orders with different phrasing
        self.run_test(
            "Logged-in: Orders in my account",
            "What orders are in my account?",
            user_email="john@example.com",
            expected_behavior="Should use search_orders tool with user_email parameter"
        )
        
        # Test Case 10: Edge case - empty query
        self.run_test(
            "Edge case: Empty query",
            "",
            user_email="john@example.com",
            expected_behavior="Should handle gracefully"
        )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        summary = self.results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ({summary['passed']/summary['total_tests']*100:.1f}%)")
        print(f"Failed: {summary['failed']} ({summary['failed']/summary['total_tests']*100:.1f}%)")
        
        if summary['issues_found']:
            print(f"\nIssues Found ({len(summary['issues_found'])}):")
            for i, issue in enumerate(set(summary['issues_found']), 1):
                print(f"  {i}. {issue}")
        
        print(f"\nDetailed log saved to: {self.log_file}")
        print("="*80)
    
    def evaluate_and_recommend(self):
        """Evaluate results and provide recommendations"""
        print("\n" + "="*80)
        print("EVALUATION AND RECOMMENDATIONS")
        print("="*80)
        
        failed_tests = [tc for tc in self.results["test_cases"] if not tc["passed"]]
        
        if not failed_tests:
            print("[SUCCESS] ALL TESTS PASSED! Bot is working correctly.")
            return
        
        print(f"\n[FAILED] {len(failed_tests)} test(s) failed. Analysis:")
        
        # Group issues by type
        issue_types = {}
        for test in failed_tests:
            for issue in test.get("issues", []):
                issue_type = issue.split(":")[0] if ":" in issue else issue
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append({
                    "test": test["test_name"],
                    "issue": issue
                })
        
        print("\nIssue Categories:")
        for issue_type, occurrences in issue_types.items():
            print(f"\n  {issue_type} ({len(occurrences)} occurrences):")
            for occ in occurrences[:3]:  # Show first 3
                print(f"    - {occ['test']}: {occ['issue']}")
        
        # Recommendations
        print("\nRecommendations:")
        if any("search_orders" in str(issue) for test in failed_tests for issue in test.get("issues", [])):
            print("  1. Check system prompt - ensure it clearly instructs to use search_orders for 'my orders' queries")
            print("  2. Verify context detection logic in _reason_node")
        
        if any("error" in str(issue).lower() for test in failed_tests for issue in test.get("issues", [])):
            print("  3. Check message formatting - ensure ToolMessages are properly paired")
            print("  4. Review workflow error handling")
        
        if any("iterations" in str(issue) for test in failed_tests for issue in test.get("issues", [])):
            print("  5. Check workflow completion logic")
            print("  6. Verify iteration limits and stopping conditions")

if __name__ == "__main__":
    tester = BotTester()
    tester.run_all_tests()
    tester.evaluate_and_recommend()

