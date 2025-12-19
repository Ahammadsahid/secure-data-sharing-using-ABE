import axios from "axios";
import { useState } from "react";

export default function Download() {
  const [fileId, setFileId] = useState("");

  const download = async () => {
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/files/download/${fileId}?username=${localStorage.getItem("username")}`
      );
      alert("File decrypted successfully");
      console.log(res.data);
    } catch {
      alert("Access Denied");
    }
  };

  return (
    <div className="card">
      <h2>Download Secure File</h2>
      <input placeholder="File ID" onChange={e => setFileId(e.target.value)} />
      <button onClick={download}>Download</button>
    </div>
  );
}
