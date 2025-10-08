import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export const useStorySave = () => {
    const { t } = useTranslation('common');
    const [saveMessage, setSaveMessage] = useState('');

    const saveStory = async (responseText, selectedImages) => {
        const token = localStorage.getItem('token');

        if (!token) {
            const message = t('artExploration.loginToSave');
            setSaveMessage(message);
            setTimeout(() => setSaveMessage(''), 3000);
            return { success: false, message };
        }

        if (!responseText) {
            const message = t('artExploration.noStoryToSave');
            setSaveMessage(message);
            setTimeout(() => setSaveMessage(''), 3000);
            return { success: false, message };
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

        try {
            const response = await fetch(`/api/save-story`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    storyText: responseText,
                    selectedImagesByDataset: selectedImagesByDatasetForSave,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const successMessage = t('artExploration.storySaved');
            setSaveMessage(successMessage);
            setTimeout(() => setSaveMessage(''), 3000);

            const saveData = {
                storyText: responseText,
                selectedImages: selectedImages,
            };

            return { success: true, message: successMessage, data: saveData };
        } catch (error) {
            console.error('There was a problem saving the story:', error);
            const errorMessage = t('artExploration.saveFailed');
            setSaveMessage(errorMessage);
            setTimeout(() => setSaveMessage(''), 3000);
            return { success: false, message: errorMessage, error };
        }
    };

    return {
        saveMessage,
        setSaveMessage,
        saveStory
    };
};