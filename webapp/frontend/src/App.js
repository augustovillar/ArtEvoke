// src/App.js
import React from 'react';
import './i18n';
import { Routes, Route } from 'react-router-dom';
import { Navbar, Footer, ProtectedRoute } from './components/common';
import { Home, About, MemoryReconstruction, SignUp, Login, Profile, Patients, CreatePatient, Sessions, SessionDetails, RoleSelection, DoctorSignUp, DoctorLogin, PatientComplete, PatientLogin } from './pages';
import ArtExplorationFree from './pages/ArtExploration/ArtExplorationFree';
import ArtExplorationSession from './pages/ArtExploration/ArtExplorationSession';
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
                                {/* Art Exploration - Free Mode */}
                                <Route path="/artsearch" element={
                                    <ProtectedRoute>
                                        <ArtExplorationFree />
                                    </ProtectedRoute>
                                } />
                                
                                {/* Art Exploration - Session Mode */}
                                <Route path="/sessions/:sessionId/art-exploration" element={
                                    <ProtectedRoute>
                                        <ArtExplorationSession />
                                    </ProtectedRoute>
                                } />
                                <Route path="/sessions/:sessionId/art-exploration/evaluation" element={
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
                                <Route path="/sessions" element={
                                    <ProtectedRoute>
                                        <Sessions />
                                    </ProtectedRoute>
                                } />
                                <Route path="/sessions/:sessionId/results" element={
                                    <ProtectedRoute>
                                        <SessionDetails />
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