// src/components/Navbar.jsx
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav style={{ backgroundColor: '#007bff', padding: '1rem', marginBottom: '2rem' }}>
      <Link to="/" style={{ color: 'white', marginRight: '2rem', textDecoration: 'none' }}>
        Upload
      </Link>
      <Link to="/patients" style={{ color: 'white', textDecoration: 'none' }}>
        Find Patients
      </Link>
    </nav>
  );
}

export default Navbar;
