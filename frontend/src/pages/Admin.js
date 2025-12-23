import axios from "axios";
import { useState } from "react";

export default function Admin() {
  const [file, setFile] = useState(null);
  const [roles, setRoles] = useState({
    admin: false,
    manager: false,
    accountant: false,
    worker: false,
  });

  const upload = async () => {
    console.log("UPLOAD CLICKED");

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
      selectedRoles.map(r => `role:${r}`).join(" OR ")
    );
    formData.append("username", username);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/files/upload",
        formData
      );
      alert(res.data.message);
    } catch (err) {
      console.error("UPLOAD ERROR:", err);
      if (err.response) {
        alert(err.response.data.detail);
      } else {
        alert("Frontend crash prevented. Check console.");
      }
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>ADMIN PANEL LOADED</h1>
      <h2>Admin Upload Panel</h2>

      <input type="file" onChange={e => setFile(e.target.files[0])} />

      <h4>Select who can access</h4>

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

      <br />
      <button onClick={upload}>Upload File</button>
    </div>
  );
}
