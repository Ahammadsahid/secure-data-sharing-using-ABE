import axios from "axios";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Admin() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [roles, setRoles] = useState({
    admin: false,
    manager: false,
    accountant: false,
    employee: false,
    worker: false,
  });

  const backendUrl = "http://127.0.0.1:8000";

  const upload = async () => {
    if (!file) {
      alert("Select a file first");
      return;
    }

    const selectedRoles = Object.keys(roles).filter(r => roles[r]);
    if (selectedRoles.length === 0) {
      alert("Select at least one role");
      return;
    }

    const username = localStorage.getItem("username");

    const formData = new FormData();
    formData.append("file", file);
    formData.append(
      "policy",
      selectedRoles.map(r => `role:${r}`).join(" AND ")
    );
    formData.append("username", username);

    try {
      const res = await axios.post(
        `${backendUrl}/files/upload`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data"
          }
        }
      );

      alert(res.data.message);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Upload failed");
    }
  };


  return (
    <div className="page">
      <div className="container">
        <div className="panel">
          <div className="panel__header">
            <div>
              <h1 className="panel__title">Admin upload</h1>
              <p className="panel__subtitle">Upload an encrypted file with a role-based policy</p>
            </div>
          </div>

          <div className="section">
            <div className="section__title">File</div>
            <label htmlFor="admin-upload-file">Choose file</label>
            <input
              id="admin-upload-file"
              type="file"
              onChange={e => setFile(e.target.files[0])}
            />
            <p className="help">The backend encrypts the file and stores it with the selected access policy.</p>
          </div>

          <div className="section">
            <div className="section__title">Policy</div>
            <p className="help">Select one or more roles. The policy is built as: <span className="muted">role:A AND role:B ...</span></p>

            <div className="grid grid--2">
              {Object.keys(roles).map(r => (
                <div key={r} className="stat">
                  <label style={{ margin: 0, display: "flex", gap: 10, alignItems: "center" }}>
                    <input
                      type="checkbox"
                      checked={roles[r]}
                      onChange={e => setRoles({ ...roles, [r]: e.target.checked })}
                    />
                    <span style={{ fontWeight: 700, textTransform: "capitalize" }}>{r}</span>
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="section">
            <button className="btn btn--block" onClick={upload}>
              Upload file
            </button>
          </div>

          <div className="section">
            <div className="section__title">User management</div>
            <p className="help">Create users, add admins, and reset passwords in a separate page.</p>
            <button className="btn btn--secondary" onClick={() => navigate("/admin/users")}>
              Go to user management
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
