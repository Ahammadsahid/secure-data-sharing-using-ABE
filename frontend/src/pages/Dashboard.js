import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username");
  const role = localStorage.getItem("role");
  const department = localStorage.getItem("department");
  const clearance = localStorage.getItem("clearance");

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <div className="card" style={{ maxWidth: "800px", margin: "0 auto" }}>
      <h2 style={{ color: "#2c3e50", marginBottom: "20px" }}>📊 Secure Data Sharing Dashboard</h2>

      {/* Welcome Section */}
      <div style={{
        padding: "20px",
        backgroundColor: "#e8f4f8",
        borderRadius: "8px",
        marginBottom: "30px",
        border: "2px solid #3498db"
      }}>
        <h3 style={{ marginTop: 0, color: "#2980b9" }}>👋 Welcome, {username}!</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px", marginTop: "15px", fontSize: "14px" }}>
          <div>
            <label style={{ fontWeight: "bold", color: "#34495e" }}>Role:</label>
            <p style={{ margin: "5px 0 0 0", color: "#555", textTransform: "capitalize" }}>{role}</p>
          </div>
          <div>
            <label style={{ fontWeight: "bold", color: "#34495e" }}>Department:</label>
            <p style={{ margin: "5px 0 0 0", color: "#555" }}>{department}</p>
          </div>
          <div>
            <label style={{ fontWeight: "bold", color: "#34495e" }}>Clearance Level:</label>
            <p style={{ margin: "5px 0 0 0", color: "#555", textTransform: "capitalize" }}>{clearance}</p>
          </div>
          <div>
            <label style={{ fontWeight: "bold", color: "#34495e" }}>Status:</label>
            <p style={{ margin: "5px 0 0 0", color: "#27ae60" }}>🟢 Authenticated</p>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div style={{ marginBottom: "30px" }}>
        <h3 style={{ color: "#2c3e50", marginBottom: "15px" }}>🎯 Available Actions</h3>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
          {/* Upload Card */}
          <div
            onClick={() => navigate("/upload")}
            style={{
              padding: "20px",
              backgroundColor: role && role.toLowerCase() === "admin" ? "#fff9e6" : "#f5f5f5",
              border: role && role.toLowerCase() === "admin" ? "2px solid #f39c12" : "2px solid #ccc",
              borderRadius: "8px",
              cursor: role && role.toLowerCase() === "admin" ? "pointer" : "not-allowed",
              transition: "all 0.3s ease",
              opacity: role && role.toLowerCase() === "admin" ? 1 : 0.6
            }}
            onMouseOver={(e) => {
              if (role && role.toLowerCase() === "admin") {
                e.currentTarget.style.boxShadow = "0 4px 12px rgba(243, 156, 18, 0.3)";
                e.currentTarget.style.transform = "translateY(-4px)";
              }
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.boxShadow = "none";
              e.currentTarget.style.transform = "translateY(0)";
            }}
          >
            <h4 style={{ marginTop: 0, marginBottom: "8px" }}>📤 Upload Secure File</h4>
            <p style={{ fontSize: "13px", color: "#666", margin: 0 }}>
              {role && role.toLowerCase() === "admin"
                ? "Encrypt and upload files with attribute-based access control"
                : "Only administrators can upload files"}
            </p>
          </div>

          {/* Download Card */}
          <div
            onClick={() => navigate("/download")}
            style={{
              padding: "20px",
              backgroundColor: "#e8f4f8",
              border: "2px solid #3498db",
              borderRadius: "8px",
              cursor: "pointer",
              transition: "all 0.3s ease"
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.boxShadow = "0 4px 12px rgba(52, 152, 219, 0.3)";
              e.currentTarget.style.transform = "translateY(-4px)";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.boxShadow = "none";
              e.currentTarget.style.transform = "translateY(0)";
            }}
          >
            <h4 style={{ marginTop: 0, marginBottom: "8px" }}>📥 Download & Decrypt File</h4>
            <p style={{ fontSize: "13px", color: "#666", margin: 0 }}>
              Request approvals and download files you have access to
            </p>
          </div>
        </div>
      </div>

      {/* Security Info */}
      <div style={{
        padding: "15px",
        backgroundColor: "#d5f4e6",
        borderRadius: "8px",
        borderLeft: "4px solid #27ae60",
        marginBottom: "20px"
      }}>
        <strong style={{ color: "#27ae60" }}>🔐 Security Features</strong>
        <ul style={{ margin: "8px 0 0 0", paddingLeft: "20px", color: "#555", fontSize: "13px" }}>
          <li>AES-256 Encryption for all files</li>
          <li>Attribute-Based Encryption (ABE) for access control</li>
          <li>Blockchain-verified 4-of-7 threshold approvals</li>
          <li>Immutable audit trail on Ganache</li>
        </ul>
      </div>

      {/* Logout Button */}
      <button
        onClick={handleLogout}
        style={{
          width: "100%",
          padding: "12px",
          backgroundColor: "#e74c3c",
          marginTop: 0
        }}
        onMouseOver={(e) => e.target.style.backgroundColor = "#c0392b"}
        onMouseOut={(e) => e.target.style.backgroundColor = "#e74c3c"}
      >
        🚪 Logout
      </button>
    </div>
  );
}
