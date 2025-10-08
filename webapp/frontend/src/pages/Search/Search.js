// src/Search.js
import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import './Search.css';
import SpeechInput from '../../features/speech';
// import ReadAloudButton from './components/ReadAloudButton'; // Removed ReadAloudButton import
import { useReadAloud } from '../../contexts/ReadAloudContext'; // Import useReadAloud
import InterruptionModal from '../../components/interruptionModal';
import { INTERRUPTION_CONFIG } from '../../config/interruption.config';

const Search = () => {
    const { t } = useTranslation('common');
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud(); // Get registerContent from context

    const [storyText, setStoryText] = useState('');
    const [images, setImages] = useState([]); // This will hold images from the *current* search
    const [selectedImages, setSelectedImages] = useState([]); // This will hold *all* selected images across searches, with their dataset

    const [language, setLanguage] = useState('en');

    const [dataset, setDataset] = useState('wikiart'); // This refers to the dataset selected for the CURRENT search (lowercase value)

    const [submitLoading, setSubmitLoading] = useState(false);
    const [generateLoading, setGenerateLoading] = useState(false);

    const [responseText, setResponseText] = useState(null);
    const [saveMessage, setSaveMessage] = useState('');

    // Interruption states
    const [showInterruption, setShowInterruption] = useState(false);
    const [savedStoryData, setSavedStoryData] = useState(null);

    const location = useLocation();
    const navigate = useNavigate();

    // For testing, always show interruption. FUTURE: use location.state?.fromSession
    const shouldShowInterruption = true;

    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

    // Register content for read aloud when the component mounts or contentRef changes
    useEffect(() => {
        registerContent(contentRef, [
            t('search.description1'),
            t('search.description2')
        ]);
        return () => registerContent(null); // Cleanup on unmount
    }, [registerContent, t]);

    // Handle form submission to fetch images
    const handleSubmit = () => {
        setSubmitLoading(true);
        setResponseText(null);
        setImages([]); // Clear *only* the currently displayed images

        fetch(`/api/search-images`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                story: storyText,
                language: language,
                dataset: dataset
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const newImages = data.images.map(item => {
                const imageUrl = item.image_url; 
                const imageName = item.art_name;

                const imageDataset = typeof item === 'object' && item.dataset 
                                    ? item.dataset.toLowerCase()
                                    : dataset;
                return { url: imageUrl, name: imageName, dataset: imageDataset };
            });
            setImages(newImages); // Update only the currently displayed images
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            setImages([]);
        }).finally(() => {
            setSubmitLoading(false);
        });
    };

    // Handle image selection/deselection
    const handleImageToggle = (imageToToggle) => {
        setSelectedImages(prevSelected => {
            const isSelected = prevSelected.some(img => img.url === imageToToggle.url);
            if (isSelected) {
                return prevSelected.filter(img => img.url !== imageToToggle.url);
            } else {
                return [...prevSelected, { url: imageToToggle.url, name: imageToToggle.name, dataset: imageToToggle.dataset }];
            }
        });
    };

    // Handle story generation from selected images
    const handleGenerateStory = () => {
        if (selectedImages.length === 0) {
            alert(t('search.selectAtLeastOne'));
            return;
        }

        setGenerateLoading(true);
        setResponseText(null); // Clear previous story

        const selectedImagesByDataset = {};
        const allDatasets = ['wikiart', 'semart', 'ipiranga'];
        allDatasets.forEach(ds => {
            selectedImagesByDataset[ds] = [];
        });

        selectedImages.forEach(img => {
            if (selectedImagesByDataset[img.dataset]) {
                selectedImagesByDataset[img.dataset].push(img.url);
            } else {
                console.warn(`Image with unknown dataset '${img.dataset}' found. It will not be included in the generation request.`);
            }
        });

        fetch(`/api/generate-story`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                selectedImagesByDataset: selectedImagesByDataset,
            }),
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            // Apenas definir o texto gerado; a interrupção só será exibida quando o usuário salvar
            setResponseText(data.text);
        })
        .catch((error) => {
            console.error("There was a problem with the fetch operation:", error);
            setResponseText('Failed to generate story. Please try again.');
        })
        .finally(() => {
            setGenerateLoading(false);
        });
    };

    // Copy generated story text to clipboard
    const copyToClipboard = () => {
        if (responseText) {
            navigator.clipboard.writeText(responseText)
                .then(() => {
                    console.log('Text copied to clipboard!');
                    setSaveMessage(t('search.textCopied'));
                    setTimeout(() => setSaveMessage(''), 3000);
                })
                .catch(err => {
                    console.error('Failed to copy text: ', err);
                    setSaveMessage(t('search.copyFailed'));
                    setTimeout(() => setSaveMessage(''), 3000);
                });
        }
    }

    // Regenerate the story
    const handleRegenerateClick = () => {
        handleGenerateStory();
    };

    const handleSaveClick = () => {
        const token = localStorage.getItem('token');

        if (!token) {
            setSaveMessage(t('search.loginToSave'));
            setTimeout(() => setSaveMessage(''), 3000);
            return;
        }

        if (!responseText) {
            setSaveMessage(t('search.noStoryToSave'));
            setTimeout(() => setSaveMessage(''), 3000);
            return;
        }

        const selectedImagesByDatasetForSave = {};
        const allDatasets = ['wikiart', 'semart', 'ipiranga'];
        allDatasets.forEach(ds => {
            selectedImagesByDatasetForSave[ds] = [];
        });

        selectedImages.forEach(img => {
            if (selectedImagesByDatasetForSave[img.dataset]) {
                selectedImagesByDatasetForSave[img.dataset].push(img.url);
            }
        });


        fetch(`/api/save-story`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
                storyText: responseText,
                selectedImagesByDataset: selectedImagesByDatasetForSave,
            }),
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            setSaveMessage(t('search.storySaved'));
            setTimeout(() => setSaveMessage(''), 3000);

            // Após salvar com sucesso, verificar se deve mostrar interrupção
            const saveData = {
                storyText: responseText,
                selectedImages: selectedImages,
            };

            if (shouldShowInterruption) {
                setSavedStoryData(saveData);
                setShowInterruption(true);
            } else {
                handleProceedToNextStep(saveData);
            }
        })
        .catch((error) => {
            console.error('There was a problem saving the story:', error);
            setSaveMessage(t('search.saveFailed'));
            setTimeout(() => setSaveMessage(''), 3000);
        });
    };

    // Função chamada quando a interrupção é completada
    const handleInterruptionComplete = () => {
        setShowInterruption(false);
        handleProceedToNextStep(savedStoryData);
    };

    // Função para prosseguir para próxima etapa (preparado para futuras implementações)
    const handleProceedToNextStep = (data) => {
        console.log('Prosseguindo para avaliação (futuro) com:', data);
        // Futuro: navigate('/evaluation/memory-reconstruction', { state: { data } });
        alert('Interrupção concluída — futuramente irá para avaliação.');
    };

    const handleLanguageChange = (event) => {
        setLanguage(event.target.value);
    };

    const handleDatasetChange = (event) => {
        setDataset(event.target.value);
    };

    return (
        <div>
            <div className="content-box" ref={contentRef}>
                <h1>{t('search.title')}</h1>
                <p>
                    {t('search.description1')}
                    <br></br>
                    <br></br>
                    {t('search.description2')}
                    <br></br>
                    <br></br>
                    {t('search.description3')}
                </p>
                <ol className="instructions-list">
                    <li>{t('search.instruction1')}</li>
                    <li>{t('search.instruction2')}</li>
                </ol>
                {/* ReadAloudButton was here */}
            </div>
            <div className="content-box">
                <h1>{t('search.enterKeywords')}</h1>
                <div className="input-row">
                    <textarea
                        className="search-textbox"
                        placeholder={t('search.placeholder')}
                        value={storyText}
                        onChange={(e) => setStoryText(e.target.value)}
                    />
                    <div className="select-row">
                        <div className="select-group">
                            <label htmlFor="language-select-id" className="select-label">{t('search.selectLanguage')}</label>
                            <select
                                id="language-select-id"
                                className="language-select"
                                value={language}
                                onChange={handleLanguageChange}
                            >
                                <option value="en">English</option>
                                <option value="fr">French</option>
                                <option value="nl">Dutch</option>
                                <option value="es">Spanish</option>
                                <option value="pt">Portuguese</option>
                                <option value="de">German</option>
                            </select>
                        </div>
                        <div className="select-group">
                            <label htmlFor="dataset-select-id" className="select-label">{t('search.selectDataset')}</label>
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
                    </div>
                </div>
                <div className='input-buttons'>
                    <button className="submit-button" onClick={handleSubmit} disabled={submitLoading}>
                        {submitLoading ? t('search.searching') : t('search.submit')}
                    </button>
                    <SpeechInput onChange={setStoryText} initialValue={storyText} />
                </div>
            </div>

            {(images.length > 0 || selectedImages.length > 0) && (
                <div className="content-box">
                    <h1>{t('search.imageSelection')}</h1>
                    <p>{t('search.imageSelectionDesc')}</p>
                    <div className="images-grid">
                        {/* Display currently searched images */}
                        {images.map((image) => (
                            <div
                                key={`search-${image.url}`}
                                className={`image-container ${selectedImages.some(img => img.url === image.url) ? 'selected' : ''}`}
                                onClick={() => handleImageToggle(image)}
                            >
                                <img
                                    src={image.url}
                                    alt={t('search.generatedImageAlt', { name: image.name })}
                                    className="generated-image"
                                />
                                <span className="image-name">{image.name}</span>
                            </div>
                        ))}

                        {/* Display already selected images that are NOT in the current search results */}
                        {selectedImages.map((selectedImage) => {
                            const isAlreadyDisplayed = images.some(img => img.url === selectedImage.url);
                            if (!isAlreadyDisplayed) {
                                return (
                                    <div
                                        key={`selected-${selectedImage.url}`}
                                        className="image-container selected"
                                        onClick={() => handleImageToggle(selectedImage)}
                                    >
                                        <img
                                            src={selectedImage.url}
                                            alt={t('search.selectedImageAlt', { name: selectedImage.name })}
                                            className="generated-image"
                                        />
                                        <span className="image-name">{selectedImage.name}</span>
                                    </div>
                                );
                            }
                            return null;
                        })}

                    </div>
                    <div className="buttons-container">
                        <button
                            className="submit-button"
                            onClick={handleGenerateStory}
                            disabled={generateLoading || selectedImages.length === 0}
                        >
                            {generateLoading ? t('search.generatingStory') : t('search.generateStory', { count: selectedImages.length })}
                        </button>
                        <button
                            className="submit-button"
                            onClick={() => setSelectedImages([])}
                            disabled={selectedImages.length === 0}
                        >
                            {t('search.clearSelections')}
                        </button>
                    </div>
                </div>
            )}

            {/* Display response text */}
            {responseText && (
                <div id='generated-story' className="content-box">
                    <h1>{t('search.aiGeneratedStory')}</h1>
                    <p>{responseText}</p>
                    <div className="buttons-container">
                        <button className="submit-button" onClick={handleRegenerateClick} disabled={generateLoading}>{t('search.regenerateStory')}</button>
                        <button className="submit-button" onClick={copyToClipboard}>{t('search.copyText')}</button>
                        <button className="submit-button" onClick={handleSaveClick}>{t('search.saveToAccount')}</button>
                    </div>
                    {saveMessage && <p>{saveMessage}</p>}
                </div>
            )}

            {/* Modal de Interrupção */}
            <InterruptionModal
                isOpen={showInterruption}
                duration={INTERRUPTION_CONFIG.MEMORY_RECONSTRUCTION.duration}
                title={INTERRUPTION_CONFIG.MEMORY_RECONSTRUCTION.title}
                message={INTERRUPTION_CONFIG.MEMORY_RECONSTRUCTION.message}
                buttonText={INTERRUPTION_CONFIG.MEMORY_RECONSTRUCTION.buttonText}
                onComplete={handleInterruptionComplete}
            />
        </div>
    );
};

export default Search;