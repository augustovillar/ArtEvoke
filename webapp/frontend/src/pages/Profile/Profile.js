import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts';
import './Profile.css';

const Profile = () => {
    const { t } = useTranslation('common');
    const { user, userType } = useAuth();
    const [savedArtSearches, setSavedArtSearches] = useState([]);
    const [savedStoryGenerations, setSavedStoryGenerations] = useState([]);
    const [expandedItem, setExpandedItem] = useState(null);
    const [deleteMessage, setDeleteMessage] = useState('');

    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

    const fetchUserProfile = async () => {
        if (!user || userType !== 'patient') return;

        try {
            const token = localStorage.getItem('token');
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
        if (user && userType === 'patient') {
            fetchUserProfile();
        }
    }, [user, userType]);

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
            setDeleteMessage(t('profile.loginToDelete'));
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
                setDeleteMessage(errorData.message || t('profile.deleteFailed'));
                console.error('Error deleting item:', errorData);
                return;
            }

            setDeleteMessage(t('profile.deleteSuccess'));
            fetchUserProfile();
            closeModal();
        } catch (error) {
            console.error('Error deleting item:', error);
            setDeleteMessage(t('profile.deleteFailed'));
        }
    };


    return (
        <div>
            <div className="content-box">
                <h1>{t('profile.welcomeTitle', { email: user?.email || 'User' })}</h1>
                <p>{t('profile.welcomeDescription')}</p>
            </div>

            {userType === 'patient' ? (
                <>
                    <div className="content-box">
                        <h1>{t('profile.storyHistoryTitle')}</h1>
                        <div className="story-list">
                            {savedStoryGenerations.length > 0 ? (
                                savedStoryGenerations.map((story, index) => (
                                    <div
                                        key={story._id || index}
                                        className="story-box"
                                        onClick={() => handleItemClick(story)}
                                    >
                                        <h3><strong>{t('profile.date')}</strong> {new Date(story.dateAdded).toLocaleString()}</h3>
                                        <p>{story.text.substring(0, 50)}...</p>
                                    </div>
                                ))
                            ) : (
                                <p>{t('profile.noStoriesYet')}</p>
                            )}
                        </div>
                    </div>

                    <div className="content-box">
                        <h1>{t('profile.artHistoryTitle')}</h1>
                        <div className="story-list">
                            {savedArtSearches.length > 0 ? (
                                savedArtSearches.map((search, index) => (
                                    <div
                                        key={search._id || index}
                                        className="story-box"
                                        onClick={() => handleItemClick(search)}
                                    >
                                        <h3><strong>{t('profile.date')}</strong> {new Date(search.dateAdded).toLocaleString()}</h3>
                                        <p>{search.text.substring(0, 50)}...</p>
                                    </div>
                                ))
                            ) : (
                                <p>{t('profile.noSearchesYet')}</p>
                            )}
                        </div>
                    </div>
                </>
            ) : null}            {expandedItem && (
                <div className="modal-history">
                    <div className="modal-history-content">
                        <span className="history-close-button" onClick={closeModal}>&times;</span>
                        <h3><strong>{t('profile.date')}</strong> {new Date(expandedItem.dateAdded).toLocaleString()}</h3>
                        <p>{expandedItem.text}</p>
                        {expandedItem.hasOwnProperty('images') && Array.isArray(expandedItem.images) && expandedItem.images.length > 0 ? (
                            // This is for savedStoryGenerations (flat list of images)
                            <div className="modal-images-grid">
                                {expandedItem.images.map((imageUrl, index) => (
                                    <img
                                        key={index}
                                        src={imageUrl}
                                        alt={t('profile.storyImageAlt', { number: index + 1 })}
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
                                            <h4>{datasetName.charAt(0).toUpperCase() + datasetName.slice(1)} {t('profile.imagesLabel')}</h4>
                                            {urls.map((imageUrl, index) => (
                                                <img
                                                    key={`${datasetName}-${index}`}
                                                    src={imageUrl}
                                                    alt={t('profile.datasetImageAlt', { dataset: datasetName, number: index + 1 })}
                                                    className="modal-history-image"
                                                />
                                            ))}
                                        </div>
                                    )
                                ))}
                            </div>
                        ) : null}

                        <div className="modal-actions">
                            <button className="delete-button" onClick={handleDeleteClick}>{t('profile.delete')}</button>
                            {deleteMessage && <p className="delete-message">{deleteMessage}</p>}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Profile;