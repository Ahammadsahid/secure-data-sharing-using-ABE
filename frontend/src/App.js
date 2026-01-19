import { BrowserRouter, Route, Routes } from "react-router-dom";
import Admin from "./pages/Admin";
import AdminUsers from "./pages/AdminUsers";
import Dashboard from "./pages/Dashboard";
import DecentralizedAccess from "./pages/DecentralizedAccess";
import Download from "./pages/Download";
import Login from "./pages/Login";
import Upload from "./pages/Upload";
import ForgotPassword from "./pages/ForgotPassword";
import ChangePassword from "./pages/ChangePassword";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/change-password" element={<ChangePassword />} />

        <Route path="/admin" element={<Admin />} />
        <Route path="/admin/users" element={<AdminUsers />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/access" element={<DecentralizedAccess />} />

        <Route path="/upload" element={<Upload />} />
        <Route path="/download" element={<Download />} />
      </Routes>
    </BrowserRouter>
  );
}
