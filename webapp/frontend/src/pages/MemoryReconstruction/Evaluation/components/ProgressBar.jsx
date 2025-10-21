import React from 'react';
import { useTranslation } from 'react-i18next';
import styles from './ProgressBar.module.css';

const ProgressBar = ({ current, total }) => {
    const { t } = useTranslation();
    // Garante que o progresso não ultrapasse 100% mesmo se current vier maior que total
    const safeTotal = typeof total === 'number' && total > 0 ? total : 1;
    const clampedCurrent = Math.min(Math.max(current, 0), safeTotal);
    const percentage = Math.min(100, (clampedCurrent / safeTotal) * 100);

    return (
        <div className={styles.container}>
            <div className={styles.info}>
                <span className={styles.text}>
                    {t('evaluation.progress') || 'Progresso'}: {clampedCurrent} / {total}
                </span>
                <span className={styles.percentage}>
                    {Math.round(percentage)}%
                </span>
            </div>
            <div className={styles.barBackground}>
                <div 
                    className={styles.barFill} 
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
};

export default ProgressBar;
