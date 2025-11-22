import React, { useEffect, useState } from 'react';
import './Toast.css';

const Toast = ({ message, type = 'warning', duration = 5000, onClose }) => {
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsVisible(false);
            setTimeout(() => {
                if (onClose) onClose();
            }, 300); // Wait for fade-out animation
        }, duration);

        return () => clearTimeout(timer);
    }, [duration, onClose]);

    if (!isVisible) return null;

    return (
        <div className={`toast toast-${type} ${isVisible ? 'toast-visible' : ''}`}>
            <div className="toast-content">
                <span className="toast-message">{message}</span>
                <button 
                    className="toast-close" 
                    onClick={() => {
                        setIsVisible(false);
                        setTimeout(() => {
                            if (onClose) onClose();
                        }, 300);
                    }}
                    aria-label="Close"
                >
                    ×
                </button>
            </div>
        </div>
    );
};

export default Toast;

