import React from 'react';
import './Footer.css';
import logoUcl from '../../../assets/images/logoucl.png';

const Footer = () => {
    return (
        <footer className="footer">
            <div className="footer-main-content">
                <div className="footer-text-column">
                    <p>
                        &copy; 2025{' '}
                        <a href="mailto:augubvs@gmail.com">Augusto B. V. Silva</a>
                        {', '}
                        <a href="mailto:alvarenga.vinicius@usp.br">Vinicius Alvarenga</a>
                    </p>
                </div>
                
                <div className="footer-logos-row">
                    <img src={logoUcl} alt='UCL' className="footer-logo"></img>
                </div>
            </div>
        </footer>
    );
};

export default Footer;