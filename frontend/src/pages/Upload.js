import axios from "axios";
import { useState } from "react";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [roles, setRoles] = useState([]);

  const allRoles = [
    "admin",
    "manager",
    "accountant",
    "employee",
    "worker",
  ];

  const toggleRole = (role) => {
    setRoles((prev) =>
      prev.includes(role)
        ? prev.filter((r) => r !== role)
        : [...prev, role]
    );
  };

  const upload = async () => {
    if (!file || roles.length === 0) {
      alert("Select file and at least one role");
      return;
    }

    // 🔐 Build CP-ABE policy
    const policy = "(" + roles.map(r => `role:${r}`).join(" OR ") + ")";

    const formData = new FormData();
    formData.append("file", file);

    await axios.post(
      `http://127.0.0.1:8000/files/upload?username=${localStorage.getItem("username")}&policy=${policy}`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );

    alert("File uploaded & encrypted");
  };

  return (
    <div className="card">
      <h2>Admin File Upload</h2>

      <input type="file" onChange={(e) => setFile(e.target.files[0])} />

      <h4>Who can access?</h4>
      {allRoles.map((role) => (
        <label key={role} style={{ display: "block" }}>
          <input
            type="checkbox"
            checked={roles.includes(role)}
            onChange={() => toggleRole(role)}
          />
          {role}
        </label>
      ))}

      <button onClick={upload}>Upload Secure File</button>
    </div>
  );
}
