import axios from 'axios';
import { useEffect, useState } from 'react';

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
      setMessage('Blockchain not connected. Start Ganache.');
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
      setMessage('Please select a file.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/access/request-key-approval`, {
        file_id: selectedFile,
        user_id: localStorage.getItem('username'),
        user_attributes: {
          role: localStorage.getItem('role'),
          department: localStorage.getItem('department'),
          clearance: localStorage.getItem('clearance')
        }
      });

      setMessage(`Approval request created. Key ID: ${response.data.key_id.substring(0, 10)}...`);
      localStorage.setItem('current_key_id', response.data.key_id);
      
      // Start polling approval status
      pollApprovalStatus(response.data.key_id);
    } catch (error) {
      setMessage('Failed to request approval: ' + error.response?.data?.detail);
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
          setMessage(`Key approved. ${response.data.current_approvals}/${response.data.required_approvals} authorities approved.`);
          clearInterval(interval);
        } else {
          setMessage(`Waiting for approvals: ${response.data.current_approvals}/${response.data.required_approvals}`);
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
      setMessage('No active approval request.');
      return;
    }

    setLoading(true);
    try {
      // In real scenario, each authority would approve individually
      // For demo, we simulate approving from 4 random authorities
      const approvers = authorities.slice(0, 4).map(a => a.address);
      setUserApprovals(approvers);

      await axios.post(`${API_URL}/api/access/simulate-approvals`, {
        key_id: keyId,
        authority_addresses: approvers
      });

      setMessage(`✅ Submitted ${approvers.length} approval transactions on Ganache`);
    } catch (error) {
      setMessage('❌ Error simulating approvals: ' + (error.response?.data?.detail?.message || error.response?.data?.detail || error.message));
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
    <div className="page">
      <div className="container">
        <div className="panel">
          <div className="panel__header">
            <div>
              <h1 className="panel__title">Decentralized access</h1>
              <p className="panel__subtitle">On-chain threshold approvals for decryption</p>
            </div>
            <span className={blockchainStatus ? "badge badge--success" : "badge badge--warning"}>
              {blockchainStatus ? "Connected" : "Not connected"}
            </span>
          </div>

          <div className="section">
            <div className="section__title">Blockchain status</div>
            {blockchainStatus ? (
              <div className="grid grid--2">
                <div className="stat">
                  <div className="stat__label">Network</div>
                  <div className="stat__value">{blockchainStatus.network}</div>
                </div>
                <div className="stat">
                  <div className="stat__label">RPC</div>
                  <div className="stat__value" style={{ wordBreak: "break-all" }}>{blockchainStatus.rpc_url}</div>
                </div>
                <div className="stat" style={{ gridColumn: "1 / -1" }}>
                  <div className="stat__label">Contract</div>
                  <div
                    className="stat__value"
                    style={{
                      fontFamily:
                        "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
                      wordBreak: "break-all",
                    }}
                  >
                    {blockchainStatus.contract_address}
                  </div>
                </div>
              </div>
            ) : (
              <p className="muted" style={{ margin: 0 }}>Blockchain not connected. Start Ganache and refresh.</p>
            )}
          </div>

          <div className="section">
            <div className="section__title">Authorities</div>
            <p className="help">Requires 4 out of 7 approvals to decrypt.</p>
            <div className="grid grid--2">
              {authorities.map((auth, idx) => (
                <div key={`${auth.address}-${idx}`} className="stat">
                  <div className="stat__label">Authority {idx + 1}</div>
                  <div
                    className="stat__value"
                    style={{
                      fontFamily:
                        "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
                    }}
                  >
                    {auth.address.substring(0, 12)}...
                  </div>
                  <p className="help" style={{ marginTop: 8 }}>
                    {auth.is_authority ? <span className="badge badge--success">Active</span> : <span className="badge badge--warning">Inactive</span>}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="section">
            <div className="section__title">Request</div>
            <label htmlFor="dac-file">File ID</label>
            <input
              id="dac-file"
              type="text"
              placeholder="Enter file ID"
              value={selectedFile || ''}
              onChange={(e) => setSelectedFile(e.target.value)}
            />
            <p className="help">Creates an on-chain approval request and starts polling approval status.</p>
            <button onClick={requestKeyApproval} disabled={!selectedFile || loading} className="btn btn--block">
              {loading ? 'Requesting...' : 'Request key approval'}
            </button>
          </div>

          {approvalStatus ? (
            <div className="section">
              <div className="section__title">Approval status</div>
              <div className="grid grid--2">
                <div className="stat">
                  <div className="stat__label">Approvals</div>
                  <div className="stat__value">
                    {approvalStatus.current_approvals} / {approvalStatus.required_approvals}
                  </div>
                </div>
                <div className="stat">
                  <div className="stat__label">Approved?</div>
                  <div className="stat__value">
                    {approvalStatus.is_approved ? <span className="badge badge--success">Approved</span> : <span className="badge badge--warning">Pending</span>}
                  </div>
                </div>
                <div className="stat" style={{ gridColumn: "1 / -1" }}>
                  <div className="stat__label">Progress</div>
                  <div className="stat__value">{approvalStatus.approval_percentage}%</div>
                </div>
              </div>
            </div>
          ) : null}

          <div className="section">
            <div className="section__title">Demo approvals</div>
            <p className="help">For demo purposes, submits 4 approval transactions from known authorities.</p>
            <button onClick={simulateApprovals} disabled={!approvalStatus || loading} className="btn btn--secondary btn--block">
              Simulate 4 approvals
            </button>

            {userApprovals.length > 0 ? (
              <div className="grid grid--2" style={{ marginTop: 12 }}>
                {userApprovals.map((addr, idx) => (
                  <div key={`${addr}-${idx}`} className="stat">
                    <div className="stat__label">Approver</div>
                    <div
                      className="stat__value"
                      style={{
                        fontFamily:
                          "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
                      }}
                    >
                      {addr.substring(0, 12)}...
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
          </div>

          <div className="section">
            <div className="section__title">Decrypt</div>
            <button onClick={decryptFile} disabled={userApprovals.length < 4 || loading} className="btn btn--block">
              {loading ? 'Decrypting...' : 'Decrypt file'}
            </button>
            <p className="help">
              {userApprovals.length < 4 ? `Need ${4 - userApprovals.length} more approvals` : 'Ready to decrypt'}
            </p>
          </div>

          {message ? (
            <div className="section">
              <div className="section__title">Status</div>
              <div className="stat">
                <div className="stat__value">{message}</div>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
