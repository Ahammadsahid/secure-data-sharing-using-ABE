import axios from "axios";
import { useState, useEffect } from "react";

export default function Download() {
  const [fileId, setFileId] = useState("");
  const [username, setUsername] = useState(localStorage.getItem("username") || "");
  const [requesting, setRequesting] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [keyId, setKeyId] = useState("");
  const [authorities, setAuthorities] = useState([]);
  const [userAttributes, setUserAttributes] = useState({
    role: "",
    department: "",
    clearance: ""
  });
  const [approvalStatus, setApprovalStatus] = useState("pending");

  const API_BASE = "http://127.0.0.1:8000";

  useEffect(() => {
    setUserAttributes({
      role: localStorage.getItem("role") || "admin",
      department: localStorage.getItem("department") || "IT",
      clearance: localStorage.getItem("clearance") || "high"
    });
  }, []);

  const requestApproval = async () => {
    if (!fileId || !username) {
      alert("❌ Please enter File ID and username");
      return;
    }

    setRequesting(true);
    setApprovalStatus("pending");
    try {
      const res = await axios.post(`${API_BASE}/api/access/request-key-approval`, {
        file_id: String(fileId),
        user_id: username,
        user_attributes: userAttributes,
      });

      setKeyId(res.data.key_id);
      setAuthorities(res.data.authorities || []);
      setApprovalStatus("key_received");
      alert("✅ Key approval request created successfully!");
    } catch (err) {
      console.error("REQUEST ERROR:", err);
      setApprovalStatus("error");
      alert("❌ " + (err.response?.data?.detail || "Failed to request approval"));
    } finally {
      setRequesting(false);
    }
  };

  const simulateApprovals = async () => {
    if (!keyId || authorities.length === 0) {
      alert("❌ No key or authorities available");
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
      setApprovalStatus("approved");
      alert("✅ 4-of-7 approvals simulated successfully!");
    } catch (err) {
      console.error("SIMULATE ERROR:", err);
      setApprovalStatus("error");
      alert("❌ " + (err.response?.data?.detail || "Simulation failed"));
    } finally {
      setSimulating(false);
    }
  };

  const download = async () => {
    if (!fileId || !username || !keyId) {
      alert("❌ Please request approval first");
      return;
    }

    if (approvalStatus !== "approved") {
      alert("❌ Please get approvals first");
      return;
    }

    setDownloading(true);
    try {
      const res = await axios.get(`${API_BASE}/files/download/${fileId}`, {
        params: { username, key_id: keyId },
        responseType: "blob",
      });

      const contentType = res.headers["content-type"] || "application/octet-stream";
      const blob = new Blob([res.data], { type: contentType });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      const contentDisposition = res.headers["content-disposition"];
      let filename = `secure_file_${fileId}`;
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
    } catch (err) {
      console.error("DOWNLOAD ERROR:", err);
      alert("❌ " + (err.response?.data?.detail || "Download failed. Check access policy or approvals."));
    } finally {
      setDownloading(false);
    }
  };

  const getProgressColor = () => {
    if (approvalStatus === "pending") return "#95a5a6";
    if (approvalStatus === "key_received") return "#f39c12";
    if (approvalStatus === "approved") return "#27ae60";
    return "#e74c3c";
  };

  return (
    <div className="card" style={{ maxWidth: "700px", margin: "0 auto" }}>
      <h2 style={{ color: "#2c3e50", marginBottom: "20px" }}>📥 Download Secure File</h2>

      {/* File ID and Username Inputs */}
      <div style={{ marginBottom: "20px" }}>
        <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold", color: "#34495e" }}>
          📄 File ID
        </label>
        <input
          type="text"
          placeholder="Enter file ID (e.g., 1)"
          value={fileId}
          onChange={(e) => setFileId(e.target.value)}
          style={{
            width: "100%",
            padding: "10px",
            border: "2px solid #bdc3c7",
            borderRadius: "5px",
            boxSizing: "border-box",
            fontSize: "14px"
          }}
        />
      </div>

      <div style={{ marginBottom: "20px" }}>
        <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold", color: "#34495e" }}>
          👤 Username
        </label>
        <input
          type="text"
          placeholder="Enter username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled
          style={{
            width: "100%",
            padding: "10px",
            border: "2px solid #bdc3c7",
            borderRadius: "5px",
            boxSizing: "border-box",
            fontSize: "14px",
            backgroundColor: "#ecf0f1",
            cursor: "not-allowed"
          }}
        />
      </div>

      {/* User Attributes Display */}
      <div style={{ marginBottom: "20px", padding: "12px", backgroundColor: "#e8f4f8", borderRadius: "5px" }}>
        <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold", color: "#2980b9" }}>
          🔐 Your Attributes
        </label>
        <div style={{ fontSize: "13px", color: "#34495e" }}>
          <p style={{ margin: "4px 0" }}>
            <strong>Role:</strong> {userAttributes.role}
          </p>
          <p style={{ margin: "4px 0" }}>
            <strong>Department:</strong> {userAttributes.department}
          </p>
          <p style={{ margin: "4px 0" }}>
            <strong>Clearance:</strong> {userAttributes.clearance}
          </p>
        </div>
      </div>

      {/* Step-by-step Flow */}
      <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#f8f9fa", borderRadius: "5px", border: "2px solid #dee2e6" }}>
        <h4 style={{ marginTop: 0, color: "#2c3e50", marginBottom: "15px" }}>🔄 Access Flow (3 Steps)</h4>

        {/* Step 1 */}
        <div style={{ marginBottom: "12px" }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "10px",
            backgroundColor: approvalStatus !== "pending" ? "#d5f4e6" : "#fff9e6",
            borderRadius: "5px",
            border: "1px solid #bdc3c7"
          }}>
            <span style={{ fontWeight: "bold", color: "#34495e" }}>
              Step 1: {approvalStatus !== "pending" ? "✅" : "⏳"} Request Approval
            </span>
            <button
              onClick={requestApproval}
              disabled={requesting || approvalStatus !== "pending"}
              style={{
                padding: "8px 16px",
                backgroundColor: requesting ? "#bdc3c7" : approvalStatus !== "pending" ? "#27ae60" : "#3498db",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: requesting || approvalStatus !== "pending" ? "not-allowed" : "pointer",
                fontSize: "12px",
                fontWeight: "bold"
              }}
            >
              {requesting ? "⏳ Requesting..." : approvalStatus !== "pending" ? "✅ Done" : "Start"}
            </button>
          </div>
        </div>

        {/* Step 2 */}
        <div style={{ marginBottom: "12px" }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "10px",
            backgroundColor: approvalStatus === "approved" ? "#d5f4e6" : approvalStatus === "key_received" ? "#fff9e6" : "#f5f5f5",
            borderRadius: "5px",
            border: "1px solid #bdc3c7",
            opacity: approvalStatus === "pending" ? 0.5 : 1
          }}>
            <span style={{ fontWeight: "bold", color: "#34495e" }}>
              Step 2: {approvalStatus === "approved" ? "✅" : "⏳"} Simulate Approvals (4-of-7)
            </span>
            <button
              onClick={simulateApprovals}
              disabled={simulating || approvalStatus === "pending" || approvalStatus === "approved"}
              style={{
                padding: "8px 16px",
                backgroundColor: simulating ? "#bdc3c7" : approvalStatus === "approved" ? "#27ae60" : approvalStatus === "key_received" ? "#f39c12" : "#95a5a6",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: simulating || approvalStatus === "pending" || approvalStatus === "approved" ? "not-allowed" : "pointer",
                fontSize: "12px",
                fontWeight: "bold"
              }}
            >
              {simulating ? "⏳ Simulating..." : approvalStatus === "approved" ? "✅ Done" : "Start"}
            </button>
          </div>
        </div>

        {/* Step 3 */}
        <div style={{ marginBottom: 0 }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "10px",
            backgroundColor: approvalStatus === "approved" ? "#d5f4e6" : "#f5f5f5",
            borderRadius: "5px",
            border: "1px solid #bdc3c7",
            opacity: approvalStatus !== "approved" ? 0.5 : 1
          }}>
            <span style={{ fontWeight: "bold", color: "#34495e" }}>
              Step 3: 📥 Download Decrypted File
            </span>
            <button
              onClick={download}
              disabled={downloading || approvalStatus !== "approved"}
              style={{
                padding: "8px 16px",
                backgroundColor: downloading ? "#bdc3c7" : approvalStatus === "approved" ? "#27ae60" : "#95a5a6",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: downloading || approvalStatus !== "approved" ? "not-allowed" : "pointer",
                fontSize: "12px",
                fontWeight: "bold"
              }}
            >
              {downloading ? "⏳ Downloading..." : "Download"}
            </button>
          </div>
        </div>
      </div>

      {/* Key ID and Authorities */}
      {keyId && (
        <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#f0f3f7", borderRadius: "5px", border: "2px solid #3498db" }}>
          <h4 style={{ marginTop: 0, color: "#2980b9", marginBottom: "10px" }}>🔑 Blockchain Details</h4>
          <div style={{ marginBottom: "10px" }}>
            <label style={{ fontWeight: "bold", color: "#34495e", fontSize: "12px" }}>Key ID:</label>
            <p style={{
              margin: "5px 0 0 0",
              padding: "8px",
              backgroundColor: "white",
              borderRadius: "3px",
              wordBreak: "break-all",
              fontSize: "12px",
              fontFamily: "monospace",
              color: "#2c3e50"
            }}>
              {keyId}
            </p>
          </div>

          <div>
            <label style={{ fontWeight: "bold", color: "#34495e", fontSize: "12px" }}>
              🏛️ Authorities ({authorities.length}/7):
            </label>
            <div style={{
              margin: "8px 0 0 0",
              padding: "8px",
              backgroundColor: "white",
              borderRadius: "3px",
              maxHeight: "150px",
              overflowY: "auto",
              fontSize: "12px"
            }}>
              {authorities.map((a, i) => (
                <div key={a} style={{
                  padding: "5px",
                  borderBottom: i < authorities.length - 1 ? "1px solid #ecf0f1" : "none",
                  fontFamily: "monospace",
                  color: "#555"
                }}>
                  {i + 1}. {a}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Security Info */}
      <div style={{ padding: "12px", backgroundColor: "#fffacd", borderRadius: "5px", fontSize: "12px", color: "#856404", border: "1px solid #ffeaa7" }}>
        <strong>ℹ️ Security Note:</strong>
        <p style={{ margin: "5px 0 0 0" }}>
          Files are encrypted with AES-256 + ABE. You can only access files matching your attributes. The blockchain requires 4-of-7 authority approvals.
        </p>
      </div>
    </div>
  );
}
