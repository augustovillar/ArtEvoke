import React from 'react';
import styles from './DraggableEventItem.module.css';

const DraggableEventItem = ({ event, index, onDragStart, isDragging }) => {
    const handleDragStart = (e) => {
        onDragStart(e, event);
    };

    const handleDragEnd = (e) => {
        // Clean up any drag state if needed
    };

    return (
        <div
            className={`${styles.eventItem} ${isDragging ? styles.dragging : ''}`}
            draggable
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
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