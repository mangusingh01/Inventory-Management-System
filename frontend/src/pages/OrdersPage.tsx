import { Plus, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { DataTable } from "../components/DataTable";
import { Field, SelectInput, TextInput } from "../components/FormField";
import { EmptyState, ErrorState, LoadingState } from "../components/State";
import { StatusBadge } from "../components/StatusBadge";
import { api, type Customer, type Order, type OrderStatus, type Product } from "../services/api";

type OrderLine = {
  product_id: string;
  quantity: string;
};

export function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [items, setItems] = useState<OrderLine[]>([{ product_id: "", quantity: "1" }]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const productById = useMemo(
    () => new Map(products.map((product) => [product.id, product])),
    [products],
  );
  const customerById = useMemo(
    () => new Map(customers.map((customer) => [customer.id, customer])),
    [customers],
  );

  async function loadData() {
    setIsLoading(true);
    setError(null);
    try {
      const [nextOrders, nextProducts, nextCustomers] = await Promise.all([
        api.orders(),
        api.products(),
        api.customers(),
      ]);
      setOrders(nextOrders);
      setProducts(nextProducts);
      setCustomers(nextCustomers);
    } catch (caught) {
      setError((caught as Error).message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const parsedCustomerId = Number(customerId);
    const parsedItems = items.map((item) => ({
      product_id: Number(item.product_id),
      quantity: Number(item.quantity),
    }));

    if (!parsedCustomerId || parsedItems.some((item) => !item.product_id || item.quantity <= 0)) {
      setError("Select a customer and at least one product with a positive quantity.");
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      await api.createOrder({ customer_id: parsedCustomerId, items: parsedItems });
      setCustomerId("");
      setItems([{ product_id: "", quantity: "1" }]);
      await loadData();
    } catch (caught) {
      setError((caught as Error).message);
    } finally {
      setIsSaving(false);
    }
  }

  async function updateStatus(orderId: number, status: OrderStatus) {
    setError(null);
    try {
      await api.updateOrder(orderId, status);
      await loadData();
    } catch (caught) {
      setError((caught as Error).message);
    }
  }

  async function deleteOrder(orderId: number) {
    setError(null);
    try {
      await api.deleteOrder(orderId);
      await loadData();
    } catch (caught) {
      setError((caught as Error).message);
    }
  }

  function updateLine(index: number, nextLine: Partial<OrderLine>) {
    setItems((current) => current.map((item, currentIndex) => (
      currentIndex === index ? { ...item, ...nextLine } : item
    )));
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h1>Orders</h1>
          <p>Create orders and track fulfillment status.</p>
        </div>
      </header>

      {error && <ErrorState message={error} />}

      <div className="work-grid">
        <form className="panel form-panel" onSubmit={handleSubmit}>
          <div className="panel-header">
            <h2>Create Order</h2>
          </div>
          <Field label="Customer">
            <SelectInput value={customerId} onChange={(event) => setCustomerId(event.target.value)} required>
              <option value="">Select customer</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.first_name} {customer.last_name}
                </option>
              ))}
            </SelectInput>
          </Field>

          {items.map((item, index) => (
            <div className="order-line" key={index}>
              <Field label="Product">
                <SelectInput value={item.product_id} onChange={(event) => updateLine(index, { product_id: event.target.value })} required>
                  <option value="">Select product</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.sku} - {product.name} ({product.quantity} available)
                    </option>
                  ))}
                </SelectInput>
              </Field>
              <Field label="Qty">
                <TextInput min="1" type="number" value={item.quantity} onChange={(event) => updateLine(index, { quantity: event.target.value })} required />
              </Field>
              <button
                aria-label="Remove order line"
                disabled={items.length === 1}
                onClick={() => setItems((current) => current.filter((_, currentIndex) => currentIndex !== index))}
                type="button"
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))}

          <div className="actions">
            <button type="button" onClick={() => setItems([...items, { product_id: "", quantity: "1" }])}>
              Add Line
            </button>
            <button className="primary" disabled={isSaving} type="submit">
              <Plus size={16} />
              Create
            </button>
          </div>
        </form>

        <section className="panel">
          <div className="panel-header">
            <h2>Order List</h2>
            <span>{orders.length} records</span>
          </div>
          {isLoading ? (
            <LoadingState message="Loading orders" />
          ) : orders.length === 0 ? (
            <EmptyState message="No orders found." />
          ) : (
            <DataTable
              columns={[
                { key: "id", label: "Order", render: (row) => `#${row.id}` },
                {
                  key: "customer",
                  label: "Customer",
                  render: (row) => {
                    const customer = customerById.get(row.customer_id);
                    return customer ? `${customer.first_name} ${customer.last_name}` : `#${row.customer_id}`;
                  },
                },
                { key: "items", label: "Items", render: (row) => row.items.map((item) => {
                  const product = productById.get(item.product_id);
                  return `${product?.sku ?? item.product_id} x ${item.quantity}`;
                }).join(", ") },
                { key: "total", label: "Total", render: (row) => `$${row.total_amount}` },
                { key: "status", label: "Status", render: (row) => <StatusBadge status={row.status} /> },
                {
                  key: "actions",
                  label: "",
                  render: (row) => (
                    <div className="row-actions wide">
                      <SelectInput value={row.status} onChange={(event) => void updateStatus(row.id, event.target.value as OrderStatus)}>
                        <option value="pending">Pending</option>
                        <option value="fulfilled">Fulfilled</option>
                        <option value="cancelled">Cancelled</option>
                      </SelectInput>
                      <button aria-label={`Delete order ${row.id}`} onClick={() => void deleteOrder(row.id)} type="button"><Trash2 size={15} /></button>
                    </div>
                  ),
                },
              ]}
              getRowKey={(row) => row.id}
              rows={orders}
            />
          )}
        </section>
      </div>
    </section>
  );
}
