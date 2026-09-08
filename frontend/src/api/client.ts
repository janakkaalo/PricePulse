import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("pp_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export interface Product {
  id: number;
  name: string;
  url: string;
  target_price: number;
  current_price: number | null;
  image_url: string | null;
  is_active: boolean;
  created_at: string;
  deal: boolean;
}

export interface PricePoint {
  id: number;
  price: number;
  checked_at: string;
}

export interface Alert {
  id: number;
  product_id: number;
  product_name: string;
  trigger_price: number;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface Dashboard {
  total_products: number;
  active_products: number;
  active_alerts: number;
  avg_current_price: number | null;
  best_deal_product_id: number | null;
}

export default api;
