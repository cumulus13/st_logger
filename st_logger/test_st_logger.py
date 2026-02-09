"""
ST Logger Test Suite
Run these tests to verify plugin functionality
"""

import sys
import time
import logging
import traceback


def test_console_output():
    """Test basic console output capture"""
    print("=" * 70)
    print("TEST 1: Basic Console Output")
    print("=" * 70)
    print("This is a regular print statement")
    print("This should be captured by ST Logger")
    print()


def test_severity_levels():
    """Test different severity levels"""
    print("=" * 70)
    print("TEST 2: Severity Level Detection")
    print("=" * 70)
    
    # DEBUG level
    print("DEBUG: This is a debug message")
    
    # INFO level
    print("INFO: This is an informational message")
    
    # WARNING level
    print("WARNING: This is a warning message")
    print("WARN: This is also a warning")
    
    # ERROR level
    print("ERROR: This is an error message")
    print("Exception occurred in module xyz")
    
    # CRITICAL level
    print("CRITICAL: System failure detected")
    print("FATAL: Critical system error")
    print()


def test_multiline_output():
    """Test multiline log messages"""
    print("=" * 70)
    print("TEST 3: Multiline Output")
    print("=" * 70)
    
    multiline = """
    This is a multiline
    log message that spans
    multiple lines
    """
    print(multiline)
    print()


def test_exception_handling():
    """Test exception and traceback logging"""
    print("=" * 70)
    print("TEST 4: Exception Handling")
    print("=" * 70)
    
    try:
        # Intentionally cause an error
        result = 1 / 0
    except Exception as e:
        print("ERROR: Caught exception: {}".format(e))
        print("Traceback:")
        traceback.print_exc()
    print()


def test_stderr_output():
    """Test stderr output capture"""
    print("=" * 70)
    print("TEST 5: STDERR Output")
    print("=" * 70)
    
    sys.stderr.write("This is written to stderr\n")
    sys.stderr.write("ERROR: This error goes to stderr\n")
    sys.stderr.flush()
    print()


def test_rapid_logging():
    """Test rapid consecutive log messages"""
    print("=" * 70)
    print("TEST 6: Rapid Logging")
    print("=" * 70)
    
    print("Generating 100 rapid log messages...")
    for i in range(100):
        print("Message {}: Rapid test message".format(i+1))
        if i % 25 == 0:
            time.sleep(0.1)  # Brief pause every 25 messages
    print("Rapid logging test complete")
    print()


def test_unicode_characters():
    """Test Unicode and special characters"""
    print("=" * 70)
    print("TEST 7: Unicode Characters")
    print("=" * 70)
    
    print("Testing Unicode: 你好世界 🌍 🚀 ★ ♠ ♥ ♦ ♣")
    print("Special chars: @#$%^&*()_+-=[]{}|;':\",./<>?")
    print("Accented: café, naïve, résumé, Zürich")
    print()


def test_long_messages():
    """Test very long log messages"""
    print("=" * 70)
    print("TEST 8: Long Messages")
    print("=" * 70)
    
    long_message = "x" * 1000
    print("Long message ({} chars): {}".format(len(long_message), long_message))
    print()


def test_structured_data():
    """Test structured data logging"""
    print("=" * 70)
    print("TEST 9: Structured Data")
    print("=" * 70)
    
    data = {
        "user": "john_doe",
        "action": "login",
        "timestamp": "2025-02-07T10:30:00Z",
        "ip": "192.168.1.100",
        "status": "success"
    }
    print("JSON-like data: {}".format(data))
    
    print("Key-value pairs: user=admin action=create_file status=success")
    print()


def test_performance_timing():
    """Test timing of log operations"""
    print("=" * 70)
    print("TEST 10: Performance Timing")
    print("=" * 70)
    
    start = time.time()
    for i in range(1000):
        print("Performance test message {}".format(i))
    elapsed = time.time() - start
    
    print("\nPerformance: 1000 messages in {:.3f} seconds".format(elapsed))
    print("Rate: {:.0f} messages/second".format(1000/elapsed))
    print()


def test_exclusion_filtering():
    """Test message exclusion with wildcards, patterns, and regex"""
    print("=" * 70)
    print("TEST 11: Message Exclusion Filtering")
    print("=" * 70)
    
    print("NOTE: Configure exclusions in settings to test:")
    print('  "exclude_wildcards": ["reloading plugin *", "*.pyc"]')
    print('  "exclude_patterns": ["node_modules", "vendor"]')
    print('  "exclude_regex": ["^Skipped \\\\d+ files$"]')
    print()
    
    # Messages that SHOULD be excluded (if configured)
    print("Messages that SHOULD be excluded:")
    print("  reloading plugin st_logger")
    print("  compiled file.pyc generated")
    print("  path/node_modules/package.json")
    print("  vendor/library/file.js")
    print("  Skipped 10 files")
    print()
    
    # Messages that should NOT be excluded
    print("Messages that should NOT be excluded:")
    print("  ERROR: Failed to load module")
    print("  WARNING: Memory usage high")
    print("  INFO: Server started successfully")
    print()


def run_all_tests():
    """Run all test cases"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  ST LOGGER - COMPREHENSIVE TEST SUITE".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")
    
    print("Starting tests...")
    print("Check your log files and syslog server for output")
    print()
    
    test_console_output()
    time.sleep(0.5)
    
    test_severity_levels()
    time.sleep(0.5)
    
    test_multiline_output()
    time.sleep(0.5)
    
    test_exception_handling()
    time.sleep(0.5)
    
    test_stderr_output()
    time.sleep(0.5)
    
    test_rapid_logging()
    time.sleep(0.5)
    
    test_unicode_characters()
    time.sleep(0.5)
    
    test_long_messages()
    time.sleep(0.5)
    
    test_structured_data()
    time.sleep(0.5)
    
    test_performance_timing()
    time.sleep(0.5)
    
    test_exclusion_filtering()
    
    print("=" * 70)
    print("ALL TESTS COMPLETE")
    print("=" * 70)
    print("\nPlease verify:")
    print("1. Log files created in configured directory")
    print("2. Messages forwarded to syslog server (if enabled)")
    print("3. Correct severity levels assigned")
    print("4. All message types captured properly")
    print("5. Excluded messages NOT in logs (if configured)")
    print()


# Run tests when executed in Sublime Text console
if __name__ == "__main__":
    run_all_tests()
else:
    # When imported, make function available
    print("ST Logger Tests loaded. Run: test_st_logger.run_all_tests()")
