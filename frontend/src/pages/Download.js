
import axios from "axios";
import { useEffect, useState } from "react";


export default function Download() {
  const [files, setFiles] = useState([]);
  const [username] = useState(localStorage.getItem("username") || "");
  const [userAttributes] = useState({
    role: localStorage.getItem("role") || "user",
    dept: localStorage.getItem("department") || "IT",
    clearance: localStorage.getItem("clearance") || "medium",
  });
  const [requesting, setRequesting] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [keyId, setKeyId] = useState("");
  const [authorities, setAuthorities] = useState([]);
  const [approvalStatus, setApprovalStatus] = useState("pending");
  const [selectedFile, setSelectedFile] = useState(null);
  const [signatureVerified, setSignatureVerified] = useState(false);

  const API_BASE = "http://127.0.0.1:8000";

  const formatDetail = (detail) => {
    if (!detail) return "Unknown error";
    if (typeof detail === "string") return detail;
    if (typeof detail === "object") {
      return detail.message || detail.reason || JSON.stringify(detail);
    }
    return String(detail);
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/files/all`);
      setFiles(res.data);
    } catch (err) {
      setFiles([]);
    }
  };


  const requestApproval = async (file) => {
    setSelectedFile(file);
    setRequesting(true);
    setApprovalStatus("pending");
    try {
      const res = await axios.post(`${API_BASE}/api/access/request-key-approval`, {
        file_id: String(file.id),
        user_id: username,
        user_attributes: userAttributes,
      });
      setKeyId(res.data.key_id);
      setAuthorities(res.data.authorities || []);
      setApprovalStatus("key_received");
      alert("Key approval request created successfully.");
    } catch (err) {
      setApprovalStatus("error");
      alert(formatDetail(err.response?.data?.detail) || "Failed to request approval.");
    } finally {
      setRequesting(false);
    }
  };

  const simulateApprovals = async () => {
    if (!keyId || authorities.length === 0) {
      alert("No key or authorities available.");
      return;
    }

    setSimulating(true);
    try {
      const toApprove = authorities.slice(0, 4);

      const res = await axios.post(`${API_BASE}/api/access/simulate-approvals`, {
        key_id: keyId,
        authority_addresses: toApprove,
      });

      console.log("SIMULATE RESULT:", res.data);

      // Verify on-chain status (this is what actually matters)
      const statusRes = await axios.get(`${API_BASE}/api/access/approval-status/${keyId}`);
      if (statusRes.data?.is_approved) {
        setApprovalStatus("approved");
        alert(`✅ Approved on Ganache (${statusRes.data.current_approvals}/${statusRes.data.required_approvals}).`);
      } else {
        setApprovalStatus("pending");
        alert(
          `⚠️ Not approved on Ganache yet (${statusRes.data?.current_approvals || 0}/${statusRes.data?.required_approvals || 4}).`
        );
      }
    } catch (err) {
      console.error("SIMULATE ERROR:", err);
      setApprovalStatus("error");
      const detail = err.response?.data?.detail;
      if (detail?.reason === "approval_transactions_failed" && Array.isArray(detail?.results)) {
        const failed = detail.results.filter((r) => !r.tx_hash);
        alert(
          `❌ Approvals failed for ${failed.length} authority(s).\n` +
            failed.map((f) => `${f.authority}: ${f.error || "failed"}`).join("\n")
        );
      } else {
        alert(formatDetail(detail) || "Simulation failed.");
      }
    } finally {
      setSimulating(false);
    }
  };


  const download = async () => {
    if (!selectedFile || !username || !keyId) {
      alert("Please request approval first.");
      return;
    }
    if (approvalStatus !== "approved") {
      alert("Please get approvals first.");
      return;
    }
    if (!signatureVerified) {
      alert("Please verify your signature with MetaMask before downloading.");
      return;
    }
    setDownloading(true);
    try {
      const res = await axios.get(`${API_BASE}/files/download/${selectedFile.id}`, {
        params: { username, key_id: keyId },
        responseType: "blob",
      });
      const contentType = res.headers["content-type"] || "application/octet-stream";
      const blob = new Blob([res.data], { type: contentType });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      const contentDisposition = res.headers["content-disposition"];
      let filename = selectedFile.filename || `secure_file_${selectedFile.id}`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?(.+)"?/);
        if (match && match[1]) filename = match[1];
      }
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      alert("✅ File downloaded and decrypted successfully!");
      setSignatureVerified(false); // Reset after download
    } catch (err) {
      alert("❌ " + (formatDetail(err.response?.data?.detail) || "Download failed. Check access policy or approvals."));
    } finally {
      setDownloading(false);
    }
  };


  // Signature verification using MetaMask

  const verifySignature = async () => {
    if (!window.ethereum) {
      alert("MetaMask is not installed.");
      return;
    }
    if (!selectedFile || !selectedFile.id) {
      alert("Please select a file first.");
      return;
    }
    try {
      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts"
      });
      const fileId = selectedFile.id;
      const message = `Approve access for file ${fileId}`;
      const signature = await window.ethereum.request({
        method: "personal_sign",
        params: [message, accounts[0]]
      });
      const payload = {
        message: message,
        signature: signature,
        address: accounts[0],
        file_id: fileId,
        user_attributes: userAttributes
      };
      console.log("VERIFY SIGNATURE PAYLOAD:", payload);
      const res = await axios.post(
        "http://127.0.0.1:8000/api/access/verify-signature",
        payload
      );
      if (res.data && res.data.verified) {
        setSignatureVerified(true);
        alert("Signature verified successfully! You can now download the file.");
      } else {
        setSignatureVerified(false);
        alert(`Signature verification failed: ${res.data?.reason || "unknown"}`);
      }
    } catch (err) {
      setSignatureVerified(false);
      alert(`Signature verification failed: ${err.response?.data?.reason || err.response?.data?.detail || err.message || "unknown"}`);
    }
  };

  // const getProgressColor = () => {
  //   if (approvalStatus === "pending") return "#95a5a6";
  //   if (approvalStatus === "key_received") return "#f39c12";
  //   if (approvalStatus === "approved") return "#27ae60";
  //   return "#e74c3c";
  // };


  return (
    <div className="page">
      <div className="container">
        <div className="panel">
          <div className="panel__header">
            <div>
              <h1 className="panel__title">Download</h1>
              <p className="panel__subtitle">Request approvals, verify signature, then download</p>
            </div>
            <span className={signatureVerified ? "badge badge--success" : "badge badge--warning"}>
              {signatureVerified ? "Signature verified" : "Signature not verified"}
            </span>
          </div>

          <div className="section">
            <div className="section__title">Available files</div>
            {files.length === 0 ? (
              <p className="muted" style={{ margin: 0 }}>No files available.</p>
            ) : (
              <div className="grid grid--2">
                {files.map((file) => {
                  const isSelected = selectedFile && selectedFile.id === file.id;
                  const isRequested = isSelected && approvalStatus !== "pending";
                  return (
                    <div
                      key={file.id}
                      className="tile"
                      onClick={() => setSelectedFile(file)}
                      role="button"
                      tabIndex={0}
                    >
                      <p className="tile__title">{file.filename}</p>
                      <p className="tile__desc">
                        Owner: <span className="muted">{file.owner}</span>
                        {isSelected ? " · Selected" : ""}
                      </p>

                      <div style={{ marginTop: 12, display: "flex", gap: 10 }}>
                        <button
                          className="btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            requestApproval(file);
                          }}
                          disabled={requesting || isRequested}
                        >
                          {requesting && isSelected ? "Requesting..." : isRequested ? "Requested" : "Request approval"}
                        </button>
                        {isSelected ? <span className="badge">Selected</span> : null}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="section">
            <div className="section__title">Your attributes</div>
            <div className="grid grid--2">
              <div className="stat">
                <div className="stat__label">Role</div>
                <div className="stat__value" style={{ textTransform: "capitalize" }}>{userAttributes.role}</div>
              </div>
              <div className="stat">
                <div className="stat__label">Department</div>
                <div className="stat__value">{userAttributes.dept}</div>
              </div>
              <div className="stat">
                <div className="stat__label">Clearance</div>
                <div className="stat__value" style={{ textTransform: "capitalize" }}>{userAttributes.clearance}</div>
              </div>
              <div className="stat">
                <div className="stat__label">User</div>
                <div className="stat__value">{username || "-"}</div>
              </div>
            </div>
          </div>

          <div className="section">
            <div className="section__title">Access flow</div>

            <div className="grid grid--2">
              <div className="stat">
                <div className="stat__label">Step 1</div>
                <div className="stat__value">Request key approval</div>
                <p className="help" style={{ marginTop: 8 }}>
                  Select a file, then request approval to obtain a key ID.
                </p>
                <button
                  className="btn btn--block"
                  onClick={() => {
                    if (!selectedFile) {
                      alert("Please select a file first.");
                      return;
                    }
                    requestApproval(selectedFile);
                  }}
                  disabled={requesting || !selectedFile || approvalStatus !== "pending"}
                >
                  {requesting ? "Requesting..." : approvalStatus !== "pending" ? "Requested" : "Request approval"}
                </button>
              </div>

              <div className="stat">
                <div className="stat__label">Step 2</div>
                <div className="stat__value">Collect 4-of-7 approvals</div>
                <p className="help" style={{ marginTop: 8 }}>
                  Approvals are recorded on-chain (Ganache).
                </p>
                <button
                  className="btn btn--block"
                  onClick={simulateApprovals}
                  disabled={simulating || approvalStatus === "pending" || approvalStatus === "approved"}
                >
                  {simulating ? "Simulating..." : approvalStatus === "approved" ? "Approved" : "Simulate approvals"}
                </button>
              </div>

              <div className="stat">
                <div className="stat__label">Step 3</div>
                <div className="stat__value">Verify signature</div>
                <p className="help" style={{ marginTop: 8 }}>
                  Uses MetaMask personal signature for request integrity.
                </p>
                <button className="btn btn--block" onClick={verifySignature} disabled={!selectedFile?.id}>
                  Verify with MetaMask
                </button>
              </div>

              <div className="stat">
                <div className="stat__label">Step 4</div>
                <div className="stat__value">Download and decrypt</div>
                <p className="help" style={{ marginTop: 8 }}>
                  Requires on-chain approval and a verified signature.
                </p>
                <button
                  className="btn btn--block"
                  onClick={download}
                  disabled={downloading || approvalStatus !== "approved" || !signatureVerified}
                >
                  {downloading ? "Downloading..." : "Download"}
                </button>
              </div>
            </div>
          </div>

          {keyId ? (
            <div className="section">
              <div className="section__title">Blockchain details</div>
              <div className="grid grid--2">
                <div className="stat">
                  <div className="stat__label">Key ID</div>
                  <div className="stat__value" style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace", wordBreak: "break-all" }}>
                    {keyId}
                  </div>
                </div>
                <div className="stat">
                  <div className="stat__label">Authorities</div>
                  <div className="stat__value">{authorities.length}/7</div>
                  <div style={{ marginTop: 10, maxHeight: 160, overflowY: "auto" }}>
                    {authorities.map((a, i) => (
                      <div
                        key={a}
                        className="muted"
                        style={{
                          padding: "6px 0",
                          borderBottom: i < authorities.length - 1 ? "1px solid var(--border)" : "none",
                          fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
                          fontSize: 12,
                          wordBreak: "break-all",
                        }}
                      >
                        {i + 1}. {a}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : null}

          <div className="section">
            <div className="section__title">Security note</div>
            <p className="muted" style={{ margin: 0 }}>
              Files are encrypted with AES-256 + attribute-based policy checks. Download requires 4-of-7 authority approvals on-chain.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
