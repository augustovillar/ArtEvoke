/**
 * Tests for CreateSession component
 * Tests the session creation modal functionality
 */
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import CreateSession from '../../../frontend/src/pages/Sessions/CreateSession';
import i18n from './mocks/i18nMock';

const renderWithProviders = (component) => {
  return render(
    <I18nextProvider i18n={i18n}>
      {component}
    </I18nextProvider>
  );
};

describe('CreateSession Component', () => {
  const mockOnClose = jest.fn();
  const mockOnSuccess = jest.fn();
  const patientId = '123';

  beforeEach(() => {
    fetch.mockClear();
    mockOnClose.mockClear();
    mockOnSuccess.mockClear();
    localStorage.getItem.mockReturnValue('fake-token');
  });

  describe('Rendering', () => {
    test('renders create session form', () => {
      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      expect(screen.getByText(/criar nova sessão/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/selecionar modo/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/tempo de interrupção/i)).toBeInTheDocument();
    });

    test('shows patient selector when no patientId provided', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { id: '1', name: 'Patient 1' },
          { id: '2', name: 'Patient 2' },
        ],
      });

      renderWithProviders(
        <CreateSession
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      await waitFor(() => {
        expect(screen.getByLabelText(/selecionar paciente/i)).toBeInTheDocument();
      });
    });

    test('hides patient selector when patientId provided', () => {
      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      expect(screen.queryByLabelText(/selecionar paciente/i)).not.toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    test('validates required patient selection', async () => {
      renderWithProviders(
        <CreateSession
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      const submitButton = screen.getByText(/criar sessão/i);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/selecione um paciente/i)).toBeInTheDocument();
      });
    });

    test('validates required mode selection', async () => {
      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      // Clear the mode field
      const modeSelect = screen.getByLabelText(/selecionar modo/i);
      fireEvent.change(modeSelect, { target: { value: '' } });

      const submitButton = screen.getByText(/criar sessão/i);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/selecione um modo/i)).toBeInTheDocument();
      });
    });

    test('validates minimum interruption time', async () => {
      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      const interruptionInput = screen.getByLabelText(/tempo de interrupção/i);
      fireEvent.change(interruptionInput, { target: { value: '0' } });

      const submitButton = screen.getByText(/criar sessão/i);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/deve ser pelo menos 1 segundo/i)).toBeInTheDocument();
      });
    });

    test('validates maximum interruption time', async () => {
      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      const interruptionInput = screen.getByLabelText(/tempo de interrupção/i);
      fireEvent.change(interruptionInput, { target: { value: '500' } });

      const submitButton = screen.getByText(/criar sessão/i);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/não pode exceder 300 segundos/i)).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission', () => {
    test('submits form with valid data', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 'new-session-id',
          patient_id: patientId,
          mode: 'memory_reconstruction',
          interruption_time: 15,
          status: 'pending',
        }),
      });

      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      // Fill form
      const modeSelect = screen.getByLabelText(/selecionar modo/i);
      fireEvent.change(modeSelect, { target: { value: 'memory_reconstruction' } });

      const interruptionInput = screen.getByLabelText(/tempo de interrupção/i);
      fireEvent.change(interruptionInput, { target: { value: '15' } });

      // Submit
      const submitButton = screen.getByText(/criar sessão/i);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          '/api/sessions/',
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Authorization': 'Bearer fake-token',
              'Content-Type': 'application/json',
            }),
            body: JSON.stringify({
              patient_id: patientId,
              mode: 'memory_reconstruction',
              interruption_time: 15,
            }),
          })
        );
      });

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalled();
      });
    });

    test('handles submission error - no access', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({ detail: "You don't have access to this patient" }),
      });

      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      const submitButton = screen.getByText(/criar sessão/i);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/não tem acesso/i)).toBeInTheDocument();
      });

      expect(mockOnSuccess).not.toHaveBeenCalled();
    });

    test('handles generic submission error', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: "Server error" }),
      });

      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      const submitButton = screen.getByText(/criar sessão/i);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/falha ao criar sessão/i)).toBeInTheDocument();
      });
    });

    test('handles network error', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      const submitButton = screen.getByText(/criar sessão/i);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/falha ao criar sessão/i)).toBeInTheDocument();
      });
    });
  });

  describe('Mode Selection', () => {
    test('allows selecting memory_reconstruction mode', () => {
      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      const modeSelect = screen.getByLabelText(/selecionar modo/i);
      fireEvent.change(modeSelect, { target: { value: 'memory_reconstruction' } });

      expect(modeSelect.value).toBe('memory_reconstruction');
    });

    test('allows selecting art_exploration mode', () => {
      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      const modeSelect = screen.getByLabelText(/selecionar modo/i);
      fireEvent.change(modeSelect, { target: { value: 'art_exploration' } });

      expect(modeSelect.value).toBe('art_exploration');
    });

    test('allows selecting both mode', () => {
      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      const modeSelect = screen.getByLabelText(/selecionar modo/i);
      fireEvent.change(modeSelect, { target: { value: 'both' } });

      expect(modeSelect.value).toBe('both');
    });
  });

  describe('Cancel Button', () => {
    test('calls onClose when cancel button clicked', () => {
      renderWithProviders(
        <CreateSession
          patientId={patientId}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />
      );

      const cancelButton = screen.getByText(/cancelar/i);
      fireEvent.click(cancelButton);

      expect(mockOnClose).toHaveBeenCalled();
    });
  });
});
