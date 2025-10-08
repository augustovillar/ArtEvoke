import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './Story.css';
import SpeechInput from '../../features/speech';
import { useReadAloud } from '../../contexts/ReadAloudContext';
import { useTranslation } from 'react-i18next';
import InterruptionModal from '../../components/interruptionModal';
import { INTERRUPTION_CONFIG } from '../../config/interruption.config';

const Story = () => {
    const { t } = useTranslation();
    const location = useLocation();
    const navigate = useNavigate();
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud();

    const [storyText, setStoryText] = useState('');
    const [sectionsWithImages, setSectionsWithImages] = useState([]);
    const [selectedImagesPerSection, setSelectedImagesPerSection] = useState({});
    const [saveMessage, setSaveMessage] = useState('');

    // Estados para interrupção
    const [showInterruption, setShowInterruption] = useState(false);
    const [savedStoryData, setSavedStoryData] = useState(null);

    const [language, setLanguage] = useState('en');
    const [dataset, setDataset] = useState('wikiart');
    const [segmentation, setSegmentation] = useState('conservative');
    const [numImagesPerSection, setNumImagesPerSection] = useState(1);

    const [loading, setLoading] = useState(false);

    // Verifica se deve mostrar interrupção 
    // PARA TESTE: deixado como true para sempre mostrar a interrupção
    // FUTURO: quando vier das sessões, trocar por: location.state?.fromSession || false
    const shouldShowInterruption = true;

    // const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

    useEffect(() => {
        registerContent(contentRef, [
            "In the box below, you can enter text, or click a button to speak the words instead of typing.",
            "To the right of the text box, you can select the language for processing the story.",
            "Finally, there is a submit button to click once you are done inputting the text."
        ]);
        return () => registerContent(null);
    }, [registerContent]);

    const handleSubmit = (k = numImagesPerSection) => {
        setLoading(true);
        setSectionsWithImages([]);
        setSelectedImagesPerSection({});
        setNumImagesPerSection(k);

        fetch(`/api/select-images-per-section`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                story: storyText,
                language: language,
                dataset: dataset,
                segmentation: segmentation,
                k: k
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const processedSections = data.sections.map(sectionData => {
                const enrichedImages = sectionData.images.map(imageItem => {
                    return {
                        url: imageItem.image_url,
                        name: imageItem.art_name
                    };
                });
                return {
                    ...sectionData,
                    images: enrichedImages
                };
            });
            setSectionsWithImages(processedSections);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            setSectionsWithImages([]);
        }).finally(() => {
            setLoading(false);
        });
    };

    const handleImageClick = (imageObject, sectionIndex) => {
        setSelectedImagesPerSection(prev => ({ ...prev, [sectionIndex]: imageObject.url }));
    };

    const handleSaveClick = () => {
        const token = localStorage.getItem('token');
        if (!token) {
            setSaveMessage(t('story.messages.loginRequired'));
            setTimeout(() => setSaveMessage(''), 3000);
            return;
        }

        const allSectionsCovered = sectionsWithImages.every((_, index) => selectedImagesPerSection.hasOwnProperty(index));

        if (!allSectionsCovered) {
             setSaveMessage(t('story.messages.selectAllImages'));
             setTimeout(() => setSaveMessage(''), 4000);
             return;
        }

        const saveData = {
            generatedStory: storyText,
            selectedImages: Object.values(selectedImagesPerSection),
            language: language,
            dataset: dataset,
            segmentation: segmentation,
        };

        fetch(`/api/save-generation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(saveData),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            setSaveMessage(t('story.messages.savedSuccessfully'));
            setTimeout(() => setSaveMessage(''), 3000);
            
            // Após salvar com sucesso, verificar se deve mostrar interrupção
            if (shouldShowInterruption) {
                setSavedStoryData(saveData);
                setShowInterruption(true);
            } else {
                // Se não tem interrupção, vai direto para próxima etapa (futura)
                handleProceedToNextStep(saveData);
            }
        })
        .catch(error => {
            console.error('Error saving:', error);
            setSaveMessage(t('story.messages.saveFailed'));
            setTimeout(() => setSaveMessage(''), 3000);
        });
    };

    const handleRequestMoreImages = () => {
        handleSubmit(5);
    };

    // Função chamada quando a interrupção é completada
    const handleInterruptionComplete = () => {
        setShowInterruption(false);
        handleProceedToNextStep(savedStoryData);
    };

    // Função para prosseguir para próxima etapa (preparado para futuras implementações)
    const handleProceedToNextStep = (storyData) => {
        console.log("Prosseguindo para próxima etapa (avaliação futura)...");
        console.log("Story Data:", storyData);
        
        // Futuro: navigate('/evaluation/art-exploration', { 
        //     state: { 
        //         storyData,
        //         mode: 'art_exploration'
        //     } 
        // });
        
        // Por enquanto, só mostra uma mensagem
        alert("Etapa concluída! (Futuramente será redirecionado para avaliação)");
    };

    const handleLanguageChange = (event) => {
        setLanguage(event.target.value);
    };

    const handleDatasetChange = (event) => {
        setDataset(event.target.value);
    };

    const handleSegmentationChange = (event) => {
        setSegmentation(event.target.value);
    };

    return (
        <div>
            <div className="content-box" ref={contentRef}>
                <h1>{t('story.pageTitle')}</h1>
                <p>
                    {t('story.description')}
                    <br></br>
                    <br></br>
                    {t('story.optionsIntro')}
                </p>
                <ol className="instructions-list">
                    <li>{t('story.instructions.language')}</li>
                    <li>{t('story.instructions.dataset')}</li>
                    <li>{t('story.instructions.segmentation')}</li>
                </ol>
            </div>
            <div className="content-box">
                <h1>{t('story.writeStoryTitle')}</h1>
                <div className="input-row">
                    <textarea
                        className="story-textbox"
                        placeholder={t('story.textareaPlaceholder')}
                        value={storyText}
                        onChange={(e) => setStoryText(e.target.value)}
                    />
                    <div className="select-row">
                        <div className="select-group">
                            <label htmlFor="language-select-id" className="select-label">{t('story.selectLanguage')}</label>
                            <select
                                id="language-select-id"
                                className="language-select"
                                value={language}
                                onChange={handleLanguageChange}
                            >
                                <option value="en">{t('story.languages.en')}</option>
                                <option value="fr">{t('story.languages.fr')}</option>
                                <option value="nl">{t('story.languages.nl')}</option>
                                <option value="es">{t('story.languages.es')}</option>
                                <option value="pt">{t('story.languages.pt')}</option>
                                <option value="de">{t('story.languages.de')}</option>
                            </select>
                        </div>
                        <div className="select-group">
                            <label htmlFor="dataset-select-id" className="select-label">{t('story.selectDataset')}</label>
                            <select
                                id="dataset-select-id"
                                className="language-select"
                                value={dataset}
                                onChange={handleDatasetChange}
                            >
                                <option value="wikiart">Wikiart</option>
                                <option value="semart">SemArt</option>
                                <option value="ipiranga">Ipiranga</option>
                            </select>
                        </div>
                        <div className="select-group">
                            <label htmlFor="segmentation-select-id" className="select-label">{t('story.imageSelection')}</label>
                            <select
                                id="segmentation-select-id"
                                className="language-select"
                                value={segmentation}
                                onChange={handleSegmentationChange}
                            >
                                <option value="conservative">{t('story.segmentationOptions.conservative')}</option>
                                <option value="broader">{t('story.segmentationOptions.broader')}</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div className='input-buttons'>
                    <button className="submit-button" onClick={() => handleSubmit(1)} disabled={loading || !storyText.trim()}>
                        {loading ? t('story.searching') : t('story.submitButton')}
                    </button>
                    <SpeechInput onChange={setStoryText} initialValue={storyText} />
                </div>
            </div>

            {sectionsWithImages.length > 0 && (
                <div className="content-box">
                    <h1>{t('story.chooseImagesTitle')}</h1>
                    {sectionsWithImages.map((sectionData, sectionIndex) => (
                        <div key={sectionIndex} className="section-images-container">
                            {sectionData.section && <p><strong>{t('story.sectionLabel')}</strong> {sectionData.section}</p>}
                            <div className="images-grid">
                                {sectionData.images.map((imageItem, imageIndex) => (
                                    <div
                                        key={`${sectionIndex}-${imageIndex}`}
                                        className={`image-container ${selectedImagesPerSection[sectionIndex] === imageItem.url ? 'selected' : ''}`}
                                        onClick={() => handleImageClick(imageItem, sectionIndex)}
                                    >
                                        <img
                                            src={imageItem.url}
                                            alt={t('story.imageAlt', { sectionIndex: sectionIndex + 1, imageIndex: imageIndex + 1 })}
                                            className="generated-image"
                                        />
                                        <span className="image-name">{imageItem.name}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                    <div className="buttons-container">
                        {numImagesPerSection === 1 && (
                            <button
                                className="submit-button"
                                onClick={handleRequestMoreImages}
                                disabled={loading || !storyText.trim()}
                            >
                                {t('story.showMoreImages')}
                            </button>
                        )}
                        <button
                            className="submit-button"
                            onClick={handleSaveClick}
                            disabled={loading || Object.keys(selectedImagesPerSection).length !== sectionsWithImages.length}
                        >
                            {t('story.saveStory')}
                        </button>
                    </div>
                    {saveMessage && <p>{saveMessage}</p>}
                </div>
            )}

            {/* Modal de Interrupção */}
            <InterruptionModal
                isOpen={showInterruption}
                duration={INTERRUPTION_CONFIG.ART_EXPLORATION.duration}
                title={INTERRUPTION_CONFIG.ART_EXPLORATION.title}
                message={INTERRUPTION_CONFIG.ART_EXPLORATION.message}
                buttonText={INTERRUPTION_CONFIG.ART_EXPLORATION.buttonText}
                onComplete={handleInterruptionComplete}
            />
        </div>
    );
};

export default Story;