import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts';
import './Profile.css';

const Profile = () => {
    const { t } = useTranslation('common');
    const { user, userType } = useAuth();
    const [savedMemoryReconstructions, setSavedMemoryReconstructions] = useState([]);
    const [savedArtExplorations, setSavedArtExplorations] = useState([]);
    const [expandedItem, setExpandedItem] = useState(null);
    const [imageUrls, setImageUrls] = useState({});
    const [deleteMessage, setDeleteMessage] = useState('');
    const [expandedSections, setExpandedSections] = useState(new Set());
    const [selectedImage, setSelectedImage] = useState(null);

    // Fetch image URLs when opening modal for memory reconstruction or art exploration
    useEffect(() => {
        if (expandedItem && expandedItem.hasOwnProperty('sections')) {
            const allIds = [];
            expandedItem.sections.forEach(section => {
                [section.image1_id, section.image2_id, section.image3_id, section.image4_id, section.image5_id, section.image6_id, section.fav_image_id].forEach(id => {
                    if (id) allIds.push(id);
                });
            });
            if (allIds.length > 0) {
                fetch('/api/images', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    },
                    body: JSON.stringify({ ids: allIds }),
                })
                .then(response => response.json())
                .then(data => {
                    setImageUrls(data.urls || {});
                })
                .catch(error => {
                    console.error('Error fetching image URLs:', error);
                });
            }
        } else if (expandedItem && expandedItem.hasOwnProperty('story_generated')) {
            // Art exploration - fetch image URLs
            const allIds = expandedItem.images.map(img => img.id);
            if (allIds.length > 0) {
                fetch('/api/images', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    },
                    body: JSON.stringify({ ids: allIds }),
                })
                .then(response => response.json())
                .then(data => {
                    setImageUrls(data.urls || {});
                })
                .catch(error => {
                    console.error('Error fetching image URLs:', error);
                });
            }
        } else {
            setImageUrls({});
        }
    }, [expandedItem]);

    const fetchUserProfile = async () => {
        if (!user || userType !== 'patient') return;

        // Fetch memory reconstructions
        try {
            const token = localStorage.getItem('token');
            const memoryResponse = await fetch(`/api/memory/retrieve?limit=10&offset=0`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (memoryResponse.ok) {
                const memoryData = await memoryResponse.json();
                setSavedMemoryReconstructions(memoryData.memory_reconstructions || []);
            }
        } catch (error) {
            console.error('Error fetching memory reconstructions:', error);
        }

        // Fetch art explorations
        try {
            const token = localStorage.getItem('token');
            const artExplorationResponse = await fetch(`/api/art/retrieve?limit=10&offset=0`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (artExplorationResponse.ok) {
                const artExplorationData = await artExplorationResponse.json();
                setSavedArtExplorations(artExplorationData.art_explorations || []);
            }
        } catch (error) {
            console.error('Error fetching art explorations:', error);
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
        // Reset expanded sections when opening modal
        setExpandedSections(new Set());
    };

    const closeModal = () => {
        setExpandedItem(null);
        setDeleteMessage('');
        setExpandedSections(new Set());
    };

    const toggleSection = (sectionId) => {
        const newExpanded = new Set(expandedSections);
        if (newExpanded.has(sectionId)) {
            newExpanded.delete(sectionId);
        } else {
            newExpanded.add(sectionId);
        }
        setExpandedSections(newExpanded);
    };

    const handleDeleteClick = async () => {
        console.log('Delete button clicked', expandedItem);

        if (!expandedItem) {
            console.error('No item to delete.');
            return;
        }

        // Check for appropriate ID based on item type
        let itemId = null;
        if (expandedItem.hasOwnProperty('sections') || expandedItem.hasOwnProperty('story_generated')) {
            // It's a memory reconstruction or art exploration
            itemId = expandedItem.id;
        } else {
            // It's a saved story generation or art search
            itemId = expandedItem._id;
        }

        console.log('Item ID:', itemId);

        if (!itemId) {
            console.error('No ID found for item to delete.');
            return;
        }

        const token = localStorage.getItem('token');
        console.log('Token exists:', !!token);

        if (!token) {
            setDeleteMessage(t('profile.loginToDelete'));
            return;
        }

        let deleteEndpoint = '';
        if (expandedItem.hasOwnProperty('story_generated')) {
            // It's an art exploration
            deleteEndpoint = `/api/art/delete/${itemId}`;
        } else if (expandedItem.hasOwnProperty('sections')) {
            // It's a memory reconstruction
            deleteEndpoint = `/api/memory/delete/${itemId}`;
        } else {
            console.error('Unknown item type for deletion.');
            return;
        }

        console.log('Delete endpoint:', deleteEndpoint);

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
                <h1>{t('profile.welcomeTitle', { email: user?.name || user?.email || 'User' })}</h1>
                <p>{t('profile.welcomeDescription')}</p>
            </div>

            {userType === 'patient' ? (
                <>
                    <div className="content-box">
                        <h1>{t('profile.memoryReconstructionTitle')}</h1>
                        <div className="story-list">
                            {savedMemoryReconstructions.length > 0 ? (
                                savedMemoryReconstructions.map((reconstruction, index) => {
                                    const createdDate = new Date(reconstruction.created_at);
                                    return (
                                        <div
                                            key={reconstruction.id || index}
                                            className="story-box story-box-compact"
                                            onClick={() => handleItemClick(reconstruction)}
                                        >
                                            <p><strong>{t('profile.date')}:</strong> {createdDate.toLocaleDateString()}</p>
                                            <p><strong>{t('profile.time')}:</strong> {createdDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}</p>
                                            <p><strong>{t('profile.dataset')}:</strong> {reconstruction.dataset}</p>
                                            <p><strong>{t('profile.story')}:</strong> {reconstruction.story.substring(0, 60)}...</p>
                                            <p><strong>{t('profile.sectionsCount')}:</strong> {reconstruction.sections.length}</p>
                                        </div>
                                    );
                                })
                            ) : (
                                <p>{t('profile.noMemoryReconstructionsYet')}</p>
                            )}
                        </div>
                    </div>

                    <div className="content-box">
                        <h1>{t('profile.artExplorationsTitle')}</h1>
                        <div className="story-list">
                            {savedArtExplorations.length > 0 ? (
                                savedArtExplorations.map((exploration, index) => {
                                    const createdDate = new Date(exploration.created_at);
                                    return (
                                        <div
                                            key={exploration.id || index}
                                            className="story-box story-box-compact"
                                            onClick={() => handleItemClick(exploration)}
                                        >
                                            <p><strong>{t('profile.date')}:</strong> {createdDate.toLocaleDateString()}</p>
                                            <p><strong>{t('profile.time')}:</strong> {createdDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}</p>
                                            <p><strong>{t('profile.dataset')}:</strong> {exploration.dataset}</p>
                                            <p><strong>{t('profile.storyGenerated')}:</strong> {exploration.story_generated.substring(0, 60)}...</p>
                                            <p><strong>{t('profile.imagesSelected')}:</strong> {exploration.images.length}</p>
                                        </div>
                                    );
                                })
                            ) : (
                                <p>{t('profile.noArtExplorationsYet')}</p>
                            )}
                        </div>
                    </div>
                </>
            ) : null}            {expandedItem && (
                <div className="modal-history">
                    <div className="modal-history-content">
                        <span className="history-close-button" onClick={closeModal}>&times;</span>
                        <h3><strong>{t('profile.date')}</strong> {new Date(expandedItem.dateAdded || expandedItem.created_at).toLocaleString()}</h3>
                        {expandedItem.hasOwnProperty('story_generated') ? (
                            // This is an art exploration
                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                                <div style={{ marginBottom: '15px' }}>
                                    <h4>{t('profile.artExplorationStory')}:</h4>
                                    <p>{expandedItem.story_generated}</p>
                                    <p><strong>{t('profile.dataset')}:</strong> {expandedItem.dataset}</p>
                                    <p><strong>{t('profile.language')}:</strong> {expandedItem.language}</p>
                                    <h4>{t('profile.selectedImages')}:</h4>
                                </div>
                                <div className="modal-sections-content" style={{ flex: 1, overflowY: 'auto' }}>
                                    {expandedItem.images
                                        .sort((a, b) => a.display_order - b.display_order)
                                        .map((image, index) => {
                                            const imageId = image.id;
                                            const isExpanded = expandedSections.has(imageId);
                                            return (
                                                <div key={imageId} className="memory-section-modal">
                                                    <div 
                                                        className="section-header" 
                                                        onClick={() => toggleSection(imageId)}
                                                        style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                                                    >
                                                        <h5 style={{ margin: 0 }}>
                                                            {t('profile.imageLabel')} {index + 1}
                                                        </h5>
                                                        <span className="expand-arrow">
                                                            {isExpanded ? '▲' : '▼'}
                                                        </span>
                                                    </div>
                                                    {isExpanded && (
                                                        <div className="section-content">
                                                            <div className="section-images-grid" style={{ gridTemplateColumns: '1fr' }}>
                                                                <img
                                                                    src={imageUrls[imageId] || `/api/art/image/${imageId}`}
                                                                    alt={t('profile.artExplorationImageAlt', { number: index + 1 })}
                                                                    className="modal-history-image"
                                                                    onClick={() => setSelectedImage(imageUrls[imageId] || `/api/art/image/${imageId}`)}
                                                                    style={{ cursor: 'pointer', width: '100%' }}
                                                                />
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        })}
                                </div>
                            </div>
                        ) : expandedItem.hasOwnProperty('sections') ? (
                            // This is a memory reconstruction
                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                                <div style={{ marginBottom: '15px' }}>
                                    <h4>{t('profile.memoryReconstructionStory')}:</h4>
                                    <p>{expandedItem.story}</p>
                                    <h4>{t('profile.sectionsLabel')}:</h4>
                                </div>
                                <div className="modal-sections-content" style={{ flex: 1, overflowY: 'auto' }}>
                                    {expandedItem.sections.map((section, index) => {
                                        const isExpanded = expandedSections.has(section.id);
                                        return (
                                            <div key={section.id} className="memory-section-modal">
                                                <div 
                                                    className="section-header" 
                                                    onClick={() => toggleSection(section.id)}
                                                    style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                                                >
                                                    <h5 style={{ margin: 0 }}>
                                                        {t('profile.sectionLabel')} {index + 1}: {section.section_content}
                                                    </h5>
                                                    <span className="expand-arrow">
                                                        {isExpanded ? '▲' : '▼'}
                                                    </span>
                                                </div>
                                                {isExpanded && (
                                                    <div className="section-content">
                                                        <div className="section-images-grid">
                                                            {[section.image1_id, section.image2_id, section.image3_id, section.image4_id, section.image5_id, section.image6_id]
                                                                .filter(id => id)
                                                                .map((imageId, imgIndex) => {
                                                                    const imageUrl = imageUrls[imageId];
                                                                    return (
                                                                        <img
                                                                            key={imgIndex}
                                                                            src={imageUrl || `/api/art/image/${imageId}`}
                                                                            alt={t('profile.sectionImageAlt', { section: index + 1, number: imgIndex + 1 })}
                                                                            className={`modal-history-image ${imageId === section.fav_image_id ? 'favorite' : ''}`}
                                                                            onClick={() => setSelectedImage(imageUrl || `/api/art/image/${imageId}`)}
                                                                            style={{ cursor: 'pointer' }}
                                                                        />
                                                                    );
                                                                })}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        ) : null}

                        <div className="modal-actions">
                            <button className="delete-button" onClick={handleDeleteClick}>{t('profile.delete')}</button>
                            {deleteMessage && <p className="delete-message">{deleteMessage}</p>}
                        </div>
                    </div>
                </div>
            )}

            {/* Image Popup Modal */}
            {selectedImage && (
                <div className="image-popup-overlay" onClick={() => setSelectedImage(null)}>
                    <div className="image-popup-content" onClick={(e) => e.stopPropagation()}>
                        <button className="image-popup-close" onClick={() => setSelectedImage(null)}>×</button>
                        <img src={selectedImage} alt="Enlarged view" className="image-popup-image" />
                    </div>
                </div>
            )}
        </div>
    );
};

export default Profile;