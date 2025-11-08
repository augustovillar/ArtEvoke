import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionReadAloudButton } from '../../../../components/ui';
import styles from './ImageRecognitionQuestion.module.css';

const ImageRecognitionQuestion = ({ section, sectionNumber, totalSections, onAnswer }) => {
    const { t } = useTranslation();
    const [selectedImage, setSelectedImage] = useState(null);
    const [startTime] = useState(Date.now());
    const [shuffledImages, setShuffledImages] = useState([]);

    useEffect(() => {
        // Adicionar 2 imagens distratoras
        // TODO: Buscar distratores reais da API
        const mockDistractors = [
            {
                url: '/api/placeholder/distractor1.jpg',
                name: 'Distrator 1',
                isDistractor: true
            },
            {
                url: '/api/placeholder/distractor2.jpg',
                name: 'Distrator 2',
                isDistractor: true
            }
        ];

        // Criar array com todas as imagens mostradas + distratores
        const allImages = [
            ...(section.imagesShown || []).map(img => ({
                ...img,
                isDistractor: false,
                isCorrect: img.url === section.selectedImage?.url
            })),
            ...mockDistractors
        ];

        // Embaralhar as imagens
        const shuffled = allImages.sort(() => Math.random() - 0.5);
        setShuffledImages(shuffled);
    }, [section]);

    const handleImageSelect = (image) => {
        setSelectedImage(image.url);
    };

    const handleSubmitAnswer = () => {
        if (!selectedImage) {
            alert(t('evaluation.pleaseSelectImage') || 'Por favor, selecione uma imagem antes de continuar.');
            return;
        }

        const timeSpent = Date.now() - startTime;
        const isCorrect = selectedImage === section.selectedImage.url;

        onAnswer(section.sectionId, selectedImage, isCorrect, timeSpent);
    };

    return (
        <div className={styles.container}>
            <div className={styles.questionHeader}>
                <h2>
                    {t('evaluation.imageRecognitionTitle') || 'Pergunta de Reconhecimento'} {sectionNumber}/{totalSections}
                    <QuestionReadAloudButton 
                        text={`${t('evaluation.imageRecognitionTitle') || 'Pergunta de Reconhecimento'} ${sectionNumber} de ${totalSections}. ${t('evaluation.imageRecognitionInstruction') || 'Qual das imagens abaixo você selecionou anteriormente para esta seção da história?'} Texto da seção: ${section.sectionText}`}
                    />
                </h2>
                <p className={styles.instruction}>
                    {t('evaluation.imageRecognitionInstruction') || 
                    'Qual das imagens abaixo você selecionou anteriormente para esta seção da história?'}
                </p>
            </div>

            <div className={styles.sectionText}>
                <h3>{t('evaluation.sectionTextLabel') || 'Texto da Seção:'}</h3>
                <p>{section.sectionText}</p>
            </div>

            <div className={styles.imagesGrid}>
                {shuffledImages.map((image, index) => (
                    <div
                        key={index}
                        className={`${styles.imageContainer} ${
                            selectedImage === image.url ? styles.selected : ''
                        }`}
                        onClick={() => handleImageSelect(image)}
                    >
                        <img
                            src={image.url}
                            alt={`Opção ${index + 1}`}
                            className={styles.image}
                            onError={(e) => {
                                // Fallback para placeholder se imagem não carregar
                                e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-size="14"%3EImagem %23' + (index + 1) + '%3C/text%3E%3C/svg%3E';
                            }}
                        />
                        <span className={styles.imageName}>{image.name}</span>
                    </div>
                ))}
            </div>

            <div className={styles.buttonContainer}>
                <button
                    onClick={handleSubmitAnswer}
                    className={styles.submitButton}
                    disabled={!selectedImage}
                >
                    {t('evaluation.nextQuestion') || 'Próxima Pergunta'}
                </button>
            </div>
        </div>
    );
};

export default ImageRecognitionQuestion;
