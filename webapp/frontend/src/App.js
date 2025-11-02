// src/App.js
import React from 'react';
import './i18n';
import { Routes, Route } from 'react-router-dom';
import { Navbar, Footer, ProtectedRoute } from './components/common';
import { Home, About, MemoryReconstruction, ArtExploration, SignUp, Login, Profile, Patients, CreatePatient, RoleSelection, DoctorSignUp, DoctorLogin, PatientComplete, PatientLogin } from './pages';
import MemoryEvaluation from './pages/MemoryReconstruction/Evaluation';
import ArtEvaluation from './pages/ArtExploration/Evaluation';
import './styles/App.css';
import { ThemeProvider } from './contexts';
import { ReadAloudProvider } from './contexts';
import { AuthProvider } from './contexts';

function App() {
    return (
        <ThemeProvider>
            <ReadAloudProvider>
                <AuthProvider>
                    <div id="app-container">
                        <Navbar />
                        <div className="content-wrapper">
                            <Routes>
                                <Route path="/" element={<Home />} />
                                <Route path="/about" element={<About />} />
                                
                                {/* Protected Routes - Only accessible when logged in */}
                                <Route path='/story' element={
                                    <ProtectedRoute>
                                        <MemoryReconstruction />
                                    </ProtectedRoute>
                                } />
                                <Route path='/memory-reconstruction/evaluation' element={
                                    <ProtectedRoute>
                                        <MemoryEvaluation />
                                    </ProtectedRoute>
                                } />
                                <Route path="/artsearch" element={
                                    <ProtectedRoute>
                                        <ArtExploration />
                                    </ProtectedRoute>
                                } />
                                <Route path="/art-exploration/evaluation" element={
                                    <ProtectedRoute>
                                        <ArtEvaluation />
                                    </ProtectedRoute>
                                } />
                                <Route path="/profile" element={
                                    <ProtectedRoute>
                                        <Profile />
                                    </ProtectedRoute>
                                } />
                                <Route path="/patients" element={
                                    <ProtectedRoute>
                                        <Patients />
                                    </ProtectedRoute>
                                } />
                                <Route path="/patients/create" element={
                                    <ProtectedRoute>
                                        <CreatePatient />
                                    </ProtectedRoute>
                                } />
                                
                                {/* Public Auth Routes */}
                                <Route path="/signup" element={<SignUp />} />
                                <Route path="/login" element={<Login />} />
                                <Route path="/auth/role-selection" element={<RoleSelection mode="signup" />} />
                                <Route path="/auth/login-role-selection" element={<RoleSelection mode="login" />} />
                                <Route path="/auth/doctor-signup" element={<DoctorSignUp />} />
                                <Route path="/auth/doctor-login" element={<DoctorLogin />} />
                                <Route path="/auth/patient-complete" element={<PatientComplete />} />
                                <Route path="/auth/patient-login" element={<PatientLogin />} />
                            </Routes>
                        </div>
                        <Footer />
                    </div>
                </AuthProvider>
            </ReadAloudProvider>
        </ThemeProvider>
    );
}

export default App;