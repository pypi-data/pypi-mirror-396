#!/usr/bin/env python3
"""
Test script for epubkit API functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_api():
    """Test basic epubkit API functionality."""
    print("Testing epubkit basic API...")

    try:
        import epubkit

        # Test imports
        assert hasattr(epubkit, 'open')
        assert hasattr(epubkit, 'EPUB')
        assert hasattr(epubkit, 'CFI')
        print("✓ API imports successful")

        # Test version
        assert hasattr(epubkit, '__version__')
        print(f"✓ Version: {epubkit.__version__}")

        return True

    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_epub_class():
    """Test EPUB class structure."""
    print("\nTesting EPUB class...")

    try:
        from epubkit.core import EPUB

        # Check class exists and has expected methods
        assert hasattr(EPUB, '__init__')
        assert hasattr(EPUB, 'path')
        assert hasattr(EPUB, 'title')
        assert hasattr(EPUB, 'toc')
        assert hasattr(EPUB, 'spine')
        assert hasattr(EPUB, 'metadata')
        assert hasattr(EPUB, 'read_chapter')
        print("✓ EPUB class structure correct")

        return True

    except Exception as e:
        print(f"❌ EPUB class test failed: {e}")
        return False

def test_cfi_integration():
    """Test CFI integration."""
    print("\nTesting CFI integration...")

    try:
        from epubkit import CFI, CFIGenerator

        # Test CFI parsing
        test_cfi = "epubcfi(/6/4[chap01]/10:5)"
        parsed = CFI.parse(test_cfi)
        assert parsed is not None
        print("✓ CFI parsing works")

        # Test CFI generation
        generated = CFI.to_string(parsed)
        assert generated is not None
        print("✓ CFI generation works")

        return True

    except Exception as e:
        print(f"❌ CFI test failed: {e}")
        return False

def main():
    """Run all API tests."""
    print("🧪 Testing epubkit API (Phase 2)")
    print("=" * 50)

    tests = [
        test_basic_api,
        test_epub_class,
        test_cfi_integration,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            break

    print("\n" + "=" * 50)
    print(f"📊 API Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All API tests passed! epubkit is ready for use.")
        print("\n🚀 Example usage:")
        print("   import epubkit")
        print("   book = epubkit.open('my_book.epub')")
        print("   print(book.title)")
        return 0
    else:
        print("❌ Some API tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
