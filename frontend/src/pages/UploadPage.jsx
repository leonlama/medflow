import React, { useState } from 'react';
import axios from 'axios';
import { API_URL } from '../config';

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [waiting, setWaiting] = useState(false);
  const [modalPatientId, setModalPatientId] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await axios.post(`${API_URL}/clean`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      const { job_id, patient_id } = uploadResponse.data;
      console.log("Upload successful, patient_id:", patient_id, "job_id:", job_id);

      setWaiting(true);
      const timeout = 120; // seconds
      let elapsed = 0;

      while (elapsed < timeout) {
        const patientRes = await axios.get(`${API_URL}/patients?id=${patient_id}`);
        const patient = Array.isArray(patientRes.data) ? patientRes.data[0] : patientRes.data;

        console.log('Fetched patient:', patient);

        if (patient && patient.status && patient.status === "completed") {
          console.log("Patient completed!");
          setModalPatientId(patient_id);
          setShowModal(true);
          return;
        }

        await new Promise((resolve) => setTimeout(resolve, 3000));
        elapsed += 3;
      }

      alert("Diagnostic process taking too long. Please try again later.");
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error during upload.");
    } finally {
      setUploading(false);
      setWaiting(false);
    }
  };

  return (
    <div>
      <h1>Upload Patient Form</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? 'Processing...' : 'Upload'}
      </button>

      {waiting && (
        <p><i>Waiting for diagnostic results...</i></p>
      )}

      {showModal && (
        <div className="modal">
          <p>Patient ID: {modalPatientId}</p>
          <button onClick={() => setShowModal(false)}>Close</button>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
