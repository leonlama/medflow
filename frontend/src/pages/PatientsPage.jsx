import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { API_URL } from '../config';

function PatientsPage() {
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    async function fetchPatients() {
      try {
        const res = await axios.get(`${API_URL}/patients`);
        setPatients(res.data);
      } catch (error) {
        console.error('Failed to fetch patients:', error);
      }
    }
    fetchPatients();
  }, []);

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Registered Patients</h2>
      {patients.length === 0 && <p>No patients yet.</p>}
      {patients.map((p) => (
        <div key={p.patient_id} style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: '#eef2f7', borderRadius: '5px' }}>
          <strong>{p.name || 'Unnamed Patient'}</strong> — {p.birthday || 'Unknown Birthday'}
          <br />
          {p.address || 'Unknown Address'}
          <br />
          <Link to={`/patients/${p.patient_id}`} style={{ color: '#007bff', textDecoration: 'underline' }}>
            Review Record
          </Link>
        </div>
      ))}
    </div>
  );
}

export default PatientsPage;
