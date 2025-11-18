import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts';
import { useReadAloud } from '../../contexts/ReadAloudContext';
import './Home.css';
import storyImage from '../../assets/images/storyImage.png';
import artImage from '../../assets/images/artImage.png';

const Home = () => {
    const { t } = useTranslation('common');
    const navigate = useNavigate();
    const { isLoggedIn } = useAuth();
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud();
    const memoryCardRef = useRef(null);
    const artCardRef = useRef(null);
    
    const [expandedMemory, setExpandedMemory] = useState(false);
    const [expandedArt, setExpandedArt] = useState(false);

    useEffect(() => {
        registerContent(contentRef, [
            t('home.memoryReconstructionDesc'),
            t('home.artExplorationDesc')
        ]);
        return () => registerContent(null);
    }, [registerContent, t]);

    const handleModeClick = (mode) => {
        if (isLoggedIn) {
            // Se logado, navega para o modo
            navigate(mode === 'memory' ? '/story' : '/artsearch');
        } else {
            // Se não logado, expande/recolhe a explicação de forma independente
            if (mode === 'memory') {
                setExpandedMemory(!expandedMemory);
                setExpandedArt(false); // Close the other card
            } else {
                setExpandedArt(!expandedArt);
                setExpandedMemory(false); // Close the other card
            }
        }
    };

    const handleCollapse = (cardRef, setExpanded) => {
        setExpanded(false);
        // Scroll to the card after a short delay to allow state update
        setTimeout(() => {
            if (cardRef.current) {
                cardRef.current.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start'
                });
            }
        }, 100);
    };

    return (
        <div className="home-container">
            <div className="hero-section" ref={contentRef}>
                <h1 className="hero-title">{t('home.heroTitle')}</h1>
                <p className="hero-description">
                    {t('home.heroDescription')}
                </p>
            </div>

            <div className="options-section">
                <div className="options-grid">
                    {/* Memory Reconstruction Card */}
                    <div 
                        ref={memoryCardRef}
                        className={`option-card ${expandedMemory ? 'expanded' : ''} ${!isLoggedIn ? 'clickable' : ''}`}
                    >
                        <div 
                            className="option-header"
                            onClick={() => !expandedMemory && handleModeClick('memory')}
                            style={{ cursor: expandedMemory ? 'default' : 'pointer' }}
                        >
                            <div className="option-icon-wrapper">
                                <img src={storyImage} alt={t('home.memoryReconstructionDesc')} className="option-icon" />
                            </div>
                            <span className="option-text">{t('home.memoryReconstruction')}</span>
                            <p className="option-brief">{t('home.memoryReconstructionDesc')}</p>
                        </div>

                        {!isLoggedIn && expandedMemory && (
                            <div className="option-expanded-content" onClick={(e) => e.stopPropagation()}>
                                <div className="expanded-section">
                                    <h3>{t('home.howItWorks')}</h3>
                                    <ol className="how-it-works-list">
                                        <li>{t('home.memoryStep1')}</li>
                                        <li>{t('home.memoryStep2')}</li>
                                        <li>{t('home.memoryStep3')}</li>
                                        <li>{t('home.memoryStep4')}</li>
                                    </ol>
                                </div>

                                <div className="expanded-section">
                                    <h3>{t('home.example')}</h3>
                                    <div className="example-content">
                                        <div className="example-story">
                                            <p className="example-text">
                                                {t('home.memoryExampleStory')}
                                            </p>
                                        </div>
                                        <p className="example-description">
                                            {t('home.memoryExampleDesc')}
                                        </p>
                                        <div className="example-sections">
                                            <div className="example-section-item">
                                                <h4>{t('home.section')} 1</h4>
                                                <p className="section-text">{t('home.memorySection1')}</p>
                                                <div className="example-images">
                                                    <img src="/mr_example/image0_0.jpg" alt="Via Appia at Sunset" className="example-image" />
                                                    <img src="/mr_example/image0_1.jpg" alt="View Over Town at Sunset" className="example-image" />
                                                    <img src="/mr_example/image0_2.jpg" alt="The Tuileries Study" className="example-image" />
                                                    <img src="/mr_example/image0_3.jpg" alt="Bridge at Posilippo" className="example-image" />
                                                    <img src="/mr_example/image0_4.jpg" alt="View of Moscow" className="example-image" />
                                                    <img src="/mr_example/image0_5.jpg" alt="Road to Berneval" className="example-image" />
                                                </div>
                                            </div>
                                            <div className="example-section-item">
                                                <h4>{t('home.section')} 2</h4>
                                                <p className="section-text">{t('home.memorySection2')}</p>
                                                <div className="example-images">
                                                    <img src="/mr_example/image1_0.jpg" alt="July Afternoon" className="example-image" />
                                                    <img src="/mr_example/image1_1.jpg" alt="Meadow on the Edge of a Forest" className="example-image" />
                                                    <img src="/mr_example/image1_2.jpg" alt="Grass" className="example-image" />
                                                    <img src="/mr_example/image1_3.jpg" alt="Shinnecock Hills Peconic Bay" className="example-image" />
                                                    <img src="/mr_example/image1_4.jpg" alt="Oat and Poppy Field Giverny" className="example-image" />
                                                    <img src="/mr_example/image1_5.jpg" alt="Poppy Garden" className="example-image" />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <button 
                                    className="collapse-button"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleCollapse(memoryCardRef, setExpandedMemory);
                                    }}
                                >
                                    {t('home.showLess')}
                                </button>
                            </div>
                        )}

                        {!isLoggedIn && !expandedMemory && (
                            <button 
                                className="expand-button"
                                onClick={() => handleModeClick('memory')}
                            >
                                {t('home.learnMore')}
                            </button>
                        )}
                    </div>

                    {/* Art Exploration Card */}
                    <div 
                        ref={artCardRef}
                        className={`option-card ${expandedArt ? 'expanded' : ''} ${!isLoggedIn ? 'clickable' : ''}`}
                    >
                        <div 
                            className="option-header"
                            onClick={() => !expandedArt && handleModeClick('art')}
                            style={{ cursor: expandedArt ? 'default' : 'pointer' }}
                        >
                            <div className="option-icon-wrapper">
                                <img src={artImage} alt={t('home.artExplorationDesc')} className="option-icon" />
                            </div>
                            <span className="option-text">{t('home.artExploration')}</span>
                            <p className="option-brief">{t('home.artExplorationDesc')}</p>
                        </div>

                        {!isLoggedIn && expandedArt && (
                            <div className="option-expanded-content" onClick={(e) => e.stopPropagation()}>
                                <div className="expanded-section">
                                    <h3>{t('home.howItWorks')}</h3>
                                    <ol className="how-it-works-list">
                                        <li>{t('home.artStep1')}</li>
                                        <li>{t('home.artStep2')}</li>
                                        <li>{t('home.artStep3')}</li>
                                        <li>{t('home.artStep4')}</li>
                                    </ol>
                                </div>

                                <div className="expanded-section">
                                    <h3>{t('home.example')}</h3>
                                    <div className="example-content">
                                        <div className="keywords-section">
                                            <h4>{t('home.keywordsEntered')}</h4>
                                            <div className="keywords-list">
                                                <span className="keyword-tag">{t('home.keyword1')}</span>
                                                <span className="keyword-tag">{t('home.keyword2')}</span>
                                                <span className="keyword-tag">{t('home.keyword3')}</span>
                                            </div>
                                        </div>
                                        <p className="example-description">
                                            {t('home.artSearchDesc')}
                                        </p>
                                        <div className="example-images">
                                            <img src="/ae_example/image0.jpg" alt={t('home.artImage1')} className="example-image art-exploration" />
                                            <img src="/ae_example/image1.jpg" alt={t('home.artImage2')} className="example-image art-exploration" />
                                            <img src="/ae_example/image2.jpg" alt={t('home.artImage3')} className="example-image art-exploration" />
                                        </div>
                                        <p className="example-description">
                                            {t('home.artGenerationDesc')}
                                        </p>
                                        <div className="example-story">
                                            <p className="example-text">
                                                {t('home.artExampleStory')}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <button 
                                    className="collapse-button"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleCollapse(artCardRef, setExpandedArt);
                                    }}
                                >
                                    {t('home.showLess')}
                                </button>
                            </div>
                        )}

                        {!isLoggedIn && !expandedArt && (
                            <button 
                                className="expand-button"
                                onClick={() => handleModeClick('art')}
                            >
                                {t('home.learnMore')}
                            </button>
                        )}
                    </div>
                </div>

                {!isLoggedIn && (
                    <div className="login-prompt">
                        <p>{t('home.loginPrompt')}</p>
                        <button 
                            className="login-prompt-button"
                            onClick={() => navigate('/auth/login-role-selection')}
                        >
                            {t('home.loginButton')}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Home;