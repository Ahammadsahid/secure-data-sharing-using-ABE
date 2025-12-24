import axios from "axios";
import { useState } from "react";

export default function Admin() {
  const [file, setFile] = useState(null);
  const [roles, setRoles] = useState({
    admin: false,
    manager: false,
    accountant: false,
    employee: false,
    worker: false,
  });

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
        "http://127.0.0.1:8000/files/upload",
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
    <div style={{ padding: "20px" }}>
      <h2>Admin File Upload</h2>

      <input type="file" onChange={e => setFile(e.target.files[0])} />

      <h4>Select Roles</h4>
      {Object.keys(roles).map(r => (
        <label key={r}>
          <input
            type="checkbox"
            checked={roles[r]}
            onChange={e =>
              setRoles({ ...roles, [r]: e.target.checked })
            }
          />
          {r}
          <br />
        </label>
      ))}

      <button onClick={upload}>Upload File</button>
    </div>
  );
}
