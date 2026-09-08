import { useEffect, useState } from "react";
import api, { Alert } from "../api/client";

export default function Alerts() {
  const [items, setItems] = useState<Alert[]>([]);
  async function load() {
    const { data } = await api.get("/api/alerts");
    setItems(data);
  }
  useEffect(() => { load(); }, []);
  async function markRead(id: number) {
    await api.put(`/api/alerts/${id}/read`);
    load();
  }
  return (
    <div>
      <h2>Price alerts</h2>
      {items.length === 0 && <p>No alerts yet.</p>}
      {items.map((a) => (
        <div key={a.id} className="card" style={{ opacity: a.is_read ? 0.6 : 1 }}>
          <b>{a.product_name}</b>
          <p>{a.message}</p>
          <small>{new Date(a.created_at).toLocaleString()}</small>
          {!a.is_read && <div><button onClick={() => markRead(a.id)}>Mark read</button></div>}
        </div>
      ))}
    </div>
  );
}
