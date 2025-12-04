import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './DropZone.module.css';

const DropZone = ({ position, event, onDrop, onRemove, onClick, isSelectable }) => {
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

    const handleRemoveClick = (e) => {
        e.stopPropagation(); // Prevent triggering onClick when clicking remove
        onRemove(position);
    };

    const handleClick = (e) => {
        // Only handle click if there's a selected event (touch/click mode)
        if (isSelectable && onClick) {
            e.preventDefault();
            onClick(position);
        }
    };

    return (
        <div
            className={`${styles.dropZone} ${isDropTarget ? styles.dropTarget : ''} ${event ? styles.filled : ''} ${isSelectable ? styles.selectable : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
            style={{ cursor: isSelectable ? 'pointer' : 'default' }}
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