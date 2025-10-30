import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './CreateSession.css';

const CreateSession = ({ patientId, onClose, onSuccess }) => {
    const { t } = useTranslation('common');
    const [patients, setPatients] = useState([]);
    const [formData, setFormData] = useState({
        patient_id: patientId || '',
        mode: 'memory_reconstruction',
        interruption_time: 10
    });
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!patientId) {
            fetchPatients();
        }
    }, [patientId]);

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
            }
        } catch (error) {
            console.error('Error fetching patients:', error);
        }
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.patient_id) {
            newErrors.patient_id = t('sessions.create.validation.patientRequired');
        }

        if (!formData.mode) {
            newErrors.mode = t('sessions.create.validation.modeRequired');
        }

        if (formData.interruption_time < 1) {
            newErrors.interruption_time = t('sessions.create.validation.interruptionTimeMin');
        }

        if (formData.interruption_time > 300) {
            newErrors.interruption_time = t('sessions.create.validation.interruptionTimeMax');
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/sessions/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                onSuccess();
            } else {
                const error = await response.json();
                let errorMessage = t('sessions.create.error');
                
                // Check for specific error messages
                if (error.detail) {
                    if (error.detail.includes("don't have access")) {
                        errorMessage = t('sessions.errors.noAccess');
                    } else if (typeof error.detail === 'string') {
                        errorMessage = error.detail;
                    }
                }
                
                setErrors({ submit: errorMessage });
            }
        } catch (error) {
            setErrors({ submit: t('sessions.create.error') });
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'interruption_time' ? parseInt(value) : value
        }));
        // Clear error for this field
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>{t('sessions.create.title')}</h2>
                    <button className="modal-close" onClick={onClose}>&times;</button>
                </div>

                <form onSubmit={handleSubmit} className="create-session-form">
                    {!patientId && (
                        <div className="form-group">
                            <label htmlFor="patient_id">{t('sessions.create.selectPatient')}</label>
                            <select
                                id="patient_id"
                                name="patient_id"
                                value={formData.patient_id}
                                onChange={handleChange}
                                className={errors.patient_id ? 'error' : ''}
                            >
                                <option value="">{t('sessions.create.selectPatientPlaceholder')}</option>
                                {patients.map(patient => (
                                    <option key={patient.id} value={patient.id}>
                                        {patient.name}
                                    </option>
                                ))}
                            </select>
                            {errors.patient_id && <span className="error-message">{errors.patient_id}</span>}
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="mode">{t('sessions.create.selectMode')}</label>
                        <select
                            id="mode"
                            name="mode"
                            value={formData.mode}
                            onChange={handleChange}
                            className={errors.mode ? 'error' : ''}
                        >
                            <option value="memory_reconstruction">{t('sessions.modes.memory_reconstruction')}</option>
                            <option value="art_exploration">{t('sessions.modes.art_exploration')}</option>
                            <option value="both">{t('sessions.modes.both')}</option>
                        </select>
                        {errors.mode && <span className="error-message">{errors.mode}</span>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="interruption_time">{t('sessions.create.interruptionTime')}</label>
                        <input
                            type="number"
                            id="interruption_time"
                            name="interruption_time"
                            value={formData.interruption_time}
                            onChange={handleChange}
                            min="1"
                            max="300"
                            className={errors.interruption_time ? 'error' : ''}
                        />
                        <small className="form-help">{t('sessions.create.interruptionTimeHelp')}</small>
                        {errors.interruption_time && <span className="error-message">{errors.interruption_time}</span>}
                    </div>

                    {errors.submit && <div className="form-error">{errors.submit}</div>}

                    <div className="form-actions">
                        <button type="button" className="btn-cancel" onClick={onClose}>
                            {t('sessions.create.cancel')}
                        </button>
                        <button type="submit" className="btn-submit" disabled={loading}>
                            {loading ? t('common.loading') : t('sessions.create.submit')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateSession;
