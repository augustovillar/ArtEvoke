// Custom language detection utilities
export const detectLanguage = () => {
  // Priority order: localStorage > URL params > navigator > fallback
  
  // 1. Check localStorage
  const savedLang = localStorage.getItem('i18nextLng');
  if (savedLang && ['en', 'pt'].includes(savedLang)) {
    return savedLang;
  }
  
  // 2. Check URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const urlLang = urlParams.get('lang');
  if (urlLang && ['en', 'pt'].includes(urlLang)) {
    return urlLang;
  }
  
  // 3. Check navigator language
  const navigatorLang = navigator.language.split('-')[0]; // 'pt-BR' -> 'pt'
  if (['en', 'pt'].includes(navigatorLang)) {
    return navigatorLang;
  }
  
  // 4. Fallback
  return 'en';
};

export const saveLanguage = (lang) => {
  localStorage.setItem('i18nextLng', lang);
};

export const getSupportedLanguages = () => [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'pt', name: 'Português', flag: '🇧🇷' }
];
