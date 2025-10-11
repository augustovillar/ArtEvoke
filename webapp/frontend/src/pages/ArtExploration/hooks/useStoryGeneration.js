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

        try {
            const response = await fetch(`/api/generate-story`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    selectedImagesByDataset: selectedImagesByDataset,
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