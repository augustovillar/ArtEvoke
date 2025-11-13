import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionReadAloudButton } from '../../../../components/ui';
import styles from './ImageRecognitionQuestion.module.css';

const ImageRecognitionQuestion = ({ section, sectionNumber, totalSections, onAnswer }) => {
    const { t } = useTranslation();
    const [selectedImage, setSelectedImage] = useState(null);
    const [startTime] = useState(Date.now());
    const [shuffledImages, setShuffledImages] = useState([]);
    const [distractor0, setDistractor0] = useState(null);
    const [distractor1, setDistractor1] = useState(null);
    const [loadingDistractors, setLoadingDistractors] = useState(true);

    useEffect(() => {
        const fetchDistractors = async () => {
            try {
                setLoadingDistractors(true);
                const token = localStorage.getItem('token');
                
                const response = await fetch(
                    `/api/evaluation/memory-reconstruction/distractor-images/${section.sectionId}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    }
                );

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                const distractors = data.distractors.map((d, index) => ({
                    id: d.id,
                    url: d.url,
                    name: d.title || `Distractor ${index + 1}`,
                    isDistractor: true
                }));

                setDistractor0(distractors[0]);
                setDistractor1(distractors[1]);

                // Criar array com todas as imagens mostradas + distratores
                const allImages = [
                    ...(section.imagesShown || []).map(img => ({
                        ...img,
                        isDistractor: false,
                        isCorrect: img.id === section.selectedImage?.id
                    })),
                    ...distractors
                ];

                // Embaralhar as imagens
                const shuffled = allImages.sort(() => Math.random() - 0.5);
                setShuffledImages(shuffled);
            } catch (error) {
                console.error('Error fetching distractors:', error);
                alert(t('evaluation.errorLoadingDistractors') || 'Erro ao carregar imagens distratoras.');
            } finally {
                setLoadingDistractors(false);
            }
        };

        fetchDistractors();
    }, [section, t]);

    const handleImageSelect = (image) => {
        setSelectedImage(image);
    };

    const handleSubmitAnswer = () => {
        if (!selectedImage) {
            alert(t('evaluation.pleaseSelectImage') || 'Por favor, selecione uma imagem antes de continuar.');
            return;
        }

        const timeSpent = Date.now() - startTime;

        onAnswer(
            section.sectionId,
            selectedImage.id,
            distractor0.id,
            distractor1.id,
            timeSpent
        );
    };

    if (loadingDistractors) {
        return (
            <div className={styles.container}>
                <div className={styles.loading}>
                    {t('evaluation.loadingQuestion') || 'Carregando pergunta...'}
                </div>
            </div>
        );
    }

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
                            selectedImage?.id === image.id ? styles.selected : ''
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
