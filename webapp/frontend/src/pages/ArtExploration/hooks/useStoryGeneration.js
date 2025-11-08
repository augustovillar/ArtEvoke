import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export const useStoryGeneration = () => {
    const { t } = useTranslation('common');
    const [generateLoading, setGenerateLoading] = useState(false);
    const [responseText, setResponseText] = useState(null);

    const generateStory = async (selectedImages, language = 'en') => {
        if (selectedImages.length === 0) {
            alert(t('artExploration.selectAtLeastOne'));
            return;
        }

        setGenerateLoading(true);
        setResponseText(null);

        const selectedImageIds = [];

        selectedImages.forEach(img => {
            if (img.id) {
                selectedImageIds.push(img.id);
            } else {
                console.warn(`Image with missing ID found. It will not be included in the generation request.`);
            }
        });

        // Normalize language: ensure it's 'en' or 'pt'
        const normalizedLanguage = language && typeof language === 'string' 
            ? language.split('-')[0].toLowerCase() 
            : 'en';
        
        // Validate language
        const validLanguage = (normalizedLanguage === 'en' || normalizedLanguage === 'pt') 
            ? normalizedLanguage 
            : 'en';

        try {
            const response = await fetch(`/api/art/generate-story`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    selectedImageIds: selectedImageIds,
                    language: validLanguage,
                }),
            });

            if (!response.ok) {
                throw new Error('Internal error');
            }

            const data = await response.json();
            setResponseText(data.text);
            return data;
        } catch (error) {
            console.error("There was a problem with the fetch operation:", error);
            const errorMessage = error.message || 'Failed to generate story. Please try again.';
            alert(errorMessage);
            setResponseText(null);
            throw error;
        } finally {
            setGenerateLoading(false);
        }
    };

    const copyToClipboard = async () => {
        if (responseText) {
            try {
                await navigator.clipboard.writeText(responseText);
                console.log('Text copied to clipboard!');
                return { success: true, message: t('artExploration.textCopied') };
            } catch (err) {
                console.error('Failed to copy text: ', err);
                return { success: false, message: t('artExploration.copyFailed') };
            }
        }
    };

    return {
        generateLoading,
        responseText,
        setResponseText,
        generateStory,
        copyToClipboard
    };
};