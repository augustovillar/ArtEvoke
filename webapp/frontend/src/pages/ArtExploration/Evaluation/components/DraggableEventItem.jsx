import React from 'react';
import styles from './DraggableEventItem.module.css';

const DraggableEventItem = ({ event, index, onDragStart, isDragging, onClick, isSelected }) => {
    const handleDragStart = (e) => {
        onDragStart(e, event);
    };

    const handleDragEnd = (e) => {
        // Clean up any drag state if needed
    };

    const handleClick = (e) => {
        // Prevent click from triggering drag on touch devices
        e.preventDefault();
        if (onClick) {
            onClick(event);
        }
    };

    return (
        <div
            className={`${styles.eventItem} ${isDragging ? styles.dragging : ''} ${isSelected ? styles.selected : ''}`}
            draggable
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            onClick={handleClick}
            style={{ cursor: 'pointer' }}
        >
            <div className={styles.dragHandle}>
                <span className={styles.dragIcon}>⋮⋮</span>
            </div>
            <div className={styles.eventText}>
                {event}
            </div>
        </div>
    );
};

export default DraggableEventItem;