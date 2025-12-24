import axios from "axios";
import { useState, useEffect } from "react";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [attributes, setAttributes] = useState({
    role: [],
    department: [],
    clearance: []
  });
  const [uploading, setUploading] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  const allRoles = ["admin", "manager", "accountant", "employee", "worker"];
  const allDepartments = ["IT", "Finance", "HR", "Operations"];
  const allClearances = ["high", "medium", "low"];

  useEffect(() => {
    const userRole = localStorage.getItem("role");
    setIsAdmin(userRole && userRole.toLowerCase() === "admin");
  }, []);

  const toggleAttribute = (category, value) => {
    setAttributes((prev) => ({
      ...prev,
      [category]: prev[category].includes(value)
        ? prev[category].filter((v) => v !== value)
        : [...prev[category], value]
    }));
  };

  const upload = async () => {
    if (!file) {
      alert("❌ Please select a file");
      return;
    }

    if (!attributes.role.length || !attributes.department.length || !attributes.clearance.length) {
      alert("❌ Please select at least one value for each attribute");
      return;
    }

    const username = localStorage.getItem("username");
    if (!username) {
      alert("❌ You must be logged in to upload");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Build policy: (role:A OR role:B) AND (dept:X OR dept:Y) AND clearance:Z
    const rolePolicy = attributes.role.map(r => `role:${r}`).join(" OR ");
    const deptPolicy = attributes.department.map(d => `dept:${d}`).join(" OR ");
    const clearancePolicy = attributes.clearance.map(c => `clearance:${c}`).join(" OR ");
    const policy = `(${rolePolicy}) AND (${deptPolicy}) AND (${clearancePolicy})`;

    formData.append("policy", policy);
    formData.append("username", username);

    setUploading(true);
    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/files/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data"
          }
        }
      );

      alert(`✅ File uploaded successfully!\nFile ID: ${res.data.file_id}`);
      setFile(null);
      setAttributes({ role: [], department: [], clearance: [] });
    } catch (err) {
      console.error(err);
      alert("❌ " + (err.response?.data?.detail || "Upload failed"));
    } finally {
      setUploading(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="card" style={{ textAlign: "center", padding: "40px" }}>
        <h2>🔒 Access Denied</h2>
        <p style={{ fontSize: "16px", color: "#666" }}>
          Only administrators can upload files.
        </p>
        <p style={{ fontSize: "14px", color: "#999" }}>
          Your current role: <strong>{localStorage.getItem("role") || "Unknown"}</strong>
        </p>
      </div>
    );
  }

  return (
    <div className="card" style={{ maxWidth: "600px", margin: "0 auto" }}>
      <h2 style={{ color: "#2c3e50", marginBottom: "20px" }}>📤 Secure File Upload</h2>

      {/* File Input */}
      <div style={{ marginBottom: "20px" }}>
        <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold", color: "#34495e" }}>
          Select File
        </label>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          style={{
            padding: "10px",
            border: "2px solid #bdc3c7",
            borderRadius: "5px",
            width: "100%",
            boxSizing: "border-box",
            cursor: "pointer"
          }}
        />
        {file && <p style={{ color: "#27ae60", marginTop: "5px" }}>✓ {file.name}</p>}
      </div>

      {/* Roles */}
      <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#ecf0f1", borderRadius: "5px" }}>
        <label style={{ display: "block", marginBottom: "10px", fontWeight: "bold", color: "#34495e" }}>
          🔐 Who can access? (By Role)
        </label>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
          {allRoles.map((role) => (
            <label key={role} style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={attributes.role.includes(role)}
                onChange={() => toggleAttribute("role", role)}
                style={{ marginRight: "8px", cursor: "pointer" }}
              />
              <span style={{ textTransform: "capitalize" }}>{role}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Departments */}
      <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#ecf0f1", borderRadius: "5px" }}>
        <label style={{ display: "block", marginBottom: "10px", fontWeight: "bold", color: "#34495e" }}>
          🏢 Departments
        </label>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
          {allDepartments.map((dept) => (
            <label key={dept} style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={attributes.department.includes(dept)}
                onChange={() => toggleAttribute("department", dept)}
                style={{ marginRight: "8px", cursor: "pointer" }}
              />
              {dept}
            </label>
          ))}
        </div>
      </div>

      {/* Clearance Levels */}
      <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#ecf0f1", borderRadius: "5px" }}>
        <label style={{ display: "block", marginBottom: "10px", fontWeight: "bold", color: "#34495e" }}>
          🔑 Clearance Level
        </label>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px" }}>
          {allClearances.map((level) => (
            <label key={level} style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={attributes.clearance.includes(level)}
                onChange={() => toggleAttribute("clearance", level)}
                style={{ marginRight: "8px", cursor: "pointer" }}
              />
              <span style={{ textTransform: "capitalize" }}>{level}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Upload Button */}
      <button
        onClick={upload}
        disabled={uploading || !file}
        style={{
          width: "100%",
          padding: "12px",
          backgroundColor: uploading || !file ? "#bdc3c7" : "#27ae60",
          color: "white",
          border: "none",
          borderRadius: "5px",
          fontSize: "16px",
          fontWeight: "bold",
          cursor: uploading || !file ? "not-allowed" : "pointer",
          transition: "background-color 0.3s"
        }}
        onMouseOver={(e) => !uploading && !file && (e.target.style.backgroundColor = "#229954")}
        onMouseOut={(e) => !uploading && !file && (e.target.style.backgroundColor = "#27ae60")}
      >
        {uploading ? "⏳ Uploading..." : "✅ Upload Secure File"}
      </button>

      {/* Info */}
      <div style={{ marginTop: "20px", padding: "12px", backgroundColor: "#d5f4e6", borderRadius: "5px", fontSize: "13px", color: "#16a085" }}>
        <strong>ℹ️ How it works:</strong>
        <p style={{ margin: "5px 0 0 0" }}>
          Files are encrypted using AES-256. Only users matching ALL selected attributes can decrypt them.
        </p>
      </div>
    </div>
  );
}
