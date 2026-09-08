import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { Product } from "../api/client";

export default function Products() {
  const [items, setItems] = useState<Product[]>([]);
  const [form, setForm] = useState({ name: "", url: "", target_price: "" });

  async function load() {
    const { data } = await api.get("/api/products");
    setItems(data);
  }
  useEffect(() => { load(); }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    await api.post("/api/products", {
      name: form.name, url: form.url, target_price: parseFloat(form.target_price)
    });
    setForm({ name: "", url: "", target_price: "" });
    load();
  }

  async function remove(id: number) {
    await api.delete(`/api/products/${id}`);
    load();
  }

  return (
    <div>
      <h2>Tracked products</h2>
      <form className="card row" onSubmit={add}>
        <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <input placeholder="https://..." value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} required />
        <input placeholder="Target $" value={form.target_price} onChange={(e) => setForm({ ...form, target_price: e.target.value })} required />
        <button type="submit">Track</button>
      </form>
      <div className="grid">
        {items.map((p) => (
          <div key={p.id} className="card">
            <Link to={`/products/${p.id}`}><b>{p.name}</b></Link>
            <div>Current: {p.current_price ?? "—"} | Target: ${p.target_price}</div>
            {p.deal && <span className="badge">DEAL 🎉</span>}
            <div><button onClick={() => remove(p.id)}>Remove</button></div>
          </div>
        ))}
      </div>
    </div>
  );
}
