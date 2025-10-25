import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './DropZone.module.css';

const DropZone = ({ position, event, onDrop, onRemove }) => {
    const { t } = useTranslation();
    const [isDropTarget, setIsDropTarget] = useState(false);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDropTarget(true);
    };

    const handleDragLeave = (e) => {
        setIsDropTarget(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDropTarget(false);
        onDrop(e, position);
    };

    const handleRemoveClick = () => {
        onRemove(position);
    };

    return (
        <div
            className={`${styles.dropZone} ${isDropTarget ? styles.dropTarget : ''} ${event ? styles.filled : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            <div className={styles.positionNumber}>
                {position + 1}.
            </div>
            <div className={styles.dropContent}>
                {event ? (
                    <div className={styles.placedEvent}>
                        <span className={styles.eventText}>{event}</span>
                        <button 
                            className={styles.removeButton}
                            onClick={handleRemoveClick}
                            title={t('evaluation.removeEvent') || 'Remover evento'}
                        >
                            ×
                        </button>
                    </div>
                ) : (
                    <div className={styles.dropPlaceholder}>
                        {t('evaluation.dropHere') || 'Solte aqui'}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DropZone;