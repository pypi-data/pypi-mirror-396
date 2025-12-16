"""
Basic tests for Python Semantic Splitter.
"""
import tempfile
import os
from python_semantic_splitter import PythonSplitter, SplitterConfig


def test_basic_splitting():
    """Test basic splitting functionality."""
    # Sample Python code
    sample_code = '''"""
Sample module for testing.
"""
import os
import sys

DEBUG = True

def hello_world():
    """A simple greeting function."""
    return "Hello, World!"

class Greeter:
    """A simple greeter class."""
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        """Return a greeting."""
        return f"Hello, {self.name}!"

def main():
    """Main function."""
    greeter = Greeter("World")
    print(greeter.greet())

if __name__ == "__main__":
    main()
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(sample_code)
        temp_path = f.name
    
    try:
        # Test splitting
        splitter = PythonSplitter()
        chunks = splitter.split_file(temp_path)
        
        # Basic assertions
        assert len(chunks) > 0, "Should create at least one chunk"
        
        # Check chunk types
        chunk_types = [chunk.chunk_type for chunk in chunks]
        assert 'module' in chunk_types, "Should have module chunk"
        assert 'function' in chunk_types, "Should have function chunks"
        assert 'class' in chunk_types, "Should have class chunk"
        
        # Check that we have the expected functions
        function_chunks = [c for c in chunks if c.chunk_type == 'function']
        function_names = [c.metadata['function_name'] for c in function_chunks]
        assert 'hello_world' in function_names, "Should find hello_world function"
        assert 'main' in function_names, "Should find main function"
        
        # Check class
        class_chunks = [c for c in chunks if c.chunk_type == 'class']
        assert len(class_chunks) == 1, "Should have exactly one class"
        assert class_chunks[0].metadata['class_name'] == 'Greeter', "Should find Greeter class"
        
        print("✅ Basic splitting test passed!")
        return True
        
    finally:
        # Clean up
        os.unlink(temp_path)


def test_configuration():
    """Test configuration options."""
    sample_code = '''
def func1():
    """Function 1."""
    pass

def func2():
    pass
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(sample_code)
        temp_path = f.name
    
    try:
        # Test with docstrings disabled
        config = SplitterConfig(include_docstrings=False)
        splitter = PythonSplitter(config)
        chunks = splitter.split_file(temp_path)
        
        # Check that docstrings are not included
        for chunk in chunks:
            if chunk.chunk_type == 'function':
                assert chunk.metadata.get('docstring') is None, "Docstrings should be disabled"
        
        print("✅ Configuration test passed!")
        return True
        
    finally:
        os.unlink(temp_path)


def test_text_splitting():
    """Test splitting text directly."""
    code = '''
def test_function():
    """Test function."""
    return "test"
'''
    
    splitter = PythonSplitter()
    chunks = splitter.split_text(code, file_name="test.py")
    
    assert len(chunks) > 0, "Should create chunks from text"
    
    # Check that file_path is updated
    for chunk in chunks:
        assert chunk.metadata['file_path'] == "test.py", "Should use provided file name"
    
    print("✅ Text splitting test passed!")
    return True


def test_stats():
    """Test statistics functionality."""
    sample_code = '''
def func1():
    pass

def func2():
    pass

class TestClass:
    def method1(self):
        pass
'''
    
    splitter = PythonSplitter()
    chunks = splitter.split_text(sample_code)
    stats = splitter.get_stats(chunks)
    
    assert stats['total_chunks'] > 0, "Should have chunks"
    assert 'function' in stats['chunk_types'], "Should have function chunks"
    assert 'class' in stats['chunk_types'], "Should have class chunks"
    assert stats['total_characters'] > 0, "Should count characters"
    
    print("✅ Stats test passed!")
    return True


if __name__ == "__main__":
    print("Running Python Semantic Splitter tests...")
    print("=" * 50)
    
    tests = [
        test_basic_splitting,
        test_configuration,
        test_text_splitting,
        test_stats,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with error: {e}")
    
    print("=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
        exit(1)
