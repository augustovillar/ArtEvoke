import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export const useStoryGeneration = () => {
    const { t } = useTranslation('common');
    const [generateLoading, setGenerateLoading] = useState(false);
    const [responseText, setResponseText] = useState(null);

    const generateStory = async (selectedImages) => {
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

        try {
            const response = await fetch(`/api/generate-story`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    selectedImageIds: selectedImageIds,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setResponseText(data.text);
            return data.text;
        } catch (error) {
            console.error("There was a problem with the fetch operation:", error);
            setResponseText('Failed to generate story. Please try again.');
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