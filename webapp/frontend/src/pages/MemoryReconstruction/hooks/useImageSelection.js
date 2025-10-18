import { useState } from 'react';

const useImageSelection = () => {
    const [selectedImagesPerSection, setSelectedImagesPerSection] = useState({});

    const selectImage = (imageObject, sectionIndex) => {
        setSelectedImagesPerSection(prev => ({
            ...prev,
            [sectionIndex]: imageObject.url
        }));
    };

    const clearSelection = () => {
        setSelectedImagesPerSection({});
    };

    return {
        selectedImagesPerSection,
        selectImage,
        clearSelection
    };
};

export default useImageSelection;
