import React, { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './ImageRecallQuestion.module.css';

// item: { url, name, id? }
// sessionData.phase1 should include: selectedImages (array) and optionally galleryImages (full list) for distractors
const ImageRecallQuestion = ({ item, itemNumber, totalItems, onAnswer }) => {
  const { t } = useTranslation('common');
  const [selected, setSelected] = useState(null);
  const [startTime] = useState(Date.now());

  // Build options: correct image + up to 3 simple distractors using a placeholder for now
  const options = useMemo(() => {
    const distractors = [
      { url: '/api/placeholder/art-distractor-1.jpg', name: 'Distrator A', isDistractor: true },
      { url: '/api/placeholder/art-distractor-2.jpg', name: 'Distrator B', isDistractor: true },
      { url: '/api/placeholder/art-distractor-3.jpg', name: 'Distrator C', isDistractor: true }
    ];
    const base = [{ url: item.url, name: item.name, isDistractor: false }].concat(distractors);
    return base.sort(() => Math.random() - 0.5);
  }, [item]);

  const handleSubmit = () => {
    if (!selected) {
      alert(t('evaluation.pleaseSelectImage') || 'Por favor, selecione uma imagem antes de continuar.');
      return;
    }
    const timeSpent = Date.now() - startTime;
    const isCorrect = selected === item.url;
    onAnswer(item.id || item.url, selected, isCorrect, timeSpent);
  };

  useEffect(() => {
    // reset state when item changes
    setSelected(null);
  }, [item?.url]);

  return (
    <div className={styles.container}>
      <div className={styles.header}> 
        <h2>{(t('evaluation.imageRecallTitle') || 'Pergunta sobre a Imagem')} {itemNumber}/{totalItems}</h2>
        <p className={styles.instruction}>
          {t('evaluation.imageRecallInstruction') || 'Qual destas imagens você acabou de selecionar?'}
        </p>
      </div>

      <div className={styles.grid}>
        {options.map((opt, idx) => (
          <div
            key={idx}
            className={`${styles.imageContainer} ${selected === opt.url ? styles.selected : ''}`}
            onClick={() => setSelected(opt.url)}
          >
            <img
              src={opt.url}
              alt={`Opção ${idx + 1}`}
              className={styles.image}
              onError={(e) => {
                e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-size="14"%3EImagem%3C/text%3E%3C/svg%3E';
              }}
            />
            <span className={styles.caption}>{opt.name}</span>
          </div>
        ))}
      </div>

      <div className={styles.buttonRow}>
        <button className={styles.primary} onClick={handleSubmit} disabled={!selected}>
          {t('evaluation.nextQuestion') || 'Próxima Pergunta'}
        </button>
      </div>
    </div>
  );
};

export default ImageRecallQuestion;
