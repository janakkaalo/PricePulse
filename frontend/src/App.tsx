import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import Layout from "./components/Layout";
import { Login, Register } from "./pages/Auth";
import DashboardPage from "./pages/Dashboard";
import Products from "./pages/Products";
import ProductDetail from "./pages/ProductDetail";
import Alerts from "./pages/Alerts";

function Guard({ children }: { children: JSX.Element }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<Guard><DashboardPage /></Guard>} />
            <Route path="/products" element={<Guard><Products /></Guard>} />
            <Route path="/products/:id" element={<Guard><ProductDetail /></Guard>} />
            <Route path="/alerts" element={<Guard><Alerts /></Guard>} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  );
}
