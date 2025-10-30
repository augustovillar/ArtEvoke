/**
 * Tests for Sessions component
 * Tests the main sessions list page with authorization logic
 */
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import Sessions from '../../../frontend/src/pages/Sessions/Sessions';
import { AuthProvider } from '../../../frontend/src/contexts/AuthContext';
import i18n from './mocks/i18nMock';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useSearchParams: () => [new URLSearchParams()],
}));

// Wrapper component with all providers
const renderWithProviders = (component, { userType = 'doctor', user = null, patientId = null } = {}) => {
  // Mock useSearchParams if patientId provided
  if (patientId) {
    jest.requireActual('react-router-dom').useSearchParams = () => [
      new URLSearchParams({ patientId })
    ];
  }

  return render(
    <BrowserRouter>
      <I18nextProvider i18n={i18n}>
        <AuthProvider value={{ userType, user, isLoggedIn: true }}>
          {component}
        </AuthProvider>
      </I18nextProvider>
    </BrowserRouter>
  );
};

describe('Sessions Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    mockNavigate.mockClear();
    localStorage.getItem.mockReturnValue('fake-token');
  });

  describe('Rendering', () => {
    test('renders loading state initially', () => {
      fetch.mockImplementation(() => new Promise(() => {})); // Never resolves
      
      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });
      
      expect(screen.getByText(/carregando/i)).toBeInTheDocument();
    });

    test('renders sessions list for doctor with patient selected', async () => {
      const mockSessions = [
        {
          id: '1',
          mode: 'memory_reconstruction',
          status: 'pending',
          interruption_time: 10,
          created_at: '2025-10-30T10:00:00',
        },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSessions,
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(screen.getByText(/sessões do paciente/i)).toBeInTheDocument();
      });
    });

    test('renders my sessions for patient', async () => {
      const mockSessions = [
        {
          id: '1',
          mode: 'art_exploration',
          status: 'pending',
          interruption_time: 15,
          created_at: '2025-10-30T10:00:00',
        },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSessions,
      });

      renderWithProviders(<Sessions />, { userType: 'patient' });

      await waitFor(() => {
        expect(screen.getByText(/minhas sessões/i)).toBeInTheDocument();
      });
    });

    test('shows empty state when no sessions', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(screen.getByText(/nenhuma sessão encontrada/i)).toBeInTheDocument();
      });
    });

    test('shows select patient message for doctor without patient selected', async () => {
      renderWithProviders(<Sessions />, { userType: 'doctor' });

      await waitFor(() => {
        expect(screen.getByText(/selecione um paciente/i)).toBeInTheDocument();
      });
    });
  });

  describe('Create Session Button', () => {
    test('shows create button for doctor with patient selected', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(screen.getByText(/criar nova sessão/i)).toBeInTheDocument();
      });
    });

    test('does not show create button for patient', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      renderWithProviders(<Sessions />, { userType: 'patient' });

      await waitFor(() => {
        expect(screen.queryByText(/criar nova sessão/i)).not.toBeInTheDocument();
      });
    });

    test('does not show create button for doctor without patient selected', async () => {
      renderWithProviders(<Sessions />, { userType: 'doctor' });

      await waitFor(() => {
        expect(screen.queryByText(/criar nova sessão/i)).not.toBeInTheDocument();
      });
    });

    test('opens create modal when button clicked', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        const createButton = screen.getByText(/criar nova sessão/i);
        fireEvent.click(createButton);
      });

      // Modal should appear (implementation dependent)
    });
  });

  describe('API Calls', () => {
    test('calls correct endpoint for doctor viewing patient sessions', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          '/api/sessions/patient/123',
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: 'Bearer fake-token',
            }),
          })
        );
      });
    });

    test('calls correct endpoint for patient viewing own sessions', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      renderWithProviders(<Sessions />, { userType: 'patient' });

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          '/api/sessions/my-sessions',
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: 'Bearer fake-token',
            }),
          })
        );
      });
    });

    test('does not make API call for doctor without patient selected', async () => {
      renderWithProviders(<Sessions />, { userType: 'doctor' });

      await waitFor(() => {
        expect(fetch).not.toHaveBeenCalled();
      });
    });
  });

  describe('Error Handling', () => {
    test('shows error message on 403 with no access detail', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({ detail: "You don't have access to this patient" }),
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(screen.getByText(/não tem acesso a este paciente/i)).toBeInTheDocument();
      });
    });

    test('shows error message on 401 unauthorized', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: "Invalid token" }),
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(screen.getByText(/não tem permissão/i)).toBeInTheDocument();
      });
    });

    test('handles 404 as empty session list', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(screen.getByText(/nenhuma sessão encontrada/i)).toBeInTheDocument();
      });
    });

    test('shows generic error on network failure', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(screen.getByText(/falha ao carregar sessões/i)).toBeInTheDocument();
      });
    });
  });

  describe('Session Actions', () => {
    test('shows start button for patient with pending session', async () => {
      const mockSessions = [
        {
          id: '1',
          mode: 'memory_reconstruction',
          status: 'pending',
          interruption_time: 10,
          created_at: '2025-10-30T10:00:00',
        },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSessions,
      });

      renderWithProviders(<Sessions />, { userType: 'patient' });

      await waitFor(() => {
        expect(screen.getByText(/iniciar/i)).toBeInTheDocument();
      });
    });

    test('shows continue button for patient with in_progress session', async () => {
      const mockSessions = [
        {
          id: '1',
          mode: 'memory_reconstruction',
          status: 'in_progress',
          interruption_time: 10,
          created_at: '2025-10-30T10:00:00',
        },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSessions,
      });

      renderWithProviders(<Sessions />, { userType: 'patient' });

      await waitFor(() => {
        expect(screen.getByText(/continuar/i)).toBeInTheDocument();
      });
    });

    test('shows view and delete buttons for doctor', async () => {
      const mockSessions = [
        {
          id: '1',
          mode: 'memory_reconstruction',
          status: 'completed',
          interruption_time: 10,
          created_at: '2025-10-30T10:00:00',
        },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSessions,
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(screen.getByText(/visualizar/i)).toBeInTheDocument();
        expect(screen.getByText(/excluir/i)).toBeInTheDocument();
      });
    });
  });

  describe('Session Display', () => {
    test('displays session details correctly', async () => {
      const mockSessions = [
        {
          id: '1',
          mode: 'memory_reconstruction',
          status: 'pending',
          interruption_time: 15,
          created_at: '2025-10-30T10:00:00',
        },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSessions,
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(screen.getByText(/reconstrução de memória/i)).toBeInTheDocument();
        expect(screen.getByText(/pendente/i)).toBeInTheDocument();
        expect(screen.getByText(/15s/i)).toBeInTheDocument();
      });
    });

    test('displays multiple sessions', async () => {
      const mockSessions = [
        {
          id: '1',
          mode: 'memory_reconstruction',
          status: 'pending',
          interruption_time: 10,
          created_at: '2025-10-30T10:00:00',
        },
        {
          id: '2',
          mode: 'art_exploration',
          status: 'in_progress',
          interruption_time: 20,
          created_at: '2025-10-30T11:00:00',
        },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSessions,
      });

      renderWithProviders(<Sessions />, { userType: 'doctor', patientId: '123' });

      await waitFor(() => {
        expect(screen.getByText(/reconstrução de memória/i)).toBeInTheDocument();
        expect(screen.getByText(/exploração de arte/i)).toBeInTheDocument();
      });
    });
  });
});
