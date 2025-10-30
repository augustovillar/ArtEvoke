# 📖 Guia para Adicionar Novos Testes

## Backend (Python/Pytest)

### Estrutura Básica

```python
# test_session_new_feature.py

def test_descriptive_name(client, doctor_token, create_patient, link_doctor_patient):
    """
    Clear description of what this test verifies
    
    Arrange: Setup test data
    Act: Execute the action
    Assert: Verify the result
    """
    # Arrange - Prepare test data
    session_data = {
        "patient_id": create_patient.id,
        "mode": "memory_reconstruction",
        "interruption_time": 10
    }
    
    # Act - Execute the API call
    response = client.post(
        "/api/sessions/",
        headers={"Authorization": f"Bearer {doctor_token}"},
        json=session_data
    )
    
    # Assert - Verify the result
    assert response.status_code == 201
    assert response.json()["mode"] == "memory_reconstruction"
```

### Usando Fixtures Existentes

```python
def test_with_existing_session(client, doctor_token, sample_session):
    """Use sample_session fixture for pre-created session"""
    response = client.get(
        f"/api/sessions/{sample_session.id}",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    assert response.status_code == 200
```

### Criando Nova Fixture

```python
# Em conftest.py

@pytest.fixture
def completed_session(db_session, create_doctor, create_patient, link_doctor_patient):
    """Create a completed session"""
    from orm import Session as SessionModel
    from datetime import datetime
    import uuid
    
    session = SessionModel(
        id=str(uuid.uuid4()),
        patient_id=create_patient.id,
        doctor_id=create_doctor.id,
        mode="memory_reconstruction",
        interruption_time=10,
        status="completed",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session
```

### Testando Erros

```python
def test_handles_error_gracefully(client, doctor_token):
    """Test error handling"""
    # Arrange - Invalid data
    invalid_data = {
        "patient_id": "invalid-uuid",
        "mode": "invalid_mode"
    }
    
    # Act
    response = client.post(
        "/api/sessions/",
        headers={"Authorization": f"Bearer {doctor_token}"},
        json=invalid_data
    )
    
    # Assert - Verify error response
    assert response.status_code == 404  # or 400, 422, etc.
    assert "error" in response.json()["detail"].lower()
```

### Testando Workflows Complexos

```python
def test_multi_step_workflow(
    client, doctor_token, patient_token, 
    create_patient, link_doctor_patient
):
    """Test complex multi-step workflow"""
    # Step 1: Doctor creates session
    create_response = client.post(
        "/api/sessions/",
        headers={"Authorization": f"Bearer {doctor_token}"},
        json={
            "patient_id": create_patient.id,
            "mode": "both",
            "interruption_time": 20
        }
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]
    
    # Step 2: Patient starts session
    start_response = client.patch(
        f"/api/sessions/{session_id}",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"status": "in_progress"}
    )
    assert start_response.status_code == 200
    
    # Step 3: Verify state
    get_response = client.get(
        f"/api/sessions/{session_id}",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    assert get_response.json()["status"] == "in_progress"
```

## Frontend (React/Jest)

### Estrutura Básica

```javascript
// NewComponent.test.js

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import NewComponent from '../../../frontend/src/pages/NewComponent';
import i18n from './mocks/i18nMock';

const renderWithProviders = (component) => {
  return render(
    <I18nextProvider i18n={i18n}>
      {component}
    </I18nextProvider>
  );
};

describe('NewComponent', () => {
  beforeEach(() => {
    fetch.mockClear();
    localStorage.getItem.mockReturnValue('fake-token');
  });

  test('renders component correctly', () => {
    // Arrange
    renderWithProviders(<NewComponent />);
    
    // Assert
    expect(screen.getByText(/expected text/i)).toBeInTheDocument();
  });
});
```

### Testando Chamadas de API

```javascript
test('makes correct API call', async () => {
  // Arrange - Mock API response
  const mockData = { id: '1', name: 'Test' };
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => mockData
  });

  // Act - Render component
  renderWithProviders(<NewComponent />);

  // Assert - Verify API was called correctly
  await waitFor(() => {
    expect(fetch).toHaveBeenCalledWith(
      '/api/endpoint',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          'Authorization': 'Bearer fake-token'
        })
      })
    );
  });

  // Assert - Verify data is displayed
  expect(screen.getByText('Test')).toBeInTheDocument();
});
```

### Testando Interações do Usuário

```javascript
test('handles button click', async () => {
  // Arrange
  const mockOnClick = jest.fn();
  renderWithProviders(<NewComponent onClick={mockOnClick} />);

  // Act - Find and click button
  const button = screen.getByRole('button', { name: /click me/i });
  fireEvent.click(button);

  // Assert
  await waitFor(() => {
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });
});
```

### Testando Formulários

```javascript
test('validates form input', async () => {
  // Arrange
  renderWithProviders(<NewComponent />);

  // Act - Fill form with invalid data
  const input = screen.getByLabelText(/email/i);
  fireEvent.change(input, { target: { value: 'invalid-email' } });

  const submitButton = screen.getByRole('button', { name: /submit/i });
  fireEvent.click(submitButton);

  // Assert - Error message appears
  await waitFor(() => {
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
  });
});
```

### Testando Rendering Condicional

```javascript
test('shows loading state', () => {
  // Arrange - Never resolve promise
  fetch.mockImplementation(() => new Promise(() => {}));

  // Act
  renderWithProviders(<NewComponent />);

  // Assert
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
});

test('shows content after loading', async () => {
  // Arrange
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ data: 'content' })
  });

  // Act
  renderWithProviders(<NewComponent />);

  // Assert
  await waitFor(() => {
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    expect(screen.getByText('content')).toBeInTheDocument();
  });
});
```

### Testando Erros

```javascript
test('handles API error', async () => {
  // Arrange - Mock error response
  fetch.mockResolvedValueOnce({
    ok: false,
    status: 403,
    json: async () => ({ detail: 'Unauthorized' })
  });

  // Act
  renderWithProviders(<NewComponent />);

  // Assert
  await waitFor(() => {
    expect(screen.getByText(/unauthorized/i)).toBeInTheDocument();
  });
});

test('handles network error', async () => {
  // Arrange - Mock network failure
  fetch.mockRejectedValueOnce(new Error('Network error'));

  // Act
  renderWithProviders(<NewComponent />);

  // Assert
  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });
});
```

## Queries de Teste (Prioridade)

### 1. Queries Acessíveis (Preferidas)

```javascript
// Por role (melhor para acessibilidade)
screen.getByRole('button', { name: /submit/i })
screen.getByRole('textbox', { name: /email/i })

// Por label (para formulários)
screen.getByLabelText(/password/i)

// Por texto (para conteúdo)
screen.getByText(/welcome/i)
```

### 2. Queries Semânticas

```javascript
// Por placeholder
screen.getByPlaceholderText(/enter email/i)

// Por texto alternativo
screen.getByAltText(/logo/i)
```

### 3. Test IDs (Último Recurso)

```javascript
// Adicione ao componente: data-testid="my-element"
screen.getByTestId('my-element')
```

## Padrões de Asserção

### Backend

```python
# Status codes
assert response.status_code == 200
assert response.status_code == 201  # Created
assert response.status_code == 404  # Not Found

# Response content
assert response.json()["key"] == "value"
assert "key" in response.json()
assert isinstance(response.json(), list)

# Database state
assert db_session.query(Model).count() == 1
assert model.field == "expected_value"
```

### Frontend

```javascript
// Element presence
expect(screen.getByText(/text/i)).toBeInTheDocument();
expect(screen.queryByText(/text/i)).not.toBeInTheDocument();

// Visibility
expect(element).toBeVisible();
expect(element).not.toBeVisible();

// Form state
expect(input.value).toBe('expected');
expect(checkbox).toBeChecked();
expect(button).toBeDisabled();

// Function calls
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith('arg');
expect(mockFn).toHaveBeenCalledTimes(2);
```

## Dicas Importantes

### Backend

1. **Use fixtures** para dados comuns
2. **Isole testes** - cada teste deve funcionar independentemente
3. **Teste casos extremos** - valores nulos, strings vazias, etc.
4. **Mock externo** - não faça chamadas reais a APIs externas
5. **Documente** testes complexos com comentários

### Frontend

1. **Evite snapshots** - difíceis de manter
2. **Query por acessibilidade** - use roles e labels
3. **Use waitFor** para operações assíncronas
4. **Limpe mocks** no beforeEach
5. **Teste comportamento** do usuário, não implementação

## Checklist para Novos Testes

- [ ] Nome descritivo e claro
- [ ] Comentário explicando o objetivo
- [ ] Seguindo padrão AAA (Arrange, Act, Assert)
- [ ] Usa fixtures/mocks apropriados
- [ ] Testa um conceito por vez
- [ ] Falha quando deveria falhar
- [ ] Passa quando deveria passar
- [ ] Rápido (<1s se possível)
- [ ] Independente de outros testes
- [ ] Documentado se complexo

## Executando Seus Novos Testes

```bash
# Backend - teste específico
pytest tests/backend/test_new_feature.py::test_my_new_test -v

# Frontend - teste específico
npm test -- --testNamePattern="my new test"

# Todos os testes
./run_all_tests.sh
```

## Exemplos Prontos

Consulte os arquivos existentes para exemplos completos:
- `test_session_auth.py` - Autenticação
- `test_session_crud.py` - CRUD
- `test_session_workflow.py` - Workflows
- `Sessions.test.js` - Componentes React
- `CreateSession.test.js` - Formulários React
