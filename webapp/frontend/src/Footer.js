import React from 'react';
import { useTranslation } from 'react-i18next';
import './Footer.css';
import logoEpl from './images/logepl.jpg';
import logoUcl from './images/logoucl.png';
import logoMuseum from './images/logo_museum.jpg';
import logoIdLab from './images/idlab_logo.jpg';

const Footer = () => {
    const { t } = useTranslation('common');

    return (
        <footer className="footer">
            <div className="footer-main-content">
                <div className="footer-text-column">
                    <p>&copy; 2025 {t('footer.copyright')}</p>
                    <p>{t('footer.university')}</p>
                    <p>{t('footer.supervisor')}</p>
                    <p>
                        <a href="mailto:marc.bejjani@student.uclouvain.be">marc.bejjani@student.uclouvain.be</a><br/>
                        <a href="mailto:augusto.silva@student.uclouvain.be">augusto.silva@student.uclouvain.be</a>
                    </p>
                </div>
                
                <div className="footer-logos-row">
                    <img src={logoUcl} alt='UCL' className="footer-logo"></img>
                    <img src={logoEpl} alt='EPL' className="footer-logo"></img>
                    <img src={logoMuseum} alt='Museum' className="footer-logo"></img>
                    <img src={logoIdLab} alt='IDLAB' className="footer-logo"></img>
                </div>
            </div>
        </footer>
    );
};

export default Footer;