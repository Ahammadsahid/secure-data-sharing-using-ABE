import axios from "axios";
import { useEffect, useState } from "react";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [attributes, setAttributes] = useState({
    role: [],
    department: [],
    clearance: []
  });
  const [files, setFiles] = useState([]);
  const [filesLoading, setFilesLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  const allRoles = ["admin", "manager", "accountant", "employee", "worker"];
  const allDepartments = ["IT", "Finance", "HR", "Operations"];
  const allClearances = ["high", "medium", "low"];

  useEffect(() => {
    const userRole = localStorage.getItem("role");
    setIsAdmin(userRole && userRole.toLowerCase() === "admin");
  }, []);

  useEffect(() => {
    if (!isAdmin) return;
    fetchFiles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin]);

  const fetchFiles = async () => {
    setFilesLoading(true);
    try {
      const res = await axios.get("http://127.0.0.1:8000/files/all");
      setFiles(res.data || []);
    } catch (err) {
      setFiles([]);
    } finally {
      setFilesLoading(false);
    }
  };

  const deleteFile = async (fileId) => {
    const username = localStorage.getItem("username");
    if (!username) {
      alert("You must be logged in.");
      return;
    }
    const ok = window.confirm("Delete this file permanently? This cannot be undone.");
    if (!ok) return;

    try {
      await axios.delete(`http://127.0.0.1:8000/files/${fileId}`, {
        params: { username },
      });
      await fetchFiles();
      alert("File deleted.");
    } catch (err) {
      alert(err.response?.data?.detail || "Delete failed.");
    }
  };

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
      alert("Please select a file.");
      return;
    }

    if (!attributes.role.length || !attributes.department.length || !attributes.clearance.length) {
      alert("Please select at least one value for each attribute.");
      return;
    }

    const username = localStorage.getItem("username");
    if (!username) {
      alert("You must be logged in to upload.");
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

      alert(`File uploaded successfully.\nFile ID: ${res.data.file_id}`);
      setFile(null);
      setAttributes({ role: [], department: [], clearance: [] });
      await fetchFiles();
    } catch (err) {
      console.error(err);
      alert((err.response?.data?.detail || "Upload failed."));
    } finally {
      setUploading(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="page">
        <div className="container">
          <div className="panel">
            <div className="panel__header">
              <div>
                <h1 className="panel__title">Upload</h1>
                <p className="panel__subtitle">Administrators only</p>
              </div>
              <span className="badge badge--warning">Access denied</span>
            </div>
            <p className="muted" style={{ margin: 0 }}>
              Your current role: <strong>{localStorage.getItem("role") || "Unknown"}</strong>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <div className="panel">
          <div className="panel__header">
            <div>
              <h1 className="panel__title">Upload</h1>
              <p className="panel__subtitle">Encrypt and upload files with an access policy</p>
            </div>
          </div>

          <div className="section">
            <div className="section__title">File</div>
            <label htmlFor="upload-file">Select file</label>
            <input id="upload-file" type="file" onChange={(e) => setFile(e.target.files[0])} />
            {file ? (
              <p className="help">
                Selected: <span className="badge">{file.name}</span>
              </p>
            ) : (
              <p className="help">Choose a file to encrypt and upload.</p>
            )}
          </div>

          <div className="section">
            <div className="section__title">Who can access?</div>
            <p className="help">Pick one or more values in each category.</p>

            <div className="grid grid--2">
              <div className="stat">
                <div className="stat__label">Roles</div>
                <div style={{ marginTop: 10 }}>
                  {allRoles.map((role) => (
                    <label key={role} style={{ marginBottom: 8, display: "flex", gap: 10, alignItems: "center" }}>
                      <input
                        type="checkbox"
                        checked={attributes.role.includes(role)}
                        onChange={() => toggleAttribute("role", role)}
                      />
                      <span style={{ textTransform: "capitalize", fontWeight: 700 }}>{role}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="stat">
                <div className="stat__label">Departments</div>
                <div style={{ marginTop: 10 }}>
                  {allDepartments.map((dept) => (
                    <label key={dept} style={{ marginBottom: 8, display: "flex", gap: 10, alignItems: "center" }}>
                      <input
                        type="checkbox"
                        checked={attributes.department.includes(dept)}
                        onChange={() => toggleAttribute("department", dept)}
                      />
                      <span style={{ fontWeight: 700 }}>{dept}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="stat">
                <div className="stat__label">Clearance</div>
                <div style={{ marginTop: 10 }}>
                  {allClearances.map((level) => (
                    <label key={level} style={{ marginBottom: 8, display: "flex", gap: 10, alignItems: "center" }}>
                      <input
                        type="checkbox"
                        checked={attributes.clearance.includes(level)}
                        onChange={() => toggleAttribute("clearance", level)}
                      />
                      <span style={{ textTransform: "capitalize", fontWeight: 700 }}>{level}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="stat">
                <div className="stat__label">Generated policy</div>
                <p className="help" style={{ marginTop: 10 }}>
                  This upload creates a policy like:
                </p>
                <p className="muted" style={{ margin: 0, wordBreak: "break-word" }}>
                  ({attributes.role.map(r => `role:${r}`).join(" OR ") || "role:?"}) AND ({attributes.department.map(d => `dept:${d}`).join(" OR ") || "dept:?"}) AND ({attributes.clearance.map(c => `clearance:${c}`).join(" OR ") || "clearance:?"})
                </p>
              </div>
            </div>
          </div>

          <div className="section">
            <button className="btn btn--block" onClick={upload} disabled={uploading || !file}>
              {uploading ? "Uploading..." : "Upload"}
            </button>
          </div>

          <div className="section">
            <div className="section__title">Manage files</div>
            <p className="help">Admins can delete uploaded files. This removes the encrypted blob and database record.</p>

            {filesLoading ? (
              <p className="muted" style={{ margin: 0 }}>Loading files...</p>
            ) : files.length === 0 ? (
              <p className="muted" style={{ margin: 0 }}>No files uploaded yet.</p>
            ) : (
              <div className="grid grid--2">
                {files.map((f) => (
                  <div key={f.id} className="stat">
                    <div className="stat__label">{f.filename}</div>
                    <div className="stat__value" style={{ fontSize: 13, fontWeight: 600 }}>
                      Owner: <span className="muted">{f.owner}</span>
                    </div>
                    <p className="help" style={{ marginTop: 8, wordBreak: "break-word" }}>
                      Policy: <span className="muted">{f.policy}</span>
                    </p>
                    <div style={{ marginTop: 10, display: "flex", gap: 10 }}>
                      <span className="badge">ID: {f.id}</span>
                      <button className="btn btn--danger" onClick={() => deleteFile(f.id)}>
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
