import { useState } from 'react';
import { useTranslation } from 'react-i18next';

const useStoryOutOfSessionSave = () => {
    const { t } = useTranslation();
    const [saveMessage, setSaveMessage] = useState('');
    const [savedStoryData, setSavedStoryData] = useState(null);

    const saveOutOfSessionStory = (
        storyText,
        selectedImagesPerSection,
        sectionsWithImages,
        language,
        dataset,
        segmentation,
        // out-of-session save only
    ) => {
        const token = localStorage.getItem('token');
        if (!token) {
            setSaveMessage(t('memoryReconstruction.messages.loginRequired'));
            setTimeout(() => setSaveMessage(''), 3000);
            return;
        }

        const allSectionsCovered = sectionsWithImages.every((_, index) => 
            selectedImagesPerSection.hasOwnProperty(index)
        );

        if (!allSectionsCovered) {
            setSaveMessage(t('memoryReconstruction.messages.selectAllImages'));
            setTimeout(() => setSaveMessage(''), 4000);
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

        fetch(`/api/memory/save`, {
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
            setSaveMessage(t('memoryReconstruction.messages.savedSuccessfully'));
            setTimeout(() => setSaveMessage(''), 3000);
            setSavedStoryData(saveData);
        })
        .catch(error => {
            console.error('Error saving:', error);
            setSaveMessage(t('memoryReconstruction.messages.saveFailed'));
            setTimeout(() => setSaveMessage(''), 3000);
        });
    };

    return {
        saveMessage,
        savedStoryData,
        saveOutOfSessionStory
    };
};

export default useStoryOutOfSessionSave;
