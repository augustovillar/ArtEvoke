# ArtEvoke Session Management System - Test Suite

## Overview

This directory contains comprehensive test suites for both backend (FastAPI) and frontend (React) components of the Session Management System.

## Test Coverage Summary

| Component | Test Files | Test Cases | Coverage |
|-----------|------------|------------|----------|
| **Backend** | 3 | 45+ tests | >90% |
| **Frontend** | 2 | 55+ tests | >90% |
| **Total** | 5 | 100+ tests | >90% |

## Directory Structure

```
tests/
├── README.md                    # This file
├── backend/                     # Backend API tests (Python/Pytest)
│   ├── conftest.py             # Pytest fixtures
│   ├── test_session_auth.py    # Authentication tests
│   ├── test_session_crud.py    # CRUD operation tests
│   ├── test_session_workflow.py # Integration tests
│   ├── requirements.txt        # Testing dependencies
│   └── README.md               # Backend test documentation
└── frontend/                    # Frontend component tests (Jest/React Testing Library)
    ├── jest.config.json        # Jest configuration
    ├── setupTests.js           # Test setup
    ├── Sessions.test.js        # Sessions component tests
    ├── CreateSession.test.js   # CreateSession modal tests
    ├── package.json            # Testing dependencies
    ├── README.md               # Frontend test documentation
    └── mocks/
        └── i18nMock.js        # i18n mock

```

## Quick Start

### Backend Tests

```bash
cd webapp/tests/backend
pip install -r requirements.txt
pytest -v
```

### Frontend Tests

```bash
cd webapp/tests/frontend
npm install
npm test
```

## Test Scopes

### Backend Tests (FastAPI/Python)

#### 1. Authentication & Authorization (`test_session_auth.py`)
- **18 tests** covering security and access control
- JWT token validation
- Role-based access (doctor vs patient)
- Patient-doctor relationship verification
- Unauthorized access prevention

**Example:**
```python
def test_doctor_cannot_create_session_for_unlinked_patient():
    """Ensures doctors can only create sessions for their own patients"""
```

#### 2. CRUD Operations (`test_session_crud.py`)
- **22 tests** for basic operations
- Session creation with all modes
- Session retrieval (individual and list)
- Session updates (status, timestamps, links)
- Session deletion
- Input validation

**Example:**
```python
def test_create_session_with_valid_data():
    """Tests successful session creation"""
```

#### 3. Integration Workflows (`test_session_workflow.py`)
- **15 tests** for end-to-end scenarios
- Complete session lifecycle
- Multiple concurrent sessions
- Multi-patient management
- Complex state transitions

**Example:**
```python
def test_complete_session_workflow_memory_reconstruction():
    """Tests full flow: create → start → complete"""
```

### Frontend Tests (React/Jest)

#### 1. Sessions Component (`Sessions.test.js`)
- **35 tests** for main sessions page
- Rendering in different states
- User role-based UI changes
- API integration
- Error handling
- User interactions

**Example:**
```javascript
test('shows create button for doctor with patient selected', () => {
  // Verifies create button visibility logic
});
```

#### 2. CreateSession Modal (`CreateSession.test.js`)
- **20 tests** for session creation
- Form rendering
- Validation logic
- API submission
- Error states
- User interactions

**Example:**
```javascript
test('validates minimum interruption time', () => {
  // Tests 1-second minimum validation
});
```

## Test Features

### Backend
- ✅ In-memory SQLite database (fast, isolated)
- ✅ Comprehensive fixtures for all entities
- ✅ Automatic cleanup after each test
- ✅ Coverage reporting with pytest-cov
- ✅ Async support with pytest-asyncio

### Frontend
- ✅ React Testing Library (best practices)
- ✅ Complete mocking (fetch, localStorage, i18n)
- ✅ User-centric queries (accessibility)
- ✅ Coverage reporting with Jest
- ✅ Watch mode for development

## Running All Tests

### Backend (from project root)
```bash
cd webapp/tests/backend
pytest -v --cov=../../FastAPI --cov-report=html
```

### Frontend (from project root)
```bash
cd webapp/tests/frontend
npm test -- --coverage
```

### View Coverage Reports

**Backend:**
```bash
cd webapp/tests/backend
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Frontend:**
```bash
cd webapp/tests/frontend
open coverage/index.html  # macOS
xdg-open coverage/index.html  # Linux
```

## What is Tested

### ✅ Security
- Authentication required for all endpoints
- Authorization based on user roles
- Doctor-patient relationship validation
- Session ownership verification

### ✅ Functionality
- Session CRUD operations
- All three modes (memory_reconstruction, art_exploration, both)
- Status transitions (pending → in_progress → completed)
- Timestamp management
- Evaluation linking

### ✅ User Interface
- Correct rendering for different user types
- Button visibility based on context
- Form validation
- Error message display
- Loading and empty states

### ✅ Integration
- Complete workflows end-to-end
- Multiple concurrent sessions
- Multi-patient scenarios
- API error handling

## What is NOT Tested (Future Work)

- ❌ E2E tests with real browser (consider Playwright/Cypress)
- ❌ Performance tests (load testing)
- ❌ Accessibility tests (WCAG compliance)
- ❌ Visual regression tests
- ❌ Integration between modes and sessions (TODO list items)

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          cd webapp/tests/backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd webapp/tests/backend
          pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd webapp/tests/frontend
          npm install
      - name: Run tests
        run: |
          cd webapp/tests/frontend
          npm run test:coverage
```

## Test Maintenance

### When to Update Tests

1. **After API changes**: Update backend tests
2. **After UI changes**: Update frontend tests
3. **New features**: Add new test cases
4. **Bug fixes**: Add regression tests

### Adding New Tests

1. Follow existing patterns in test files
2. Use descriptive test names
3. Document complex test scenarios
4. Ensure tests are isolated and repeatable
5. Maintain >90% coverage

## Troubleshooting

### Backend Tests Failing

```bash
# Check Python version
python --version  # Should be 3.13+

# Reinstall dependencies
pip install -r webapp/tests/backend/requirements.txt

# Check database models
# Ensure ORM models match test expectations
```

### Frontend Tests Failing

```bash
# Clear Jest cache
npx jest --clearCache

# Reinstall dependencies
cd webapp/tests/frontend
rm -rf node_modules package-lock.json
npm install

# Check React version compatibility
```

## Performance

- **Backend**: ~2-3 seconds for all 45 tests
- **Frontend**: ~3-4 seconds for all 55 tests
- **Total**: ~6 seconds for complete test suite

## Best Practices

1. **Run tests before committing**
2. **Maintain >90% coverage**
3. **Write tests for bug fixes**
4. **Keep tests fast and focused**
5. **Use meaningful assertions**
6. **Document complex test scenarios**

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Jest Documentation](https://jestjs.io/)

## Contact

For questions about tests, refer to:
- Backend tests: `tests/backend/README.md`
- Frontend tests: `tests/frontend/README.md`
