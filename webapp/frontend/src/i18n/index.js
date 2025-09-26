import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translations
import en from './translations/en';
import pt from './translations/pt';

const resources = {
  en: en,
  pt: pt
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: false,
    
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage']
    },

    interpolation: {
      escapeValue: false // React already does escaping
    },

    // Namespace configuration
    defaultNS: 'common',
    ns: ['common', 'auth', 'pages', 'accessibility']
  });

export default i18n;
