import { useState } from 'react';

export const useImageSelection = () => {
    const [selectedImages, setSelectedImages] = useState([]);

    const handleImageToggle = (imageToToggle) => {
        setSelectedImages(prevSelected => {
            const isSelected = prevSelected.some(img => img.url === imageToToggle.url);
            if (isSelected) {
                return prevSelected.filter(img => img.url !== imageToToggle.url);
            } else {
                return [...prevSelected, { 
                    url: imageToToggle.url, 
                    name: imageToToggle.name, 
                    dataset: imageToToggle.dataset 
                }];
            }
        });
    };

    const clearSelections = () => {
        setSelectedImages([]);
    };

    return {
        selectedImages,
        setSelectedImages,
        handleImageToggle,
        clearSelections
    };
};