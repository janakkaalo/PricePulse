import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { Dashboard, Product } from "../api/client";

export default function DashboardPage() {
  const [stats, setStats] = useState<Dashboard | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  useEffect(() => {
    api.get("/api/stats/dashboard").then((r) => setStats(r.data)).catch(() => {});
    api.get("/api/products").then((r) => setProducts(r.data)).catch(() => {});
  }, []);
  const deals = products.filter((p) => p.deal);
  return (
    <div>
      <h2>Dashboard</h2>
      {stats && (
        <div className="grid">
          <div className="stat"><span>Total tracked</span><b>{stats.total_products}</b></div>
          <div className="stat"><span>Active</span><b>{stats.active_products}</b></div>
          <div className="stat"><span>Unread alerts</span><b>{stats.active_alerts}</b></div>
          <div className="stat"><span>Avg price</span><b>{stats.avg_current_price ?? "—"}</b></div>
        </div>
      )}
      <h3>🔥 Deals ({deals.length})</h3>
      {deals.length === 0 && <p>No deals yet. Add a product with a target price above current price.</p>}
      <div className="grid">
        {deals.map((p) => (
          <Link key={p.id} className="card" to={`/products/${p.id}`}>
            <b>{p.name}</b>
            <div>${p.current_price} <s>${p.target_price}</s> target</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
