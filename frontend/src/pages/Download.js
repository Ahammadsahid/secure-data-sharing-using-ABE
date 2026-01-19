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

  const normalizeToken = (token) => String(token || "").trim().toLowerCase();

  const tokenVariants = (token) => {
    const t = normalizeToken(token);
    if (t.startsWith("department:")) return [t, `dept:${t.split(":")[1] || ""}`];
    if (t.startsWith("dept:")) return [t, `department:${t.split(":")[1] || ""}`];
    return [t];
  };

  const userAttributeSet = () => {
    const role = normalizeToken(`role:${userAttributes.role}`);
    const dept = normalizeToken(`dept:${userAttributes.dept}`);
    const department = normalizeToken(`department:${userAttributes.dept}`);
    const clearance = normalizeToken(`clearance:${userAttributes.clearance}`);
    return new Set([role, dept, department, clearance]);
  };

  const policySatisfied = (policy) => {
    const attrs = userAttributeSet();
    const p = String(policy || "").replace(/\s\s+/g, " ");
    if (!p.trim()) return false;

    const andParts = p.split(" AND ").map((x) => x.trim()).filter(Boolean);
    for (let part of andParts) {
      if (part.startsWith("(") && part.endsWith(")")) part = part.slice(1, -1).trim();
      const orParts = part.split(" OR ").map((x) => x.trim()).filter(Boolean);
      let ok = false;
      for (const orToken of orParts) {
        const variants = tokenVariants(orToken);
        if (variants.some((v) => attrs.has(normalizeToken(v)))) {
          ok = true;
          break;
        }
      }
      if (!ok) return false;
    }
    return true;
  };

  const formatDetail = (detail) => {
    if (!detail) return "Unknown error";
    if (typeof detail === "string") return detail;
    if (typeof detail === "object") {
      return detail.message || detail.reason || JSON.stringify(detail);
    }
    return String(detail);
  };

  const getAxiosErrorMessage = async (err) => {
    if (!err?.response) {
      return (
        err?.message ||
        "Backend not reachable (is FastAPI running on http://127.0.0.1:8000 ?)"
      );
    }

    const data = err?.response?.data;
    try {
      if (data instanceof Blob) {
        const text = await data.text();
        try {
          const parsed = JSON.parse(text);
          return formatDetail(parsed?.detail ?? parsed);
        } catch {
          return text;
        }
      }
    } catch {
    }

    const detail = err?.response?.data?.detail ?? err?.response?.data;
    const msg = formatDetail(detail);
    if (msg && msg !== "Unknown error") return msg;
    return err?.message || `Request failed (HTTP ${err?.response?.status || "?"})`;
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

      console.log("simulateApprovals:", res.data);

      const statusRes = await axios.get(`${API_BASE}/api/access/approval-status/${keyId}`);
      if (statusRes.data?.is_approved) {
        setApprovalStatus("approved");
        alert(`Approved on Ganache (${statusRes.data.current_approvals}/${statusRes.data.required_approvals}).`);
      } else {
        setApprovalStatus("pending");
        alert(
          `Not approved on Ganache yet (${statusRes.data?.current_approvals || 0}/${statusRes.data?.required_approvals || 4}).`
        );
      }
    } catch (err) {
      console.error("SIMULATE ERROR:", err);
      setApprovalStatus("error");
      const detail = err.response?.data?.detail;
      if (detail?.reason === "approval_transactions_failed" && Array.isArray(detail?.results)) {
        const failed = detail.results.filter((r) => !r.tx_hash);
        alert(
          `Approvals failed for ${failed.length} authority(s).\n` +
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
        const star = contentDisposition.match(/filename\*=(?:UTF-8'')?([^;]+)/i);
        if (star && star[1]) {
          try {
            filename = decodeURIComponent(star[1].trim().replace(/^"|"$/g, ""));
          } catch {
          }
        }
        const match = contentDisposition.match(/filename="?(.+)"?/);
        if (match && match[1]) filename = match[1];
      }
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      alert("File downloaded successfully.");
      setSignatureVerified(false);
    } catch (err) {
      alert((await getAxiosErrorMessage(err)) || "Download failed. Check access policy or approvals.");
    } finally {
      setDownloading(false);
    }
  };

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
                  const canAccess = policySatisfied(file.policy);
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

                      <div style={{ marginTop: 10, display: "flex", gap: 8, flexWrap: "wrap" }}>
                        <span className={canAccess ? "badge badge--success" : "badge badge--warning"}>
                          {canAccess ? "Policy matched" : "Policy not matched"}
                        </span>
                        {(file.required_attributes || []).slice(0, 6).map((t) => (
                          <span key={t} className="badge">{t}</span>
                        ))}
                        {(file.required_attributes || []).length > 6 ? (
                          <span className="badge">+{file.required_attributes.length - 6} more</span>
                        ) : null}
                      </div>

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

        </div>
      </div>
    </div>
  );
}
