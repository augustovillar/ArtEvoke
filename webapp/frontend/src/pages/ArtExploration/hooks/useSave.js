import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export const useSave = () => {
    const { t } = useTranslation('common');
    const [saveMessage, setSaveMessage] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [hasSaved, setHasSaved] = useState(false);

    const saveStory = async (responseText, selectedImages, dataset, language, artExplorationId = null) => {
        // Prevent multiple saves - set saving state immediately
        if (isSaving) return { success: false, message: 'Already saving...' };
        
        setIsSaving(true);

        const token = localStorage.getItem('token');

        if (!token) {
            const message = t('artExploration.loginToSave');
            setSaveMessage(message);
            setTimeout(() => setSaveMessage(''), 3000);
            setIsSaving(false);
            return { success: false, message };
        }

        if (!responseText) {
            const message = t('artExploration.noStoryToSave');
            setSaveMessage(message);
            setTimeout(() => setSaveMessage(''), 3000);
            setIsSaving(false);
            return { success: false, message };
        }

        try {
            // Build endpoint with optional artExplorationId query param
            let endpoint = `/api/art/save`;
            if (artExplorationId) {
                endpoint += `?art_exploration_id=${artExplorationId}`;
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    story_generated: responseText,
                    dataset: dataset,
                    language: language,
                    images_selected: selectedImages.map((img, index) => ({
                        id: img.id,
                        display_order: index + 1
                    })),
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            await response.json();
            const successMessage = t('artExploration.storySaved');
            setSaveMessage(successMessage);
            setTimeout(() => setSaveMessage(''), 3000);

            const saveData = {
                storyText: responseText,
                selectedImages: selectedImages,
            };

            setHasSaved(true); // Mark as saved successfully
            return { success: true, message: successMessage, data: saveData };
        } catch (error) {
            console.error('There was a problem saving the story:', error);
            const errorMessage = t('artExploration.saveFailed');
            setSaveMessage(errorMessage);
            setTimeout(() => setSaveMessage(''), 3000);
            return { success: false, message: errorMessage, error };
        } finally {
            setIsSaving(false);
        }
    };

    const resetSaveState = () => {
        setHasSaved(false);
    };

    return {
        saveMessage,
        setSaveMessage,
        isSaving,
        hasSaved,
        saveStory,
        resetSaveState
    };
};

