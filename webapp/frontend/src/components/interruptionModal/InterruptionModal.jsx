import React from 'react';
import { useTranslation } from 'react-i18next';
import Timer from '../Timer/Timer';
import styles from './InterruptionModal.module.css';

const InterruptionModal = ({
  isOpen,
  duration,
  translationKey,
  onComplete
}) => {
  const { t } = useTranslation('common');
  const [timeLeft, setTimeLeft] = React.useState(duration);
  const [isTimerComplete, setIsTimerComplete] = React.useState(false);

  React.useEffect(() => {
    if (!isOpen) {
      setTimeLeft(duration);
      setIsTimerComplete(false);
      return;
    }

    if (timeLeft <= 0) {
      setIsTimerComplete(true);
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          setIsTimerComplete(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isOpen, timeLeft, duration]);

  if (!isOpen) return null;

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <div className={styles.content}>
          <h2 className={styles.title}>{t(`${translationKey}.title`)}</h2>
          
          <Timer 
            timeLeft={timeLeft} 
            duration={duration}
            isComplete={isTimerComplete}
          />
          
          <p className={styles.message}>{t(`${translationKey}.message`)}</p>
          
          <button
            className={`${styles.button} ${!isTimerComplete ? styles.buttonDisabled : styles.buttonEnabled}`}
            onClick={onComplete}
            disabled={!isTimerComplete}
          >
            {isTimerComplete ? t(`${translationKey}.buttonText`) : t(`${translationKey}.waitText`, { seconds: timeLeft })}
          </button>
        </div>
      </div>
    </div>
  );
};

export default InterruptionModal;