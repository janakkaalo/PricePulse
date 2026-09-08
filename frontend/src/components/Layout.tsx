import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Layout({ children }: { children: React.ReactNode }) {
  const { token, logout } = useAuth();
  const nav = useNavigate();
  return (
    <div className="shell">
      <nav className="nav">
        <Link to="/" className="brand">⚡ PricePulse</Link>
        <div className="links">
          {token ? (
            <>
              <Link to="/">Dashboard</Link>
              <Link to="/products">Products</Link>
              <Link to="/alerts">Alerts</Link>
              <button onClick={() => { logout(); nav("/login"); }}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </div>
      </nav>
      <main className="main">{children}</main>
    </div>
  );
}
