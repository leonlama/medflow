import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom'; // 🆕 get params
import axios from 'axios';

const PatientReviewPage = () => {
  const { patientId } = useParams(); // 🆕 get patientId from URL params

  const [patientData, setPatientData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function fetchPatient() {
      try {
        const response = await axios.get(`/api/patients?id=${patientId}`); // 🛠️ CORRECT way
        setPatientData(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching patient data', error);
        setLoading(false);
      }
    }
    fetchPatient();
  }, [patientId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setPatientData(prev => ({ ...prev, [name]: value }));
  };

  const handleConfirm = () => {
    setSaving(true);
    axios.post('/api/confirm', {
      patient_id: patientId,
      updated_data: {
        name: patientData.name,
        birthday: patientData.birthday,
        address: patientData.address,
        allergies: patientData.allergies,
      }
    })
    .then(() => {
      alert('Patient confirmed successfully!');
    })
    .catch((err) => {
      console.error('Error confirming patient', err);
      alert('Error confirming.');
    })
    .finally(() => setSaving(false));
  };

  if (loading) return <p>Loading patient data...</p>;

  return (
    <div>
      <h2>Review Patient Information</h2>
      <label>
        Name:
        <input name="name" value={patientData.name} onChange={handleChange} />
      </label>
      <br />
      <label>
        Birthday:
        <input name="birthday" value={patientData.birthday} onChange={handleChange} />
      </label>
      <br />
      <label>
        Address:
        <input name="address" value={patientData.address} onChange={handleChange} />
      </label>
      <br />
      <label>
        Allergies:
        <input name="allergies" value={patientData.allergies} onChange={handleChange} />
      </label>
      <br />
      <button onClick={handleConfirm} disabled={saving}>
        {saving ? 'Saving...' : 'Confirm'}
      </button>
    </div>
  );
};

export default PatientReviewPage;
