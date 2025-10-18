import { useState } from 'react';
import { useTranslation } from 'react-i18next';

const useStorySave = () => {
    const { t } = useTranslation();
    const [saveMessage, setSaveMessage] = useState('');
    const [savedStoryData, setSavedStoryData] = useState(null);

    const saveStory = (
        storyText,
        selectedImagesPerSection,
        sectionsWithImages,
        language,
        dataset,
        segmentation,
        shouldShowInterruption,
        onInterruptionShow
    ) => {
        const token = localStorage.getItem('token');
        if (!token) {
            setSaveMessage(t('story.messages.loginRequired'));
            setTimeout(() => setSaveMessage(''), 3000);
            return;
        }

        const allSectionsCovered = sectionsWithImages.every((_, index) => 
            selectedImagesPerSection.hasOwnProperty(index)
        );

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
            
            if (shouldShowInterruption) {
                setSavedStoryData(saveData);
                onInterruptionShow(saveData);
            }
        })
        .catch(error => {
            console.error('Error saving:', error);
            setSaveMessage(t('story.messages.saveFailed'));
            setTimeout(() => setSaveMessage(''), 3000);
        });
    };

    return {
        saveMessage,
        savedStoryData,
        saveStory
    };
};

export default useStorySave;
