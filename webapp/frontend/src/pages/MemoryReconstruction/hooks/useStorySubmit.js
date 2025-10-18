import { useState } from 'react';

const useStorySubmit = () => {
    const [sectionsWithImages, setSectionsWithImages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [numImagesPerSection, setNumImagesPerSection] = useState(1);

    const submitStory = (storyText, language, dataset, segmentation, k = 1) => {
        setLoading(true);
        setSectionsWithImages([]);
        setNumImagesPerSection(k);

        fetch(`/api/select-images-per-section`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                story: storyText,
                language: language,
                dataset: dataset,
                segmentation: segmentation,
                k: k
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const processedSections = data.sections.map(sectionData => {
                const enrichedImages = sectionData.images.map(imageItem => {
                    return {
                        url: imageItem.image_url,
                        name: imageItem.art_name
                    };
                });
                return {
                    ...sectionData,
                    images: enrichedImages
                };
            });
            setSectionsWithImages(processedSections);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            setSectionsWithImages([]);
        })
        .finally(() => {
            setLoading(false);
        });
    };

    return {
        sectionsWithImages,
        loading,
        numImagesPerSection,
        submitStory
    };
};

export default useStorySubmit;
