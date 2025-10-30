# Frontend Tests - Session Management System

## Overview

This directory contains comprehensive unit tests for the Session Management System frontend React components.

## Test Structure

```
tests/frontend/
├── jest.config.json          # Jest configuration
├── setupTests.js            # Test setup and global mocks
├── package.json             # Testing dependencies
├── Sessions.test.js         # Tests for main Sessions component
├── CreateSession.test.js    # Tests for CreateSession modal
└── mocks/
    └── i18nMock.js         # i18n mock for translations
```

## Test Coverage

### 1. Sessions Component Tests (`Sessions.test.js`)
Tests the main sessions list page with full authorization logic.

**Test Suites:**
- ✅ **Rendering**: Loading states, empty states, session lists
- ✅ **Create Session Button**: Visibility based on user role and context
- ✅ **API Calls**: Correct endpoints for different user types
- ✅ **Error Handling**: 401, 403, 404, network errors
- ✅ **Session Actions**: Start, Continue, View, Delete buttons
- ✅ **Session Display**: Correct information display

**Key Test Cases (35 tests):**
- Renders loading state initially
- Shows sessions list for doctor with patient selected
- Shows my sessions for patient
- Shows empty state when no sessions
- Shows select patient message for doctor without patient
- Create button only for doctor with patient selected
- Calls `/api/sessions/patient/{id}` for doctor
- Calls `/api/sessions/my-sessions` for patient
- Shows appropriate error messages (403, 401, 404)
- Displays Start button for pending sessions (patient)
- Displays Continue button for in_progress sessions (patient)
- Displays View and Delete buttons (doctor)
- Displays session details correctly (mode, status, time)

### 2. CreateSession Component Tests (`CreateSession.test.js`)
Tests the session creation modal functionality.

**Test Suites:**
- ✅ **Rendering**: Form fields, patient selector visibility
- ✅ **Form Validation**: Required fields, min/max values
- ✅ **Form Submission**: Success and error scenarios
- ✅ **Mode Selection**: All three modes supported
- ✅ **Cancel Button**: Closes modal correctly

**Key Test Cases (20 tests):**
- Renders create session form
- Shows patient selector when no patientId
- Hides patient selector when patientId provided
- Validates required patient selection
- Validates required mode selection
- Validates min interruption time (1 second)
- Validates max interruption time (300 seconds)
- Submits form with valid data
- Handles 403 error (no access to patient)
- Handles generic submission errors
- Handles network errors
- Allows selecting all three modes
- Calls onClose when cancel clicked

## Running Tests

### Prerequisites

1. Navigate to the tests/frontend directory:
```bash
cd /home/vinibalvarenga/ArtEvoke/webapp/tests/frontend
```

2. Install test dependencies:
```bash
npm install
```

### Run Tests

```bash
# Run all tests
npm test

# Run tests in watch mode (re-runs on file changes)
npm run test:watch

# Run with coverage report
npm run test:coverage

# Run with verbose output
npm run test:verbose

# Run specific test file
npm test Sessions.test.js

# Run tests matching pattern
npm test -- --testNamePattern="Create Session Button"
```

### Test Output

```
PASS  tests/frontend/Sessions.test.js
  Sessions Component
    Rendering
      ✓ renders loading state initially (45ms)
      ✓ renders sessions list for doctor with patient selected (32ms)
      ✓ renders my sessions for patient (28ms)
    Create Session Button
      ✓ shows create button for doctor with patient selected (25ms)
      ✓ does not show create button for patient (20ms)
    ...

Test Suites: 2 passed, 2 total
Tests:       55 passed, 55 total
Snapshots:   0 total
Time:        3.245 s
```

### Coverage Report

After running `npm run test:coverage`, open `coverage/index.html` in a browser to view detailed coverage:

```
File                    | % Stmts | % Branch | % Funcs | % Lines |
------------------------|---------|----------|---------|---------|
Sessions/Sessions.js    |   92.5  |   88.3   |   95.0  |   93.2  |
Sessions/CreateSession.js |  90.8  |   85.7   |   92.3  |   91.5  |
------------------------|---------|----------|---------|---------|
All files               |   91.7  |   87.0   |   93.7  |   92.4  |
```

## Mocks and Setup

### Global Mocks (`setupTests.js`)
- `window.matchMedia`: For responsive design tests
- `localStorage`: For token storage tests
- `fetch`: For API call tests

### i18n Mock (`mocks/i18nMock.js`)
Provides Portuguese translations for:
- Session list labels
- Button text
- Error messages
- Validation messages
- Status and mode names

## Writing New Tests

### Test Structure (AAA Pattern)

```javascript
test('descriptive test name', async () => {
  // Arrange - Setup
  const mockData = { ... };
  fetch.mockResolvedValueOnce({ ok: true, json: async () => mockData });

  // Act - Execute
  renderWithProviders(<Component />);
  const button = screen.getByText(/button text/i);
  fireEvent.click(button);

  // Assert - Verify
  await waitFor(() => {
    expect(fetch).toHaveBeenCalledWith(...);
    expect(screen.getByText(/expected text/i)).toBeInTheDocument();
  });
});
```

### Best Practices

1. **Use `waitFor` for async operations**
   ```javascript
   await waitFor(() => {
     expect(screen.getByText(/text/i)).toBeInTheDocument();
   });
   ```

2. **Query by accessibility**
   ```javascript
   screen.getByLabelText(/label text/i)  // Best
   screen.getByRole('button', { name: /button/i })  // Good
   screen.getByTestId('test-id')  // Last resort
   ```

3. **Mock fetch responses**
   ```javascript
   fetch.mockResolvedValueOnce({
     ok: true,
     status: 200,
     json: async () => mockData
   });
   ```

4. **Clean up after each test**
   ```javascript
   beforeEach(() => {
     fetch.mockClear();
     mockFunction.mockClear();
   });
   ```

## Troubleshooting

### Import Errors
If you get module resolution errors:
```bash
# Ensure dependencies are installed
npm install

# Clear Jest cache
npx jest --clearCache
```

### Mock Not Working
If mocks aren't applied:
```javascript
// Check that mock is cleared in beforeEach
beforeEach(() => {
  jest.clearAllMocks();
});
```

### Async Test Timeout
If async tests timeout:
```javascript
// Increase timeout for specific test
test('slow test', async () => {
  // test code
}, 10000); // 10 seconds
```

### Coverage Thresholds
If coverage doesn't meet thresholds, check:
- `jest.config.json` → `coverageThreshold`
- Run with `--coverage` to see which lines are missed

## Integration with CI/CD

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Frontend Tests
  run: |
    cd webapp/tests/frontend
    npm install
    npm run test:coverage
```

## Coverage Goals

- **Statements**: > 90%
- **Branches**: > 85%
- **Functions**: > 90%
- **Lines**: > 90%

## Common Assertions

```javascript
// Element presence
expect(screen.getByText(/text/i)).toBeInTheDocument();
expect(screen.queryByText(/text/i)).not.toBeInTheDocument();

// Element visibility
expect(element).toBeVisible();

// Form values
expect(input.value).toBe('expected value');

// Function calls
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith(expectedArg);
expect(mockFn).toHaveBeenCalledTimes(2);

// API calls
expect(fetch).toHaveBeenCalledWith(
  '/api/endpoint',
  expect.objectContaining({
    method: 'POST',
    headers: expect.objectContaining({
      'Authorization': 'Bearer token'
    })
  })
);
```

## Resources

- [React Testing Library Docs](https://testing-library.com/react)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Testing Library Queries](https://testing-library.com/docs/queries/about)
