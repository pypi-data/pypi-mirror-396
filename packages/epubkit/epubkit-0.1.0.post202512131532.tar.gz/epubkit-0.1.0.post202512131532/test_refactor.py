#!/usr/bin/env python3
"""
Simple validation script for epubkit refactoring.
Tests basic imports and interface compatibility.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")

    try:
        # Test CFI module
        from epubkit import cfi
        print("✓ CFI module imported")

        # Test epub submodules
        from epubkit.epub import path_resolver, opf_parser, metadata_parser
        from epubkit.epub import toc_parser, toc_builder
        print("✓ All epub submodules imported")

        # Test interfaces
        from epubkit.interfaces import ContentReader
        print("✓ Interfaces imported")

        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_interface_definition():
    """Test that ContentReader interface is properly defined."""
    print("\nTesting ContentReader interface...")

    try:
        from epubkit.interfaces import ContentReader
        import inspect

        # Check required abstract methods
        methods = [name for name, obj in inspect.getmembers(ContentReader)
                  if inspect.ismethod(obj) or isinstance(obj, property)]

        required_methods = [
            'read_chapter',  # Abstract method
            'zf',           # Property
            'opf_path',     # Property
            'epub_path',    # Property
            'zip_namelist', # Property
            'trace'         # Property
        ]

        for method in required_methods:
            if not hasattr(ContentReader, method):
                print(f"❌ Missing required interface member: {method}")
                return False

        print("✓ ContentReader interface properly defined")
        return True

    except Exception as e:
        print(f"❌ Interface test failed: {e}")
        return False

def test_refactored_functions():
    """Test that refactored functions accept ContentReader parameter."""
    print("\nTesting refactored function signatures...")

    try:
        from epubkit.epub.toc_parser import parse_nav_document_robust, parse_ncx_document_robust
        from epubkit.epub.toc_builder import TOCBuilder
        from epubkit.interfaces import ContentReader
        import inspect

        # Check toc_parser functions
        nav_sig = inspect.signature(parse_nav_document_robust)
        if 'reader' not in nav_sig.parameters:
            print("❌ parse_nav_document_robust missing 'reader' parameter")
            return False

        reader_param = nav_sig.parameters['reader']
        annotation = reader_param.annotation
        if annotation != ContentReader and str(annotation).find('ContentReader') == -1:
            print(f"❌ parse_nav_document_robust 'reader' parameter type: {annotation}")
            return False

        ncx_sig = inspect.signature(parse_ncx_document_robust)
        if 'reader' not in ncx_sig.parameters:
            print("❌ parse_ncx_document_robust missing 'reader' parameter")
            return False

        # Check TOCBuilder constructor
        builder_init = TOCBuilder.__init__
        init_sig = inspect.signature(builder_init)
        if 'reader' not in init_sig.parameters:
            print("❌ TOCBuilder.__init__ missing 'reader' parameter")
            return False

        reader_param = init_sig.parameters['reader']
        annotation = reader_param.annotation
        if annotation != ContentReader and str(annotation).find('ContentReader') == -1:
            print(f"❌ TOCBuilder.__init__ 'reader' parameter type: {annotation}")
            return False

        print("✓ Refactored functions accept ContentReader parameters")
        return True

    except Exception as e:
        print(f"❌ Function signature test failed: {e}")
        return False

def test_cfi_compatibility():
    """Test that CFI module works independently."""
    print("\nTesting CFI module compatibility...")

    try:
        from epubkit import cfi

        # Test basic CFI parsing
        test_cfi = "epubcfi(/6/4[chap01]/10:5)"
        parsed = cfi.CFI.parse(test_cfi)
        if not parsed:
            print("❌ CFI parsing failed")
            return False

        # Test CFI generation
        generated = cfi.CFI.to_string(parsed)
        if not generated:
            print("❌ CFI generation failed")
            return False

        print("✓ CFI module works independently")
        return True

    except Exception as e:
        print(f"❌ CFI test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🔍 Validating epubkit refactoring (Phase 1)")
    print("=" * 50)

    tests = [
        test_imports,
        test_interface_definition,
        test_refactored_functions,
        test_cfi_compatibility,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            break

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All validation tests passed! Phase 1 refactoring is successful.")
        return 0
    else:
        print("❌ Some tests failed. Please check the refactoring.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
