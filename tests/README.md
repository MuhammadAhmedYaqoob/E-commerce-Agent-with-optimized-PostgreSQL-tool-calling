# Unit Tests for E-Commerce MiniRAG System

## Overview

This directory contains comprehensive unit tests for the E-Commerce MiniRAG Agentic System. All tests are designed to run **without requiring API keys or external services**.

## Test Structure

```
tests/
├── __init__.py
├── test_config.py              # Configuration tests
├── test_generator.py            # Answer generator tests
├── test_minirag_graph_builder.py    # Graph builder tests
├── test_minirag_graph_retriever.py  # Graph retriever tests
├── test_tools_gmail.py          # Gmail tool tests
├── test_tools_supabase.py       # Supabase tool tests
├── run_tests.py                 # Test runner
└── README.md                    # This file
```

## Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test Module
```bash
python -m unittest tests.test_config
python -m unittest tests.test_generator
python -m unittest tests.test_minirag_graph_builder
python -m unittest tests.test_minirag_graph_retriever
python -m unittest tests.test_tools_gmail
python -m unittest tests.test_tools_supabase
```

### Run with Verbose Output
```bash
python -m unittest discover tests -v
```

## Test Coverage

### Configuration Tests (`test_config.py`)
- ✅ Knowledge base path validation
- ✅ Graph directory configuration
- ✅ Retrieval parameters
- ✅ MiniRAG settings (semantic fallback disabled)

### Generator Tests (`test_generator.py`)
- ✅ Answer generation with contexts
- ✅ Error handling for empty contexts
- ✅ API error handling

### Graph Builder Tests (`test_minirag_graph_builder.py`)
- ✅ Graph initialization
- ✅ Knowledge base loading (success/failure)
- ✅ Graph building with valid/invalid data
- ✅ Entity node resolution
- ✅ Keyword extraction
- ✅ Similarity calculation

### Graph Retriever Tests (`test_minirag_graph_retriever.py`)
- ✅ Retriever initialization
- ✅ Query entity extraction
- ✅ Node matching
- ✅ Graph traversal
- ✅ Node scoring
- ✅ Content extraction

### Gmail Tool Tests (`test_tools_gmail.py`)
- ✅ Tool initialization
- ✅ Verification code generation
- ✅ Email sending (mocked)
- ✅ 2FA code sending and verification
- ✅ Expired code handling
- ✅ Notification sending
- ✅ Code cleanup

### Supabase Tool Tests (`test_tools_supabase.py`)
- ✅ Tool initialization
- ✅ Mock mode operations
- ✅ User operations
- ✅ Order operations
- ✅ Graph entity caching

## Test Design Principles

1. **No External Dependencies**: All tests use mocks and don't require API keys
2. **Isolated**: Each test is independent and can run in any order
3. **Comprehensive**: Tests cover success cases, error cases, and edge cases
4. **Fast**: Tests run quickly without network calls
5. **Maintainable**: Clear test names and structure

## Mock Strategy

- **Gmail Tool**: SMTP operations mocked
- **Supabase Tool**: Database operations use mock mode
- **OpenAI API**: API calls mocked in generator tests
- **File Operations**: File I/O mocked where necessary

## Adding New Tests

When adding new functionality:

1. Create test file: `tests/test_<module_name>.py`
2. Follow naming convention: `test_<function_name>`
3. Use setUp() for common fixtures
4. Mock external dependencies
5. Test both success and failure cases
6. Add to `run_tests.py` if creating new module

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- No external dependencies required
- Fast execution
- Clear pass/fail indicators
- Exit codes for automation

## Coverage Goals

- **Unit Tests**: 80%+ code coverage
- **Critical Paths**: 100% coverage
- **Error Handling**: All error paths tested
- **Edge Cases**: Boundary conditions tested

## Notes

- Tests use `unittest.mock` for mocking
- No actual API calls are made
- All tests can run offline
- Mock data is used for database operations
- File operations are mocked where needed

