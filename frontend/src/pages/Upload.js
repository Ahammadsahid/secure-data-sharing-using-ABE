import axios from "axios";
import { useState } from "react";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [policy, setPolicy] = useState("role:admin");

  const upload = async () => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("policy", policy);

    await axios.post("http://127.0.0.1:8000/files/upload", formData);
    alert("File uploaded");
  };

  return (
    <div className="container">
      <h2>Upload File</h2>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <input
        placeholder="Policy"
        value={policy}
        onChange={(e) => setPolicy(e.target.value)}
      />
      <button onClick={upload}>Upload</button>
    </div>
  );
}
