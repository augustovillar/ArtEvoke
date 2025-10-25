import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import './Navbar.css';
import logo from '../../../assets/images/logepl.jpg';
import { useTheme } from '../../../contexts/ThemeContext';
import AccessibilityPanel from '../../ui/AccessibilityPanel';
import LanguageSelector from '../../../components/languageSelector/languageSelector';

const Navbar = () => {
    const { t } = useTranslation('common');
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isPanelOpen, setIsPanelOpen] = useState(false);

    const { toggleTheme } = useTheme();

    // Check if user is logged in from localStorage on mount  
    useEffect(() => {
        const token = localStorage.getItem('token'); // Check if token exists
        if (token) {
            setIsLoggedIn(true); // Set user as logged in
        }
    }, []);

    const toggleDropdown = () => {
        setDropdownOpen(!dropdownOpen);
    };

    const handleLogout = () => {
        localStorage.removeItem('token'); // Remove token from localStorage
        setIsLoggedIn(false); // Update the state to logged out
    };

    const handleOpenPanel = () => {
        setIsPanelOpen(true);
    };

    const handleClosePanel = () => {
        setIsPanelOpen(false);
    };

    return (
        <nav className="navbar navbar-expand-lg navbar-dark custom-navbar">
            <div className="center-text">
                {t('app.name')}
            </div>
            <button id='accessibility-button' onClick={handleOpenPanel}>
                {t('navbar.accessibility')}
            </button>
        
            <div className="nav-links">
                <Link to="/">{t('navbar.home')}</Link>
                <Link to="/story">{t('navbar.memoryReconstruction')}</Link>
                <Link to="/artsearch">{t('navbar.artExploration')}</Link>
                <Link to="/about">{t('navbar.about')}</Link>

                {/* Language Selector */}
                <LanguageSelector />

                {/* Conditionally render Account dropdown based on login state */}
                {isLoggedIn ? (
                    <div className={`dropdown ${dropdownOpen ? 'open' : ''}`}>
                        <button onClick={toggleDropdown} className="dropbtn">
                            {t('navbar.profile')}
                        </button>
                        <div className="dropdown-content">
                            <Link to="/profile" onClick={toggleDropdown}>
                                {t('navbar.profile')}
                            </Link>
                            <Link to="/" onClick={handleLogout}>
                                {t('navbar.logout')}
                            </Link>
                        </div>
                    </div>
                ) : (
                    <div className={`dropdown ${dropdownOpen ? 'open' : ''}`}>
                        <button onClick={toggleDropdown} className="dropbtn">
                            {t('navbar.account')}
                        </button>
                        <div className="dropdown-content">
                            <Link to="/auth/role-selection" onClick={toggleDropdown}>
                                {t('navbar.signUp')}
                            </Link>
                            <Link to="/auth/role-selection" onClick={toggleDropdown}>
                                {t('navbar.login')}
                            </Link>
                        </div>
                    </div>
                )}
            </div>

            {/* Conditionally render the Accessibility Panel */}
            {isPanelOpen && <AccessibilityPanel onClose={handleClosePanel} />}
        </nav>
    );
};

export default Navbar;