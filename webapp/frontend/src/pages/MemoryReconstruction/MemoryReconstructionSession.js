import React, { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './MemoryReconstruction.css';
import { useReadAloud } from '../../contexts/ReadAloudContext';
import InterruptionModal from '../../components/interruptionModal';
import { INTERRUPTION_CONFIG } from '../../config/interruption.config';

import InstructionsSection from './components/InstructionsSection';
import StoryInputForm from './components/StoryInputForm';
import ImageSelectionGrid from './components/ImageSelectionGrid';

import useStorySubmit from './hooks/useStorySubmit';
import useImageSelection from './hooks/useImageSelection';
import useSave from './hooks/useSave';

const MemoryReconstructionSession = () => {
    const { sessionId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud();
    const { t, i18n } = useTranslation('common');

    const [storyText, setStoryText] = useState('');
    const [language, setLanguage] = useState('en');
    const [dataset, setDataset] = useState('wikiart');
    const [segmentation, setSegmentation] = useState('conservative');
    const [showInterruption, setShowInterruption] = useState(false);
    const [interruptionTime, setInterruptionTime] = useState(10);
    const [loadingSession, setLoadingSession] = useState(false);

    useEffect(() => {
        const currentLang = i18n.language.split('-')[0];
        if (currentLang === 'en' || currentLang === 'pt') {
            setLanguage(currentLang);
        }
    }, [i18n.language]);

    const { 
        sectionsWithImages, 
        loading, 
        submitStory 
    } = useStorySubmit();

    const { 
        selectedImagesPerSection, 
        selectImage, 
        clearSelection 
    } = useImageSelection();
    
    const handleImageSelect = (imageObject, sectionIndex) => {
        selectImage(imageObject, sectionIndex);
        resetSaveState();
    };

    const { 
        saveMessage,
        sectionIds,
        isSaving,
        hasSaved,
        saveStory,
        resetSaveState
    } = useSave();

    useEffect(() => {
        const loadSessionData = async () => {
            if (!sessionId) return;

            setLoadingSession(true);
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`/api/sessions/${sessionId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    setInterruptionTime(data.interruption_time || 10);
                }
            } catch (error) {
                console.error('Error loading session data:', error);
            } finally {
                setLoadingSession(false);
            }
        };

        loadSessionData();
    }, [sessionId, navigate, location.state]);

    useEffect(() => {
        registerContent(contentRef, [
            "In the box below, you can enter text, or click a button to speak the words instead of typing.",
            "To the right of the text box, you can select the language for processing the story.",
            "Finally, there is a submit button to click once you are done inputting the text."
        ]);
        return () => registerContent(null);
    }, [registerContent]);

    const handleSubmit = () => {
        clearSelection();
        resetSaveState();
        submitStory(storyText, language, dataset, segmentation, 6);
    };

    const handleContinue = async () => {
        await handleSave();
        setShowInterruption(true);
    };

    const handleSave = async () => {
        await saveStory(
            storyText,
            selectedImagesPerSection,
            sectionsWithImages,
            language,
            dataset,
            segmentation,
            sessionId
        );
    };

    const handleClearSelection = () => {
        if (window.confirm(t('memoryReconstruction.confirmClearSelection'))) {
            clearSelection();
        }
    };

    const handleInterruptionComplete = () => {
        setShowInterruption(false);
        handleProceedToNextStep();
    };

    const handleProceedToNextStep = async () => {
        try {
            // Create evaluation before navigating
            const token = localStorage.getItem('token');
            const createResponse = await fetch(
                `/api/evaluation/create?session_id=${sessionId}`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            if (!createResponse.ok) {
                throw new Error('Failed to create evaluation');
            }

            const createData = await createResponse.json();
            console.log('Evaluation created:', createData.id);

            // Use section IDs returned from save
            const sessionData = {
                sessionId,
                mode: 'session',
                phase1: {
                    story: storyText,
                    language,
                    dataset,
                    segmentation,
                    sections: sectionsWithImages.map((section, index) => ({
                        sectionId: sectionIds[index], // Use real section ID from save response
                        sectionText: section.section,
                        imagesShown: section.images.map(img => ({
                            url: img.url,
                            name: img.name,
                            id: img.id
                        })),
                        selectedImage: {
                            url: selectedImagesPerSection[index],
                            name: section.images.find(img => img.url === selectedImagesPerSection[index])?.name,
                            id: section.images.find(img => img.url === selectedImagesPerSection[index])?.id
                        }
                    }))
                },
                interruption: {
                    duration: interruptionTime,
                    completed: true
                },
                timestamp: new Date().toISOString()
            };

            navigate(`/sessions/${sessionId}/memory-reconstruction/evaluation`, {
                state: {
                    sessionData
                }
            });
        } catch (error) {
            console.error('Error creating evaluation:', error);
            alert('Erro ao iniciar avaliação. Tente novamente.');
        }
    };

    if (loadingSession) {
        return <div className="sessions-loading">{t('common.loading')}</div>;
    }

    return (
        <div>
            <div className="session-mode-banner">
                <div className="banner-icon">🎯</div>
                <div className="banner-content">
                    <h3>{t('memoryReconstruction.sessionModeBanner.title')}</h3>
                    <p>{t('memoryReconstruction.sessionModeBanner.description')}</p>
                </div>
            </div>

            <div ref={contentRef}>
                <InstructionsSection />

                <StoryInputForm
                    storyText={storyText}
                    onStoryTextChange={setStoryText}
                    language={language}
                    onLanguageChange={(e) => setLanguage(e.target.value)}
                    dataset={dataset}
                    onDatasetChange={(e) => setDataset(e.target.value)}
                    segmentation={segmentation}
                    onSegmentationChange={(e) => setSegmentation(e.target.value)}
                    onSubmit={handleSubmit}
                    loading={loading}
                />

                <ImageSelectionGrid
                    sectionsWithImages={sectionsWithImages}
                    selectedImagesPerSection={selectedImagesPerSection}
                    onImageClick={handleImageSelect}
                    onInSession={handleContinue}
                    onClearSelection={handleClearSelection}
                    isSessionMode={true}
                    loading={loading}
                    isSaving={isSaving}
                    hasSaved={hasSaved}
                    storyText={storyText}
                    saveMessage={saveMessage}
                />
            </div>

            <InterruptionModal
                isOpen={showInterruption}
                duration={interruptionTime}
                translationKey={INTERRUPTION_CONFIG.MEMORY_RECONSTRUCTION.translationKey}
                mode="memory-reconstruction"
                onComplete={handleInterruptionComplete}
            />
        </div>
    );
};

export default MemoryReconstructionSession;
