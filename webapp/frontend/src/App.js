// src/App.js
import React from 'react';
import './i18n';
import { Routes, Route } from 'react-router-dom';
import { Navbar, Footer } from './components/common';
import { Home, About, Story, Search, SignUp, Login, Profile, RoleSelection, DoctorSignUp, DoctorLogin, PatientComplete, PatientLogin } from './pages';
import './styles/App.css';
import { ThemeProvider } from './contexts/ThemeContext';
import { ReadAloudProvider } from './contexts/ReadAloudContext';

function App() {
    return (
        <ThemeProvider>
            <ReadAloudProvider>
                <div id="app-container">
                    <Navbar />
                    <div className="content-wrapper">
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/about" element={<About />} />
                            <Route path='/story' element={<Story />} />
                            <Route path="/artsearch" element={<Search />} />
                            <Route path="/signup" element={<SignUp />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/profile" element={<Profile />} />
                            <Route path="/auth/role-selection" element={<RoleSelection />} />
                            <Route path="/auth/doctor-signup" element={<DoctorSignUp />} />
                            <Route path="/auth/doctor-login" element={<DoctorLogin />} />
                            <Route path="/auth/patient-complete" element={<PatientComplete />} />
                            <Route path="/auth/patient-login" element={<PatientLogin />} />
                        </Routes>
                    </div>
                    <Footer />
                </div>
            </ReadAloudProvider>
        </ThemeProvider>
    );
}

export default App;