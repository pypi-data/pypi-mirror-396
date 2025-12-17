"""
Simple test script to validate CodexCollector functionality.
"""

from codexcollector import CodexCollector, IngestionError, ConfigurationError


def test_initialization():
    """Test that CodexCollector initializes correctly."""
    print("Testing initialization...")

    # Test default initialization
    collector = CodexCollector()
    assert collector.max_file_size_mb == 100
    assert collector.request_delay == 1.0
    assert collector.timeout == 30
    assert collector.max_crawl_depth == 2
    assert collector.default_encoding == 'utf-8'
    assert collector.max_collection_time == 0
    print("[OK]Default initialization successful")

    # Test custom initialization
    collector = CodexCollector(
        max_file_size_mb=50,
        request_delay=2.0,
        timeout=60,
        max_crawl_depth=3,
        default_encoding='latin-1',
        max_collection_time=300
    )
    assert collector.max_file_size_mb == 50
    assert collector.request_delay == 2.0
    assert collector.timeout == 60
    assert collector.max_crawl_depth == 3
    assert collector.default_encoding == 'latin-1'
    assert collector.max_collection_time == 300
    print("[OK]Custom initialization successful")


def test_configuration_validation():
    """Test that invalid configurations raise errors."""
    print("\nTesting configuration validation...")

    # Test invalid max_file_size_mb
    try:
        CodexCollector(max_file_size_mb=-1)
        assert False, "Should have raised ConfigurationError"
    except ConfigurationError:
        print("[OK]Negative max_file_size_mb rejected")

    # Test invalid timeout
    try:
        CodexCollector(timeout=0)
        assert False, "Should have raised ConfigurationError"
    except ConfigurationError:
        print("[OK]Zero timeout rejected")

    # Test invalid max_crawl_depth
    try:
        CodexCollector(max_crawl_depth=-1)
        assert False, "Should have raised ConfigurationError"
    except ConfigurationError:
        print("[OK]Negative max_crawl_depth rejected")

    # Test invalid default_encoding
    try:
        CodexCollector(default_encoding='')
        assert False, "Should have raised ConfigurationError"
    except ConfigurationError:
        print("[OK]Empty default_encoding rejected")


def test_url_detection():
    """Test URL detection logic."""
    print("\nTesting URL detection...")

    collector = CodexCollector()

    # Test URLs
    assert collector._is_url('https://example.com') == True
    assert collector._is_url('http://example.com') == True
    assert collector._is_url('www.example.com') == True
    print("[OK]URLs detected correctly")

    # Test file paths
    assert collector._is_url('/path/to/file') == False
    assert collector._is_url('C:\\Users\\path') == False
    assert collector._is_url('relative/path') == False
    print("[OK]File paths detected correctly")


def test_filename_extraction():
    """Test URL filename extraction."""
    print("\nTesting filename extraction...")

    collector = CodexCollector()

    # Test basic URL
    assert collector._extract_filename_from_url('https://example.com/doc.pdf') == 'doc.pdf'
    print("[OK]Basic filename extraction")

    # Test URL with query string
    assert collector._extract_filename_from_url('https://example.com/doc.pdf?v=1') == 'doc.pdf'
    print("[OK]Filename extraction with query string")

    # Test URL with fragment
    assert collector._extract_filename_from_url('https://example.com/doc.pdf#page=2') == 'doc.pdf'
    print("[OK]Filename extraction with fragment")

    # Test URL with no filename
    assert collector._extract_filename_from_url('https://example.com/') == 'unknown'
    print("[OK]Unknown for URL with no filename")


def test_timeout_check():
    """Test collection timeout checking."""
    print("\nTesting timeout checking...")

    import time

    # Test with no timeout
    collector = CodexCollector(max_collection_time=0)
    start = time.time()
    assert collector._check_collection_timeout(start) == False
    print("[OK]No timeout when max_collection_time=0")

    # Test with timeout not exceeded
    collector = CodexCollector(max_collection_time=10)
    start = time.time()
    assert collector._check_collection_timeout(start) == False
    print("[OK]Timeout not exceeded")

    # Test with timeout exceeded
    collector = CodexCollector(max_collection_time=1)
    start = time.time() - 2  # Simulate 2 seconds ago
    assert collector._check_collection_timeout(start) == True
    print("[OK]Timeout exceeded detected")


def test_type_safety():
    """Test TypedDict usage."""
    print("\nTesting type safety...")

    from codexcollector import Document, CorpusType

    # Create a document
    doc: Document = {
        'filename': 'test.pdf',
        'source': '/path/to/test.pdf',
        'text': 'Sample text',
        'date': '2024-01-01T00:00:00'
    }
    assert doc['filename'] == 'test.pdf'
    print("[OK]Document TypedDict works")

    # Create a corpus
    corpus: CorpusType = {
        0: doc
    }
    assert corpus[0]['filename'] == 'test.pdf'
    print("[OK]CorpusType works")


def main():
    """Run all tests."""
    print("=" * 60)
    print("CodexCollector Test Suite")
    print("=" * 60)

    try:
        test_initialization()
        test_configuration_validation()
        test_url_detection()
        test_filename_extraction()
        test_timeout_check()
        test_type_safety()

        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
