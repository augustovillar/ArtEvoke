import { useState } from 'react';

export const useImageSelection = () => {
    const [selectedImages, setSelectedImages] = useState([]);

    const handleImageToggle = (imageToToggle) => {
        setSelectedImages(prevSelected => {
            const isSelected = prevSelected.some(img => img.id === imageToToggle.id);
            if (isSelected) {
                return prevSelected.filter(img => img.id !== imageToToggle.id);
            } else {
                return [...prevSelected, { 
                    id: imageToToggle.id,
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