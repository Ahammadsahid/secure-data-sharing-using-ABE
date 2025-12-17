import { Link } from "react-router-dom";

export default function Dashboard() {
  return (
    <div className="container">
      <h2>Dashboard</h2>
      <Link to="/upload">Upload File</Link><br />
      <Link to="/admin">Admin Panel</Link>
    </div>
  );
}
