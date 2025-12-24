import axios from 'axios';
import { useEffect, useState } from 'react';
import './DecentralizedAccess.css';

const API_URL = 'http://localhost:8000';

export default function DecentralizedAccess() {
  const [blockchainStatus, setBlockchainStatus] = useState(null);
  const [authorities, setAuthorities] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [approvalStatus, setApprovalStatus] = useState(null);
  const [userApprovals, setUserApprovals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    checkBlockchain();
    getAuthorities();
  }, []);

  const checkBlockchain = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/access/blockchain/status`);
      setBlockchainStatus(response.data);
    } catch (error) {
      setMessage('❌ Blockchain not connected. Start Ganache!');
      console.error(error);
    }
  };

  const getAuthorities = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/access/authorities`);
      setAuthorities(response.data.authorities);
    } catch (error) {
      console.error('Failed to get authorities:', error);
    }
  };

  const requestKeyApproval = async () => {
    if (!selectedFile) {
      setMessage('⚠️ Please select a file');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/access/request-key-approval`, {
        file_id: selectedFile,
        user_id: localStorage.getItem('user_id'),
        user_attributes: {
          role: localStorage.getItem('user_role'),
          department: localStorage.getItem('user_department'),
          clearance: localStorage.getItem('user_clearance')
        }
      });

      setMessage(`✅ Approval request created! Key ID: ${response.data.key_id.substring(0, 10)}...`);
      localStorage.setItem('current_key_id', response.data.key_id);
      
      // Start polling approval status
      pollApprovalStatus(response.data.key_id);
    } catch (error) {
      setMessage('❌ Failed to request approval: ' + error.response?.data?.detail);
    } finally {
      setLoading(false);
    }
  };

  const pollApprovalStatus = async (keyId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_URL}/api/access/approval-status/${keyId}`);
        setApprovalStatus(response.data);

        if (response.data.is_approved) {
          setMessage(`🎉 Key approved! ${response.data.current_approvals}/${response.data.required_approvals} authorities approved`);
          clearInterval(interval);
        } else {
          setMessage(`⏳ Waiting for approvals: ${response.data.current_approvals}/${response.data.required_approvals}`);
        }
      } catch (error) {
        clearInterval(interval);
      }
    }, 3000);
  };

  const simulateApprovals = async () => {
    // Simulate authorities approving the request
    const keyId = localStorage.getItem('current_key_id');
    if (!keyId) {
      setMessage('⚠️ No active approval request');
      return;
    }

    setLoading(true);
    try {
      // In real scenario, each authority would approve individually
      // For demo, we simulate approving from 4 random authorities
      const approvers = authorities.slice(0, 4).map(a => a.address);
      setUserApprovals(approvers);
      setMessage(`✅ Simulated ${approvers.length} authority approvals`);
    } catch (error) {
      setMessage('❌ Error simulating approvals');
    } finally {
      setLoading(false);
    }
  };

  const decryptFile = async () => {
    const keyId = localStorage.getItem('current_key_id');
    if (!keyId || userApprovals.length < 4) {
      setMessage('⚠️ Need at least 4 approvals to decrypt');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/access/decrypt`, {
        file_id: selectedFile,
        key_id: keyId,
        approving_authorities: userApprovals
      });

      if (response.data.decrypted) {
        setMessage(`✅ File decrypted successfully! Key: ${response.data.decryption_key?.substring(0, 16)}...`);
      } else {
        setMessage('❌ ' + response.data.message);
      }
    } catch (error) {
      setMessage('❌ Decryption failed: ' + error.response?.data?.detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="decentralized-container">
      <h2>🔐 Decentralized Access Control</h2>

      {/* Blockchain Status */}
      <div className="status-card">
        <h3>Blockchain Status</h3>
        {blockchainStatus ? (
          <div className="status-content">
            <p>✅ <strong>Connected</strong> to {blockchainStatus.network}</p>
            <p>📍 Contract: <code>{blockchainStatus.contract_address}</code></p>
            <p>🔗 RPC: {blockchainStatus.rpc_url}</p>
          </div>
        ) : (
          <p>❌ Not connected. Start Ganache!</p>
        )}
      </div>

      {/* Authorities List */}
      <div className="authorities-card">
        <h3>🏛️ Authorities (7/7)</h3>
        <p className="requirement">⚡ <strong>Requires 4 out of 7 approvals to decrypt</strong></p>
        <div className="authorities-list">
          {authorities.map((auth, idx) => (
            <div key={idx} className="authority-item">
              <span className="index">{idx + 1}</span>
              <span className="address">{auth.address.substring(0, 12)}...</span>
              <span className={`status ${auth.is_authority ? 'active' : 'inactive'}`}>
                {auth.is_authority ? '✅ Active' : '⚪ Inactive'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Approval Process */}
      <div className="approval-card">
        <h3>📋 Approval Process</h3>
        
        <div className="file-selection">
          <label>Select File:</label>
          <input
            type="text"
            placeholder="Enter file ID"
            value={selectedFile || ''}
            onChange={(e) => setSelectedFile(e.target.value)}
          />
        </div>

        <div className="step-indicator">
          <div className={`step ${selectedFile ? 'active' : ''}`}>1. Select File</div>
          <div className={`step ${approvalStatus?.current_approvals > 0 ? 'active' : ''}`}>2. Request Approval</div>
          <div className={`step ${approvalStatus?.is_approved ? 'active' : ''}`}>3. Wait for 4/7</div>
          <div className={`step ${userApprovals.length >= 4 ? 'active' : ''}`}>4. Decrypt</div>
        </div>

        <button 
          onClick={requestKeyApproval} 
          disabled={!selectedFile || loading}
          className="btn-primary"
        >
          🚀 {loading ? 'Requesting...' : 'Request Key Approval'}
        </button>
      </div>

      {/* Approval Status */}
      {approvalStatus && (
        <div className="approval-status-card">
          <h3>⏳ Approval Status</h3>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${approvalStatus.approval_percentage}%` }}
            ></div>
          </div>
          <p className="approval-count">
            {approvalStatus.current_approvals} / {approvalStatus.required_approvals} approvals
            {approvalStatus.is_approved && ' ✅ APPROVED!'}
          </p>
          <p className="approval-percentage">{approvalStatus.approval_percentage}% Complete</p>
        </div>
      )}

      {/* Authority Approvals Simulation (Demo Only) */}
      <div className="simulation-card">
        <h3>📝 Demo: Simulate Authority Approvals</h3>
        <p className="hint">In production, authorities approve via blockchain transactions</p>
        <button 
          onClick={simulateApprovals} 
          disabled={!approvalStatus || loading}
          className="btn-secondary"
        >
          👥 Simulate 4 Approvals
        </button>
        
        {userApprovals.length > 0 && (
          <div className="approved-list">
            <h4>Approving Authorities:</h4>
            {userApprovals.map((addr, idx) => (
              <p key={idx}>✅ {addr.substring(0, 12)}...</p>
            ))}
          </div>
        )}
      </div>

      {/* Decryption */}
      <div className="decrypt-card">
        <h3>🔓 Decrypt File</h3>
        <button 
          onClick={decryptFile}
          disabled={userApprovals.length < 4 || loading}
          className="btn-success"
        >
          🔐 {loading ? 'Decrypting...' : 'Decrypt File'}
        </button>
        <p className="requirement">
          {userApprovals.length < 4 ? `Need ${4 - userApprovals.length} more approvals` : '✅ Ready to decrypt'}
        </p>
      </div>

      {/* Messages */}
      {message && (
        <div className={`message ${message.includes('❌') ? 'error' : message.includes('✅') ? 'success' : 'info'}`}>
          {message}
        </div>
      )}
    </div>
  );
}
