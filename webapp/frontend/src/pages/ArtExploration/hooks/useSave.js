import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export const useSave = () => {
    const { t } = useTranslation('common');
    const [saveMessage, setSaveMessage] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [hasSaved, setHasSaved] = useState(false);

    const saveStory = async (responseText, selectedImages, dataset, language, storyData = null, sessionId = null) => {
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
            let endpoint = `/api/art/save`;
            if (sessionId) {
                endpoint += `?session_id=${sessionId}`;
            }

            const body = {
                story_generated: responseText,
                dataset: dataset,
                language: language,
                images_selected: selectedImages.map((img, index) => ({
                    id: img.id,
                    display_order: index + 1
                })),
            };

            if (storyData && storyData.events && Array.isArray(storyData.events)) {
                body.correct_option_0 = storyData.events[0] || null;
                body.correct_option_1 = storyData.events[1] || null;
                body.correct_option_2 = storyData.events[2] || null;
                body.correct_option_3 = storyData.events[3] || null;
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(body),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

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

