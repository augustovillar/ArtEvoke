import React from 'react';
import { useTranslation } from 'react-i18next';
import { getSupportedLanguages } from '../../118n/detector';
import './languageSelector.css';

const LanguageSelector = ({ className = '' }) => {
  const { i18n, t } = useTranslation('common');

  const handleLanguageChange = (event) => {
    const selectedLanguage = event.target.value;
    i18n.changeLanguage(selectedLanguage);
  };

  const languages = getSupportedLanguages();

  return (
    <div className={`language-selector ${className}`}>
      <select
        value={i18n.language}
        onChange={handleLanguageChange}
        className="language-select"
        aria-label={t('language.select')}
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSelector;
