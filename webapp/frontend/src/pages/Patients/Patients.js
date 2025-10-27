import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import './Patients.css';

const Patients = () => {
    const { t } = useTranslation('common');
    const [patients, setPatients] = useState([]);
    const [filteredPatients, setFilteredPatients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedPatient, setSelectedPatient] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchPatients();
    }, []);

    useEffect(() => {
        const filtered = patients.filter(patient =>
            patient.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setFilteredPatients(filtered);
    }, [patients, searchTerm]);

    const fetchPatients = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/doctors/patients', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setPatients(Array.isArray(data) ? data : []);
            } else {
                setError('Failed to fetch patients');
                setPatients([]);
            }
        } catch (error) {
            setError('Error fetching patients');
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreatePatient = () => {
        navigate('/patients/create');
    };

    const handleViewDetails = (patient) => {
        setSelectedPatient(patient);
    };

    const closeModal = () => {
        setSelectedPatient(null);
    };

    if (loading) {
        return <div className="patients-container"><p>Loading patients...</p></div>;
    }

    if (error) {
        return <div className="patients-container"><p>Error: {error}</p></div>;
    }

    return (
        <div className="patients-container">
            <h1>{t('patients.title', 'My Patients')}</h1>

            <div className="patients-header">
                <div className="search-container">
                    <input
                        type="text"
                        placeholder={t('patients.searchPlaceholder', 'Search patients by name...')}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="search-input"
                    />
                </div>
                <button onClick={handleCreatePatient} className="create-patient-btn">
                    {t('patients.createPatient', 'Create New Patient')}
                </button>
            </div>

            <div className="patients-list">
                {filteredPatients.length === 0 ? (
                    <p>{t('patients.noPatients', 'No patients found.')}</p>
                ) : (
                    <div className="patients-grid">
                        {filteredPatients.map(patient => (
                            <div key={patient.id} className="patient-card">
                                <h3>{patient.name}</h3>
                                <p><strong>{t('patients.email', 'Email')}:</strong> {patient.email}</p>
                                <p><strong>{t('patients.dateOfBirth', 'Date of Birth')}:</strong> {patient.date_of_birth || 'Not provided'}</p>
                                <div className="patient-card-actions">
                                    <div className={`status-badge ${patient.is_active ? 'active' : 'pending'}`}>
                                        {patient.is_active ? t('patients.statusActive', 'Account Active') : t('patients.statusPending', 'Account Pending')}
                                    </div>
                                    <button onClick={() => handleViewDetails(patient)} className="view-patient-btn">
                                        {t('patients.viewDetails', 'View Details')}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {selectedPatient && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>{selectedPatient.name}</h2>
                        <div className="patient-details">
                            <p><strong>{t('patients.email', 'Email')}:</strong> {selectedPatient.email}</p>
                            <p><strong>{t('patients.dateOfBirth', 'Date of Birth')}:</strong> {selectedPatient.date_of_birth || 'Not provided'}</p>
                            <p><strong>{t('patients.educationLevel', 'Education Level')}:</strong> {selectedPatient.education_level || 'Not provided'}</p>
                            <p><strong>{t('patients.occupation', 'Occupation')}:</strong> {selectedPatient.occupation || 'Not provided'}</p>
                            <p><strong>{t('patients.visualImpairment', 'Visual Impairment')}:</strong> {selectedPatient.visual_impairment ? 'Yes' : 'No'}</p>
                            <p><strong>{t('patients.hearingImpairment', 'Hearing Impairment')}:</strong> {selectedPatient.hearing_impairment ? 'Yes' : 'No'}</p>
                            <p><strong>{t('patients.status', 'Status')}:</strong> {selectedPatient.status}</p>
                            <p><strong>{t('patients.createdAt', 'Created At')}:</strong> {new Date(selectedPatient.created_at).toLocaleDateString()}</p>
                        </div>
                        <button onClick={closeModal} className="close-modal-btn">
                            {t('common.close', 'Close')}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Patients;