import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import api, { PricePoint, Product } from "../api/client";

export default function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [history, setHistory] = useState<PricePoint[]>([]);

  async function load() {
    const p = await api.get(`/api/products/${id}`);
    setProduct(p.data);
    const h = await api.get(`/api/products/${id}/history?days=90`);
    setHistory(h.data);
  }
  useEffect(() => { load(); }, [id]);

  async function recheck() {
    await api.post(`/api/products/${id}/check-now`);
    load();
  }

  if (!product) return <p>Loading…</p>;
  const chart = history.map((pt) => ({
    price: pt.price,
    date: new Date(pt.checked_at).toLocaleDateString()
  }));

  return (
    <div>
      <h2>{product.name}</h2>
      <p><a href={product.url} target="_blank" rel="noreferrer">{product.url}</a></p>
      <p>Current ${product.current_price} — Target ${product.target_price} {product.deal && "🎉 DEAL"}</p>
      <button onClick={recheck}>Check price now</button>
      <div style={{ height: 300, marginTop: 16 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chart}>
            <XAxis dataKey="date" />
            <YAxis domain={["auto", "auto"]} />
            <Tooltip />
            <Line type="monotone" dataKey="price" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
