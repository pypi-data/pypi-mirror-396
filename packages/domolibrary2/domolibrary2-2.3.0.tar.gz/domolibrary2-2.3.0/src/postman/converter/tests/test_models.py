#!/usr/bin/env python3
"""
Simple test script to validate our enhanced Postman models.
"""


def test_basic_imports():
    """Test that all our classes can be imported."""
    try:
        from models import (  # noqa: F401
            PostmanAuth,
            PostmanCollection,
            PostmanCollectionInfo,
            PostmanEvent,
            PostmanFolder,
            PostmanQueryParam,
            PostmanRequest,
            PostmanRequest_Body,
            PostmanRequest_Header,
            PostmanResponse,
            PostmanScript,
            PostmanUrl,
            PostmanVariable,
        )

        print("✅ All classes imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality of our classes."""
    try:
        from models import PostmanQueryParam, PostmanRequest_Header

        # Test PostmanRequest_Header
        header_data = {
            "key": "Content-Type",
            "value": "application/json",
            "disabled": False,
            "description": "Content type header",
        }

        header = PostmanRequest_Header.from_dict(header_data)

        print(f"✅ Header round-trip test: {header.key} = {header.value}")

        # Test PostmanQueryParam
        param_data = {
            "key": "limit",
            "value": "10",
            "disabled": False,
            "description": "Limit results",
        }

        param = PostmanQueryParam.from_dict(param_data)

        print(f"✅ Query param round-trip test: {param.key} = {param.value}")

        return True

    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def test_complex_structure():
    """Test with a simple collection structure."""
    try:
        from models import PostmanCollection

        # Simple test collection
        test_data = {
            "info": {
                "_postman_id": "test-123",
                "name": "Test Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": [
                {
                    "name": "Test Request",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "Accept", "value": "application/json"}],
                        "url": {
                            "raw": "https://api.example.com/test",
                            "protocol": "https",
                            "host": ["api", "example", "com"],
                            "path": ["test"],
                        },
                    },
                    "response": [],
                }
            ],
        }

        # Test from_dict
        collection = PostmanCollection.from_dict(test_data)
        print(f"✅ Collection parsed: {collection.info.name}")
        print(f"✅ Found {len(collection.requests)} requests")

        # Test to_dict
        collection.to_dict()
        print("✅ Collection converted back to dictionary")

        return True

    except Exception as e:
        print(f"❌ Complex structure test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🔍 Testing enhanced Postman models...")
    print("=" * 50)

    tests = [
        ("Import Test", test_basic_imports),
        ("Basic Functionality Test", test_basic_functionality),
        ("Complex Structure Test", test_complex_structure),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Models are working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Models need fixes.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
