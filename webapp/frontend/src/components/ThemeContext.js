import React, { createContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  return React.useContext(ThemeContext);
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'theme-default');

  useEffect(() => {
    // Apply the theme class to the body
    document.body.classList.remove('theme-default', 'theme-high-contrast', 'theme-soft');
    document.body.classList.add(theme);

    // Save theme in localStorage for persistence
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => {
      if (prevTheme === 'theme-high-contrast') return 'theme-soft';
      if (prevTheme === 'theme-soft') return 'theme-default';
      return 'theme-high-contrast';
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
