import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_URL } from '../config';

const PatientReviewModal = ({ patientId, onClose }) => {
  const [patientData, setPatientData] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function fetchPatient() {
      try {
        const response = await axios.get(`${API_URL}/patients?id=${patientId}`);
        setPatientData(response.data);
      } catch (error) {
        console.error('Error fetching patient data', error);
      }
    }
    fetchPatient();
  }, [patientId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setPatientData(prev => ({ ...prev, [name]: value }));
  };

  const handleConfirm = async () => {
    setSaving(true);
    try {
      await axios.post(`${API_URL}/confirm`, {
        patient_id: patientId,
        updated_data: {
          name: patientData.name,
          birthday: patientData.birthday,
          address: patientData.address,
          allergies: patientData.allergies,
        }
      });
      alert('Patient confirmed successfully!');
      onClose();
    } catch (err) {
      console.error('Error confirming patient', err);
      alert('Error confirming.');
    } finally {
      setSaving(false);
    }
  };

  if (!patientData) return <div>Loading...</div>;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center'
    }}>
      <div style={{ backgroundColor: 'white', padding: '2rem', borderRadius: '10px', width: '400px' }}>
        <h2>Review Patient</h2>
        <label>
          Name:
          <input name="name" value={patientData.name || ''} onChange={handleChange} />
        </label>
        <br />
        <label>
          Birthday:
          <input name="birthday" value={patientData.birthday || ''} onChange={handleChange} />
        </label>
        <br />
        <label>
          Address:
          <input name="address" value={patientData.address || ''} onChange={handleChange} />
        </label>
        <br />
        <label>
          Allergies:
          <input name="allergies" value={patientData.allergies || ''} onChange={handleChange} />
        </label>
        <br />
        <button onClick={handleConfirm} disabled={saving} style={{ marginTop: '1rem' }}>
          {saving ? 'Saving...' : 'Confirm'}
        </button>
        <button onClick={onClose} style={{ marginLeft: '1rem', marginTop: '1rem' }}>
          Cancel
        </button>
      </div>
    </div>
  );
};

export default PatientReviewModal;
