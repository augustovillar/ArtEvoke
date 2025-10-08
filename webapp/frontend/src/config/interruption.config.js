export const INTERRUPTION_CONFIG = {
  ART_EXPLORATION: {
    duration: 5, // segundos
    title: "História Gerada com Sucesso!",
    message: "Por favor, aguarde um momento antes de prosseguir para a avaliação.",
    buttonText: "Continuar para Avaliação"
  },
  MEMORY_RECONSTRUCTION: {
    duration: 7, // segundos
    title: "Visualização Concluída!",
    message: "Reserve um momento para refletir sobre as imagens que você viu.",
    buttonText: "Iniciar Avaliação"
  }
};

// Para uso futuro das sessões
export const NAVIGATION_MODES = {
  DIRECT: 'direct',        // Vindo da navbar diretamente
  SESSION: 'session'       // Vindo de uma sessão
};