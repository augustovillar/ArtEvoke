import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n.use(initReactI18next).init({
  lng: 'pt',
  fallbackLng: 'pt',
  ns: ['common'],
  defaultNS: 'common',
  resources: {
    pt: {
      common: {
        common: {
          loading: 'Carregando...',
          back: 'Voltar',
          cancel: 'Cancelar',
        },
        sessions: {
          title: 'Sessões',
          createSession: 'Criar Nova Sessão',
          noSessions: 'Nenhuma sessão encontrada.',
          selectPatientFirst: 'Selecione um paciente para visualizar e criar sessões.',
          mySessions: 'Minhas Sessões',
          patientSessions: 'Sessões do Paciente',
          mode: 'Modo',
          status: 'Status',
          interruptionTime: 'Tempo de Interrupção',
          createdAt: 'Criada em',
          startedAt: 'Iniciada em',
          completedAt: 'Concluída em',
          start: 'Iniciar',
          continue: 'Continuar',
          view: 'Visualizar',
          delete: 'Excluir',
          modes: {
            memory_reconstruction: 'Reconstrução de Memória',
            art_exploration: 'Exploração de Arte',
            both: 'Ambos',
          },
          statuses: {
            pending: 'Pendente',
            in_progress: 'Em Progresso',
            completed: 'Concluída',
          },
          create: {
            title: 'Criar Nova Sessão',
            selectPatient: 'Selecionar Paciente',
            selectMode: 'Selecionar Modo',
            interruptionTime: 'Tempo de Interrupção (segundos)',
            submit: 'Criar Sessão',
            cancel: 'Cancelar',
            validation: {
              patientRequired: 'Selecione um paciente',
              modeRequired: 'Selecione um modo',
              interruptionTimeMin: 'O tempo de interrupção deve ser pelo menos 1 segundo',
              interruptionTimeMax: 'O tempo de interrupção não pode exceder 300 segundos',
            },
          },
          errors: {
            loadFailed: 'Falha ao carregar sessões',
            createFailed: 'Falha ao criar sessão',
            noAccess: 'Você não tem acesso a este paciente',
            unauthorized: 'Você não tem permissão para acessar estas sessões',
          },
        },
      },
    },
  },
});

export default i18n;
