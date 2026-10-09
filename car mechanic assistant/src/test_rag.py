"""
Test and evaluation script for RAG system
"""
from .rag_system import MechanicAssistant
from typing import List, Dict, Any
import json


class RAGTester:
    """Test suite for RAG system"""

    def __init__(self):
        self.assistant = MechanicAssistant()
        self.test_cases = self._load_test_cases()

    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases"""
        return [
            {
                "name": "BMW N54 HPFP Failure",
                "query": "2008 BMW 335i hard to start when hot, loses power under boost",
                "expected_keywords": ["HPFP", "high pressure fuel pump", "N54", "fuel pressure"],
                "expected_folder": "10_troubleshooting_database"
            },
            {
                "name": "P0300 Misfire Code",
                "query": "P0300 code on my car, what does it mean?",
                "expected_keywords": ["misfire", "ignition", "coil", "spark plug"],
                "expected_folder": "03_fault_codes"
            },
            {
                "name": "Rough Idle Diagnosis",
                "query": "Engine shakes and vibrates at idle, what to check?",
                "expected_keywords": ["ignition", "vacuum leak", "misfire"],
                "expected_folder": "02_diagnostic_procedures"
            },
            {
                "name": "Oil Specification",
                "query": "What oil should I use in a turbocharged engine?",
                "expected_keywords": ["synthetic", "specification"],
                "expected_folder": "09_workshop_rules"
            },
            {
                "name": "Paint Code Lookup",
                "query": "BMW paint code 300, what color is this?",
                "expected_keywords": ["Alpine White", "solid"],
                "expected_folder": "07_paint_codes"
            },
            {
                "name": "Repair Procedure",
                "query": "How do I replace injectors on N54 engine?",
                "expected_keywords": ["injector", "coding", "INPA", "fuel rail"],
                "expected_folder": "04_repair_procedures"
            },
            {
                "name": "Labor Time Estimate",
                "query": "How long does timing belt replacement take?",
                "expected_keywords": ["hours", "labor", "water pump"],
                "expected_folder": "08_pricing_valuation"
            },
            {
                "name": "Honda VTC Rattle",
                "query": "Honda makes rattling noise on cold start for a few seconds",
                "expected_keywords": ["VTC", "actuator", "K-series", "cold start"],
                "expected_folder": "10_troubleshooting_database"
            },
        ]

    def run_test(self, test_case: Dict[str, Any], verbose: bool = True) -> Dict[str, Any]:
        """Run a single test case"""
        if verbose:
            print(f"\n{'='*80}")
            print(f"TEST: {test_case['name']}")
            print(f"{'='*80}")
            print(f"Query: {test_case['query']}")

        # Query the system
        result = self.assistant.query(test_case['query'], verbose=False)

        # Evaluate results
        evaluation = self._evaluate_result(test_case, result)

        if verbose:
            print(f"\nResponse:")
            print(result['response'][:500] + "..." if len(result['response']) > 500 else result['response'])
            print(f"\nSources used:")
            for source in result['sources']:
                print(f"  - {source['folder']}/{source['file']} (score: {source['score']:.1f})")

            print(f"\nEvaluation:")
            print(f"  ✓ Keywords found: {evaluation['keywords_found']}/{evaluation['keywords_total']}")
            print(f"  ✓ Expected folder: {evaluation['folder_match']}")
            print(f"  Overall: {'PASS' if evaluation['pass'] else 'FAIL'}")

        return evaluation

    def _evaluate_result(self, test_case: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate query result against expected outcomes"""
        response = result['response'].lower()
        sources = result['sources']

        # Check keywords
        keywords_found = sum(1 for kw in test_case['expected_keywords'] if kw.lower() in response)
        keywords_total = len(test_case['expected_keywords'])

        # Check if expected folder is in sources
        folder_match = any(
            test_case['expected_folder'] in source['folder']
            for source in sources
        )

        # Overall pass/fail
        pass_test = (keywords_found >= keywords_total * 0.5) and folder_match

        return {
            "keywords_found": keywords_found,
            "keywords_total": keywords_total,
            "folder_match": folder_match,
            "pass": pass_test,
            "response_length": len(result['response'])
        }

    def run_all_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """Run all test cases"""
        print("\n" + "="*80)
        print("RUNNING RAG SYSTEM TESTS")
        print("="*80)

        results = []
        for test_case in self.test_cases:
            evaluation = self.run_test(test_case, verbose=verbose)
            results.append({
                "name": test_case['name'],
                "evaluation": evaluation
            })

        # Summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['evaluation']['pass'])

        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests/total_tests*100:.1f}%")

        print("\nDetailed Results:")
        for result in results:
            status = "✓ PASS" if result['evaluation']['pass'] else "✗ FAIL"
            print(f"  {status}: {result['name']}")

        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": passed_tests/total_tests,
            "details": results
        }


def main():
    """Main test function"""
    tester = RAGTester()
    results = tester.run_all_tests(verbose=True)

    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to test_results.json")


if __name__ == "__main__":
    main()
