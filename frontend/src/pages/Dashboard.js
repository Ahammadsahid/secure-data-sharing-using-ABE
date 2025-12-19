import { Link } from "react-router-dom";

export default function Dashboard() {
  return (
    <div className="card">
      <h2>Secure Data Sharing Dashboard</h2>

      <p>Welcome, {localStorage.getItem("username")}</p>

      <div className="actions">
        <Link to="/upload">Upload File (Admin)</Link>
        <Link to="/download">Download Files</Link>
      </div>
    </div>
  );
}
