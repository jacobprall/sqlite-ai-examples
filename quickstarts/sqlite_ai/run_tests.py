#!/usr/bin/env python3
"""
Comprehensive test runner for the SQLite-AI chatbot tutorial.

This script runs all tests and provides detailed results, supporting both
unittest and pytest frameworks with various configuration options.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --verbose          # Verbose output
    python run_tests.py --coverage         # With coverage report
    python run_tests.py --fast             # Skip slow tests
    python run_tests.py --integration      # Run integration tests only
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path

def check_environment():
    """Check that we're in the right directory and have required files."""
    if not os.path.exists('tests/'):
        print("❌ tests/ directory not found. Are you in the right directory?")
        return False

    return True

def check_dependencies():
    """Check if test dependencies are installed."""
    missing = []
    optional_missing = []
    
    # Required dependencies
    try:
        import click
    except ImportError:
        missing.append('click')
    
    # Optional but recommended dependencies
    try:
        import pytest
    except ImportError:
        optional_missing.append('pytest')
    
    try:
        import pytest_cov
    except ImportError:
        optional_missing.append('pytest-cov')
    
    if missing:
        print(f"❌ Missing required dependencies: {', '.join(missing)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    if optional_missing:
        print(f"⚠️  Missing optional dependencies: {', '.join(optional_missing)}")
        print("💡 Install with: pip install -r requirements.txt")
        print("   (Some test features may be limited)")
    
    return True

def run_unittest_tests(verbose=False):
    """Run unittest-based tests."""
    print("\n🧪 Running unittest tests...")
    print("─" * 40)
    
    cmd = [sys.executable, '-m', 'unittest']
    if verbose:
        cmd.append('-v')
    
    # Discover and run all unittest tests
    cmd.extend(['discover', '-s', 'tests', '-p', 'test_*.py'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ Unittest tests passed!")
            if verbose:
                print(result.stdout)
        else:
            print("❌ Unittest tests failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running unittest: {e}")
        return False

def run_pytest_tests(verbose=False, coverage=False, fast=False, integration_only=False):
    """Run pytest-based tests."""
    print("\n🧪 Running pytest tests...")
    print("─" * 40)
    
    cmd = [sys.executable, '-m', 'pytest']
    
    # Coverage options
    if coverage:
        cmd.extend(['--cov=ai', '--cov-report=term-missing', '--cov-report=html'])
    
    # Verbosity
    if verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    # Test selection
    if fast:
        cmd.extend(['-m', 'not slow'])
    elif integration_only:
        cmd.extend(['-m', 'integration'])
    
    # Add test directory
    cmd.append('tests/')
    
    try:
        result = subprocess.run(cmd, cwd='.')
        
        if result.returncode == 0:
            print("✅ Pytest tests passed!")
            if coverage:
                print("📊 Coverage report generated in htmlcov/")
        else:
            print("❌ Pytest tests failed!")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return False

def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test method."""
    print(f"\n🎯 Running specific test: {test_path}")
    print("─" * 40)
    
    if test_path.endswith('.py') or '::' in test_path:
        # Use pytest for specific test files/methods
        cmd = [sys.executable, '-m', 'pytest']
        if verbose:
            cmd.append('-v')
        cmd.append(test_path)
    else:
        # Use unittest for test classes
        cmd = [sys.executable, '-m', 'unittest']
        if verbose:
            cmd.append('-v')
        cmd.append(test_path)
    
    try:
        result = subprocess.run(cmd, cwd='.')
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running specific test: {e}")
        return False

def show_test_info():
    """Show information about available tests."""
    print("\n📋 Available Tests")
    print("=" * 50)
    
    test_files = []
    if os.path.exists('tests/'):
        for file in Path('tests/').glob('test_*.py'):
            test_files.append(file.name)
    
    if test_files:
        print("Test files found:")
        for test_file in sorted(test_files):
            print(f"  • {test_file}")
        
        print(f"\nTotal: {len(test_files)} test files")
    else:
        print("No test files found.")
    
    print("\nTest categories:")
    print("  • Unit tests: Core AIClient functionality")
    print("  • Integration tests: CLI and workflow testing")
    print("  • Pytest tests: Modern test framework features")
    print("  • Unittest tests: Standard library testing")

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description='Run SQLite-AI chatbot tutorial tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                     # Run all tests
  python run_tests.py --verbose           # Verbose output
  python run_tests.py --coverage          # With coverage report
  python run_tests.py --fast              # Skip slow tests
  python run_tests.py --pytest-only       # Only pytest tests
  python run_tests.py --test test_ai_client.py  # Specific test file
        """
    )
    
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Run tests with verbose output')
    parser.add_argument('--coverage', '-c', action='store_true',
                        help='Run tests with coverage report (pytest only)')
    parser.add_argument('--fast', action='store_true',
                        help='Skip slow-running tests')
    parser.add_argument('--integration', action='store_true',
                        help='Run integration tests only')
    parser.add_argument('--unittest-only', action='store_true',
                        help='Run only unittest tests')
    parser.add_argument('--pytest-only', action='store_true',
                        help='Run only pytest tests')
    parser.add_argument('--test', metavar='TEST_PATH',
                        help='Run a specific test file or method')
    parser.add_argument('--info', action='store_true',
                        help='Show information about available tests')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("🤖 SQLite-AI Chatbot Test Runner")
        print("=" * 50)
    
    if args.info:
        show_test_info()
        return
    
    # Check environment and dependencies
    if not check_environment():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Handle specific test
    if args.test:
        success = run_specific_test(args.test, args.verbose)
        if success:
            if not args.quiet:
                print("\n🎉 Test passed!")
        else:
            if not args.quiet:
                print("\n💥 Test failed!")
        sys.exit(0 if success else 1)
    
    # Run tests based on arguments
    success = True
    
    if args.unittest_only:
        success = run_unittest_tests(args.verbose)
    elif args.pytest_only:
        success = run_pytest_tests(args.verbose, args.coverage, args.fast, args.integration)
    else:
        # Run both by default
        if not args.quiet:
            print("Running both unittest and pytest suites...")
        
        success1 = run_unittest_tests(args.verbose)
        success2 = run_pytest_tests(args.verbose, args.coverage, args.fast, args.integration)
        success = success1 and success2
    
    # Final results
    if not args.quiet:
        print("\n" + "=" * 50)
        if success:
            print("🎉 All tests passed!")
            print("🚀 Your chatbot implementation is working correctly!")
        else:
            print("💥 Some tests failed!")
            print("🔧 Check the output above for details on what needs fixing.")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()