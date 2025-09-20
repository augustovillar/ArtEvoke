import React from 'react';
import './About.css';
import poster from './images/poster.png'

const About = () => {
    return (
        <div>
            <div className="content-box">
                <h1>About Us</h1>
                <p>
                    This website is created in the context of a Masters Thesis at the Université Catholique de Louvain, 
                    undertaken by Marc Bejjani and Augusto Barbosa Villar Silva, under the supervision of Professor Benoît Macq.
                </p>
                <p>
                    This thesis explores how artificial intelligence can support non-drug interventions
                    for people living with Alzheimer’s disease (AD) through the use of visual stimuli and
                    art. We present a prototype platform that combines large multimodal models (LMMs),
                    large language models (LLMs), and embedding-based vector search to connect personal
                    stories with curated artworks. Designed to assist memory recall and cognitive engagement,
                    ArtEvoke generates personalized visual narratives or retrieves relevant paintings based on
                    the user’s story. Art is used not only as a memory trigger but also as a tool to promote
                    emotional connection and engagement. The prototype is intended for testing in future
                    therapeutic and research settings, particularly as a scalable support tool for caregivers
                    and clinical practitioners. We evaluate model performance, retrieval effectiveness using
                    FAISS, and user interaction design with a focus on accessibility. These findings highlight
                    the potential of AI tools to support scalable cognitive stimulation in dementia care.
                </p>
            </div>
        </div>
    );
};

export default About;