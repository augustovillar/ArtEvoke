// src/components/FontSizeAdjuster.js
import React, { useState, useEffect } from 'react';
import './FontSizeAdjuster.css';

const FontSizeAdjuster = () => {
    // Initialize font size from a CSS custom property if it exists, otherwise default
    const getInitialFontSize = () => {
        const rootFontSize = getComputedStyle(document.documentElement).getPropertyValue('--base-font-size');
        return rootFontSize ? parseInt(rootFontSize, 10) : 16; // Default to 16px if not set, match your usual base font size
    };

    const [fontSize, setFontSize] = useState(getInitialFontSize);

    useEffect(() => {
        // Update the CSS custom property whenever fontSize changes
        document.documentElement.style.setProperty('--base-font-size', `${fontSize}px`);
    }, [fontSize]);

    const handleFontSizeChange = (event) => {
        setFontSize(event.target.value);
    };

    return (
        <div className="font-size-adjuster">
            <h3>Adjust Font Size: {fontSize}px</h3>
            <input
                type="range"
                min="14" // Minimum font size
                max="24" // Maximum font size. You had 32 in Home.js, consider if 24 is better for accessibility panel
                value={fontSize}
                onChange={handleFontSizeChange}
                className="font-size-slider"
            />
            <p className="slider-example-text">
                This text will scale dynamically based on the font size you select.
            </p>
        </div>
    );
};

export default FontSizeAdjuster;