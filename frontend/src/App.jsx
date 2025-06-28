import { useState } from 'react';

function App() {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [barcode, setBarcode] = useState('');
  const [patronId, setPatronId] = useState(null);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [isNewPatron, setIsNewPatron] = useState(false);
  const [email, setEmail] = useState('');


  // function for the identify patron api. if patron exists in db,
  // patron will go to checkout screen. otherwise, they will be taken to registration screen
  const handleIdentify = async () => {
    setError('');
    setStatus('');
    try {
      const res = await fetch('http://localhost:8000/patrons/identify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, phone })
      });
      const data = await res.json();
      if (data.existing) {
        setPatronId(data.patron.id);
        setStatus(`Welcome back, ${data.patron.name}`);
        setIsNewPatron(false);
      } else {
        setIsNewPatron(true);
        setStatus('');
      }
    } catch (err) {
      setError('Error contacting server.');
    }
  };

  // function for /patrons/create route
  const handleRegister = async () => {
  try {
    const res = await fetch('http://localhost:8000/patrons/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone, email })
    });
    const data = await res.json();
    if (res.ok) {
      setPatronId(data.id);  // assume backend returns new patron's ID
      setIsNewPatron(false);
      setStatus('Registered successfully. You can now check out or return books.');
    } else {
      setError(data.error || 'Registration failed.');
    }
  } catch (err) {
    setError('Error contacting server.');
  }
};


  // function for the /books/toggle route
  const handleToggle = async (action) => {
    setError('');
    setStatus('');
    if (!barcode) {
      setError('Please enter a barcode.');
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/books/${barcode}/toggle`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, patron_id: patronId })
      });
      const data = await res.json();
      if (res.ok) {
        setStatus(data.message);
        setBarcode('');
      } else {
        setError(data.error || 'Error performing action.');
      }
    } catch (err) {
      setError('Network error.');
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: 600, margin: 'auto' }}>
      <h2>Library System</h2>

      <div>
        <label>Name:</label><br />
        <input value={name} onChange={e => setName(e.target.value)} /><br />
        <label>Phone:</label><br />
        <input value={phone} onChange={e => setPhone(e.target.value)} /><br />
        <button onClick={handleIdentify}>Identify Patron</button>
      </div>

      {isNewPatron && (
        <div style={{ marginTop: '1rem' }}>
          <p>New patron detected. Please enter your email to register:</p>
          <label>Email:</label><br />
          <input value={email} onChange={e => setEmail(e.target.value)} /><br />
          <button onClick={handleRegister}>Register</button>
        </div>
      )}


      {patronId && (
        <div style={{ marginTop: '1.5rem' }}>
          <label>Book Barcode:</label><br />
          <input value={barcode} onChange={e => setBarcode(e.target.value)} /><br />
          <button onClick={() => handleToggle('checkout')}>Check Out</button>
          <button onClick={() => handleToggle('return')} style={{ marginLeft: '1rem' }}>Return</button>
        </div>
      )}

      <div style={{ marginTop: '1rem', color: 'green' }}>{status}</div>
      <div style={{ marginTop: '1rem', color: 'red' }}>{error}</div>
    </div>
  );
}

export default App;
