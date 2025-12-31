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
    <div className="page">
      <div className="container">
        <div className="panel">
          <div className="panel__header">
            <div>
              <h1 className="panel__title">Dashboard</h1>
              <p className="panel__subtitle">Secure data sharing workspace</p>
            </div>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "flex-end" }}>
              <button className="btn btn--secondary" onClick={() => navigate("/change-password")}>
                Change password
              </button>
              <button className="btn btn--danger" onClick={handleLogout}>
                Logout
              </button>
            </div>
          </div>

          <div className="section">
            <div className="section__title">Profile</div>
            <div className="grid grid--2">
              <div className="stat">
                <div className="stat__label">User</div>
                <div className="stat__value">{username || "-"}</div>
              </div>
              <div className="stat">
                <div className="stat__label">Status</div>
                <div className="stat__value">
                  <span className="badge badge--success">Authenticated</span>
                </div>
              </div>
              <div className="stat">
                <div className="stat__label">Role</div>
                <div className="stat__value" style={{ textTransform: "capitalize" }}>
                  {role || "-"}
                </div>
              </div>
              <div className="stat">
                <div className="stat__label">Department</div>
                <div className="stat__value">{department || "-"}</div>
              </div>
              <div className="stat">
                <div className="stat__label">Clearance</div>
                <div className="stat__value" style={{ textTransform: "capitalize" }}>
                  {clearance || "-"}
                </div>
              </div>
            </div>
          </div>

          <div className="section">
            <div className="section__title">Actions</div>
            <div className="grid grid--2">
              <div
                className={`tile ${role && role.toLowerCase() === "admin" ? "" : "tile--disabled"}`}
                onClick={() => navigate("/upload")}
                role="button"
                tabIndex={0}
              >
                <p className="tile__title">Upload secure file</p>
                <p className="tile__desc">
                  {role && role.toLowerCase() === "admin"
                    ? "Upload an encrypted file with an access policy"
                    : "Only administrators can upload files"}
                </p>
              </div>

              <div className="tile" onClick={() => navigate("/download")} role="button" tabIndex={0}>
                <p className="tile__title">Request access and download</p>
                <p className="tile__desc">Request approvals, verify signature, then download</p>
              </div>

              {role && role.toLowerCase() === "admin" ? (
                <div className="tile" onClick={() => navigate("/admin/users")} role="button" tabIndex={0}>
                  <p className="tile__title">User management</p>
                  <p className="tile__desc">Create users, add admins, reset passwords</p>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
