import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionReadAloudButton } from '../../../../components/ui';
import DraggableEventItem from './DraggableEventItem';
import DropZone from './DropZone';
import styles from './ChronologyOrderQuestion.module.css';

const ChronologyOrderQuestion = ({ onAnswer }) => {
    const { t } = useTranslation();
    const [startTime] = useState(Date.now());

    // Mock data - in final version, this will come from Maritaca AI
    const mockStoryEvents = {
        correctOrder: [
            "Ele comeu sorvete",
            "Ele foi à escola", 
            "Ele ficou satisfeito"
        ]
    };

    const [shuffledEvents, setShuffledEvents] = useState([]);
    const [orderedEvents, setOrderedEvents] = useState([]);
    const [draggedItem, setDraggedItem] = useState(null);
    const [attempts, setAttempts] = useState(0);

    // Initialize shuffled events on component mount
    useEffect(() => {
        const shuffled = [...mockStoryEvents.correctOrder].sort(() => Math.random() - 0.5);
        setShuffledEvents(shuffled);
        setOrderedEvents(new Array(mockStoryEvents.correctOrder.length).fill(null));
    }, []);

    const handleDragStart = (event, eventText) => {
        setDraggedItem(eventText);
        event.dataTransfer.setData('text/plain', eventText);
    };

    const handleDrop = (event, position) => {
        event.preventDefault();
        const eventText = event.dataTransfer.getData('text/plain');
        
        if (!eventText) return;

        // Remove from shuffled events if it's still there
        setShuffledEvents(prev => prev.filter(item => item !== eventText));
        
        // Place in ordered position
        const newOrderedEvents = [...orderedEvents];
        
        // If position is already occupied, move that item back to shuffled
        if (newOrderedEvents[position] !== null) {
            setShuffledEvents(prev => [...prev, newOrderedEvents[position]]);
        }
        
        newOrderedEvents[position] = eventText;
        setOrderedEvents(newOrderedEvents);
        setDraggedItem(null);
    };

    const handleRemoveFromOrder = (position) => {
        const eventText = orderedEvents[position];
        if (eventText) {
            setShuffledEvents(prev => [...prev, eventText]);
            const newOrderedEvents = [...orderedEvents];
            newOrderedEvents[position] = null;
            setOrderedEvents(newOrderedEvents);
        }
    };

    const isComplete = orderedEvents.every(event => event !== null);

    const handleSubmit = () => {
        if (!isComplete) {
            alert(t('evaluation.completeOrder') || 'Complete a ordenação para continuar.');
            return;
        }

        const timeSpent = Date.now() - startTime;
        const isCorrect = JSON.stringify(orderedEvents) === JSON.stringify(mockStoryEvents.correctOrder);
        
        const answer = {
            questionType: 'chronology_order',
            userOrder: orderedEvents,
            correctOrder: mockStoryEvents.correctOrder,
            isCorrect,
            timeSpent,
            attempts: attempts + 1
        };

        setAttempts(prev => prev + 1);
        onAnswer('chronology-order', answer, timeSpent);
    };

    const questionText = t('evaluation.chronologyInstruction') || 
        'Arraste os eventos para organizá-los na ordem cronológica correta:';

    return (
        <div className={styles.container}>
            <div className={styles.questionHeader}>
                <h2>
                    {t('evaluation.chronologyTitle') || 'Ordem dos Eventos'}
                    <QuestionReadAloudButton 
                        text={`${t('evaluation.chronologyTitle') || 'Ordem dos Eventos'}. ${questionText}`}
                    />
                </h2>
            </div>

            <div className={styles.instructionSection}>
                <p className={styles.instruction}>
                    {questionText}
                </p>
            </div>

            <div className={styles.gameArea}>
                {/* Events to drag */}
                <div className={styles.eventsPool}>
                    <h3 className={styles.sectionTitle}>
                        {t('evaluation.eventsToOrder') || 'Eventos para ordenar:'}
                    </h3>
                    <div className={styles.eventsList}>
                        {shuffledEvents.map((event, index) => (
                            <DraggableEventItem
                                key={`${event}-${index}`}
                                event={event}
                                index={index}
                                onDragStart={handleDragStart}
                                isDragging={draggedItem === event}
                            />
                        ))}
                    </div>
                </div>

                {/* Drop zones */}
                <div className={styles.chronologyArea}>
                    <h3 className={styles.sectionTitle}>
                        {t('evaluation.chronologicalOrder') || 'Ordem Cronológica:'}
                    </h3>
                    <div className={styles.dropZonesList}>
                        {orderedEvents.map((event, position) => (
                            <DropZone
                                key={position}
                                position={position}
                                event={event}
                                onDrop={handleDrop}
                                onRemove={() => handleRemoveFromOrder(position)}
                            />
                        ))}
                    </div>
                </div>
            </div>

            <div className={styles.buttonContainer}>
                <button
                    onClick={handleSubmit}
                    className={styles.submitButton}
                    disabled={!isComplete}
                >
                    {t('evaluation.nextQuestion') || 'Próxima Pergunta'}
                </button>
            </div>
        </div>
    );
};

export default ChronologyOrderQuestion;