import React from 'react';
import styles from './Timer.module.css';

const Timer = ({ timeLeft, duration, isComplete }) => {
  const progress = ((duration - timeLeft) / duration) * 100;
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={styles.timerContainer}>
      <svg className={styles.progressRing} viewBox="0 0 200 200">
        {/* Background circle */}
        <circle
          className={styles.progressRingCircleBg}
          cx="100"
          cy="100"
          r="85"
        />
        {/* Progress circle */}
        <circle
          className={`${styles.progressRingCircle} ${isComplete ? styles.complete : ''}`}
          cx="100"
          cy="100"
          r="85"
          style={{
            strokeDashoffset: 534 - (534 * progress) / 100
          }}
        />
      </svg>
      
      <div className={styles.timeDisplay}>
        <span className={styles.timeText}>
          {isComplete ? '✓' : formatTime(timeLeft)}
        </span>
      </div>
    </div>
  );
};

export default Timer;