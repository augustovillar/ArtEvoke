import { useState } from 'react';

export const useImageSearch = () => {
    const [images, setImages] = useState([]);
    const [submitLoading, setSubmitLoading] = useState(false);

    const searchImages = async (storyText, language, dataset) => {
        setSubmitLoading(true);
        setImages([]);

        try {
            const response = await fetch(`/api/search-images`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    story: storyText,
                    language: language,
                    dataset: dataset
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const newImages = data.images.map(item => {
                const imageUrl = item.image_url; 
                const imageName = item.art_name;
                const imageDataset = typeof item === 'object' && item.dataset 
                                    ? item.dataset.toLowerCase()
                                    : dataset;
                return {  
                    url: imageUrl, 
                    name: imageName, 
                    dataset: imageDataset,
                    // Add new rich metadata
                    id: item.id,
                    title: item.title,
                    artist: item.artist,
                    year: item.year,
                    description: item.description,
                    technique: item.technique,
                    width: item.width,
                    height: item.height
                };
            });
            
            setImages(newImages);
            return newImages;
        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
            setImages([]);
            throw error;
        } finally {
            setSubmitLoading(false);
        }
    };

    return {
        images,
        setImages,
        submitLoading,
        searchImages
    };
};