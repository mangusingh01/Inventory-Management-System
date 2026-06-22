const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error("VITE_API_BASE_URL is required.");
}

export type Product = {
  id: number;
  name: string;
  sku: string;
  description: string | null;
  quantity: number;
  price: string;
  created_at: string;
  updated_at: string;
};

export type Customer = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  company: string | null;
  created_at: string;
  updated_at: string;
};

export type OrderStatus = "pending" | "fulfilled" | "cancelled";

export type OrderItem = {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: string;
  line_total: string;
};

export type Order = {
  id: number;
  customer_id: number;
  status: OrderStatus;
  total_amount: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
};

export type Dashboard = {
  total_products: number;
  total_customers: number;
  total_orders: number;
  total_inventory_units: number;
  low_stock_threshold: number;
  low_stock_product_count: number;
  pending_order_count: number;
  fulfilled_order_count: number;
  cancelled_order_count: number;
  active_order_value: string;
  fulfilled_revenue: string;
  low_stock_products: Pick<Product, "id" | "name" | "sku" | "quantity">[];
  recent_orders: Pick<Order, "id" | "customer_id" | "status" | "total_amount" | "created_at">[];
};

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers: options.body === undefined ? undefined : { "Content-Type": "application/json" },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;
    try {
      const data = (await response.json()) as { detail?: string };
      if (data.detail) {
        message = data.detail;
      }
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<Dashboard>("/dashboard"),
  products: () => request<Product[]>("/products"),
  createProduct: (body: Omit<Product, "id" | "created_at" | "updated_at">) =>
    request<Product>("/products", { method: "POST", body }),
  updateProduct: (id: number, body: Partial<Omit<Product, "id" | "created_at" | "updated_at">>) =>
    request<Product>(`/products/${id}`, { method: "PUT", body }),
  deleteProduct: (id: number) => request<void>(`/products/${id}`, { method: "DELETE" }),
  customers: () => request<Customer[]>("/customers"),
  createCustomer: (body: Omit<Customer, "id" | "created_at" | "updated_at">) =>
    request<Customer>("/customers", { method: "POST", body }),
  updateCustomer: (id: number, body: Partial<Omit<Customer, "id" | "created_at" | "updated_at">>) =>
    request<Customer>(`/customers/${id}`, { method: "PUT", body }),
  deleteCustomer: (id: number) => request<void>(`/customers/${id}`, { method: "DELETE" }),
  orders: () => request<Order[]>("/orders"),
  createOrder: (body: { customer_id: number; items: { product_id: number; quantity: number }[] }) =>
    request<Order>("/orders", { method: "POST", body }),
  updateOrder: (id: number, status: OrderStatus) =>
    request<Order>(`/orders/${id}`, { method: "PUT", body: { status } }),
  deleteOrder: (id: number) => request<void>(`/orders/${id}`, { method: "DELETE" }),
};
