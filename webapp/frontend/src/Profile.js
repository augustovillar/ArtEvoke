import React, { useEffect, useState } from 'react';
import './Profile.css';

const Profile = () => {
    const [username, setUsername] = useState('');
    const [savedArtSearches, setSavedArtSearches] = useState([]);
    const [savedStoryGenerations, setSavedStoryGenerations] = useState([]);
    const [expandedItem, setExpandedItem] = useState(null);
    const [deleteMessage, setDeleteMessage] = useState('');

    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

    const fetchUserProfile = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const response = await fetch(`/api/retrieve-searches`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to fetch user profile');
            }

            const data = await response.json();
            setSavedArtSearches(data.savedArtSearches || []);
            setSavedStoryGenerations(data.savedStoryGenerations || []);
        } catch (error) {
            console.error('Error fetching profile:', error);
        }
    };

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            const user = JSON.parse(storedUser);
            setUsername(user.username);
        }

        fetchUserProfile();
    }, []);

    const handleItemClick = (item) => {
        setExpandedItem(item);
        setDeleteMessage('');
    };

    const closeModal = () => {
        setExpandedItem(null);
        setDeleteMessage('');
    };

    const handleDeleteClick = async () => {
        if (!expandedItem || !expandedItem._id) {
            console.error('No item or ID to delete.');
            return;
        }

        const token = localStorage.getItem('token');
        if (!token) {
            setDeleteMessage('Please log in to delete.');
            return;
        }

        let deleteEndpoint = '';
        if (expandedItem.hasOwnProperty('images')) {
            // It's a saved story generation
            deleteEndpoint = `/api/delete-generation/${expandedItem._id}`;
        } else if (expandedItem.hasOwnProperty('selectedImagesByDataset')) {
            // It's a saved art search
            deleteEndpoint = `/api/delete-art-search/${expandedItem._id}`;
        } else {
            console.error('Unknown item type for deletion.');
            return;
        }

        try {
            const response = await fetch(deleteEndpoint, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                setDeleteMessage(errorData.message || 'Failed to delete item.');
                console.error('Error deleting item:', errorData);
                return;
            }

            setDeleteMessage('Item deleted successfully.');
            fetchUserProfile();
            closeModal();
        } catch (error) {
            console.error('Error deleting item:', error);
            setDeleteMessage('Failed to delete item. Please try again.');
        }
    };


    return (
        <div>
            <div className="content-box">
                <h1>Welcome to your dashboard, {username}!</h1>
                <p>You can check the history of your created stories or art pieces.</p>
            </div>

            <div className="content-box">
                <h1>Story Generation History</h1>
                <div className="story-list">
                    {savedStoryGenerations.length > 0 ? (
                        savedStoryGenerations.map((story, index) => (
                            <div
                                key={story._id || index}
                                className="story-box"
                                onClick={() => handleItemClick(story)}
                            >
                                <h3><strong>Date:</strong> {new Date(story.dateAdded).toLocaleString()}</h3>
                                <p>{story.text.substring(0, 50)}...</p>
                            </div>
                        ))
                    ) : (
                        <p>No saved stories yet.</p>
                    )}
                </div>
            </div>

            <div className="content-box">
                <h1>Art Search History</h1>
                <div className="story-list">
                    {savedArtSearches.length > 0 ? (
                        savedArtSearches.map((search, index) => (
                            <div
                                key={search._id || index}
                                className="story-box"
                                onClick={() => handleItemClick(search)}
                            >
                                <h3><strong>Date:</strong> {new Date(search.dateAdded).toLocaleString()}</h3>
                                <p>{search.text.substring(0, 50)}...</p>
                            </div>
                        ))
                    ) : (
                        <p>No saved art searches yet.</p>
                    )}
                </div>
            </div>

            {expandedItem && (
                <div className="modal-history">
                    <div className="modal-history-content">
                        <span className="history-close-button" onClick={closeModal}>&times;</span>
                        <h3><strong>Date:</strong> {new Date(expandedItem.dateAdded).toLocaleString()}</h3>
                        <p>{expandedItem.text}</p>
                        {expandedItem.hasOwnProperty('images') && Array.isArray(expandedItem.images) && expandedItem.images.length > 0 ? (
                            // This is for savedStoryGenerations (flat list of images)
                            <div className="modal-images-grid">
                                {expandedItem.images.map((imageUrl, index) => (
                                    <img
                                        key={index}
                                        src={imageUrl}
                                        alt={`Story Image ${index + 1}`}
                                        className="modal-history-image"
                                    />
                                ))}
                            </div>
                        ) : expandedItem.hasOwnProperty('selectedImagesByDataset') && expandedItem.selectedImagesByDataset ? (
                            // This is for savedArtSearches (structured images by dataset)
                            <div className="modal-images-grid">
                                {Object.entries(expandedItem.selectedImagesByDataset).map(([datasetName, urls]) => (
                                    urls.length > 0 && (
                                        <div key={datasetName} className="dataset-images-section">
                                            <h4>{datasetName.charAt(0).toUpperCase() + datasetName.slice(1)} Images:</h4>
                                            {urls.map((imageUrl, index) => (
                                                <img
                                                    key={`${datasetName}-${index}`}
                                                    src={imageUrl}
                                                    alt={`${datasetName} Image ${index + 1}`}
                                                    className="modal-history-image"
                                                />
                                            ))}
                                        </div>
                                    )
                                ))}
                            </div>
                        ) : null}

                        <div className="modal-actions">
                            <button className="delete-button" onClick={handleDeleteClick}>Delete</button>
                            {deleteMessage && <p className="delete-message">{deleteMessage}</p>}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Profile;