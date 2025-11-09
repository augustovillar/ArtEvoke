import { useState } from 'react';
import { useTranslation } from 'react-i18next';

const useSave = () => {
    const { t } = useTranslation();
    const [saveMessage, setSaveMessage] = useState('');
    const [savedStoryData, setSavedStoryData] = useState(null);
    const [isSaving, setIsSaving] = useState(false);
    const [hasSaved, setHasSaved] = useState(false);

    const saveStory = async (
        storyText,
        selectedImagesPerSection,
        sectionsWithImages,
        language,
        dataset,
        segmentation,
        sessionId = null
    ) => {
        if (isSaving) return;
        
        setIsSaving(true);

        const token = localStorage.getItem('token');
        if (!token) {
            setSaveMessage(t('memoryReconstruction.messages.loginRequired'));
            setTimeout(() => setSaveMessage(''), 3000);
            setIsSaving(false);
            return;
        }

        const allSectionsCovered = sectionsWithImages.every((_, index) => 
            selectedImagesPerSection.hasOwnProperty(index)
        );

        if (!allSectionsCovered) {
            setSaveMessage(t('memoryReconstruction.messages.selectAllImages'));
            setTimeout(() => setSaveMessage(''), 4000);
            setIsSaving(false);
            return;
        }

        const saveData = {
            story: storyText,
            dataset: dataset,
            language: language,
            segmentation_strategy: segmentation,
            sections: sectionsWithImages.map((sectionData, index) => ({
                section_content: sectionData.section,
                image1_id: sectionData.images[0]?.id || null,
                image2_id: sectionData.images[1]?.id || null,
                image3_id: sectionData.images[2]?.id || null,
                image4_id: sectionData.images[3]?.id || null,
                image5_id: sectionData.images[4]?.id || null,
                image6_id: sectionData.images[5]?.id || null,
                fav_image_id: selectedImagesPerSection[index] ? 
                    sectionData.images.find(img => img.url === selectedImagesPerSection[index])?.id || null : null
            }))
        };
        try {
            const url = sessionId 
                ? `/api/memory/save?session_id=${sessionId}`
                : `/api/memory/save`;
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(saveData),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            await response.json();
            setSaveMessage(t('memoryReconstruction.messages.savedSuccessfully'));
            setTimeout(() => setSaveMessage(''), 3000);
            setSavedStoryData(saveData);
            setHasSaved(true);
        } catch (error) {
            console.error('Error saving:', error);
            setSaveMessage(t('memoryReconstruction.messages.saveFailed'));
            setTimeout(() => setSaveMessage(''), 3000);
        } finally {
            setIsSaving(false);
        }
    };

    const resetSaveState = () => {
        setHasSaved(false);
    };

    return {
        saveMessage,
        savedStoryData,
        isSaving,
        hasSaved,
        saveStory,
        resetSaveState
    };
};

export default useSave;

