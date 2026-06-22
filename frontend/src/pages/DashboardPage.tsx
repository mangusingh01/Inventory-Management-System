import { DollarSign, PackageCheck, ShoppingCart, Users } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { DataTable } from "../components/DataTable";
import { EmptyState, ErrorState, LoadingState } from "../components/State";
import { StatusBadge } from "../components/StatusBadge";
import { api, type Dashboard } from "../services/api";

export function DashboardPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .dashboard()
      .then(setDashboard)
      .catch((caught: Error) => setError(caught.message))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return <LoadingState message="Loading dashboard" />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (!dashboard) {
    return <EmptyState message="No dashboard data available." />;
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Current inventory, customer, and order activity.</p>
        </div>
      </header>

      <div className="metric-grid">
        <Metric label="Products" value={dashboard.total_products} icon={<PackageCheck size={18} />} />
        <Metric label="Customers" value={dashboard.total_customers} icon={<Users size={18} />} />
        <Metric label="Orders" value={dashboard.total_orders} icon={<ShoppingCart size={18} />} />
        <Metric label="Active order value" value={`$${dashboard.active_order_value}`} icon={<DollarSign size={18} />} />
      </div>

      <div className="split-grid">
        <section className="panel">
          <div className="panel-header">
            <h2>Low Stock</h2>
            <span>{dashboard.low_stock_product_count} at or below {dashboard.low_stock_threshold}</span>
          </div>
          {dashboard.low_stock_products.length === 0 ? (
            <EmptyState message="No low-stock products." />
          ) : (
            <DataTable
              columns={[
                { key: "sku", label: "SKU", render: (row) => row.sku },
                { key: "name", label: "Name", render: (row) => row.name },
                { key: "quantity", label: "Qty", render: (row) => row.quantity },
              ]}
              getRowKey={(row) => row.id}
              rows={dashboard.low_stock_products}
            />
          )}
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Recent Orders</h2>
            <span>{dashboard.pending_order_count} pending</span>
          </div>
          {dashboard.recent_orders.length === 0 ? (
            <EmptyState message="No recent orders." />
          ) : (
            <DataTable
              columns={[
                { key: "id", label: "Order", render: (row) => `#${row.id}` },
                { key: "customer", label: "Customer", render: (row) => `#${row.customer_id}` },
                { key: "status", label: "Status", render: (row) => <StatusBadge status={row.status} /> },
                { key: "total", label: "Total", render: (row) => `$${row.total_amount}` },
              ]}
              getRowKey={(row) => row.id}
              rows={dashboard.recent_orders}
            />
          )}
        </section>
      </div>
    </section>
  );
}

function Metric({ label, value, icon }: { label: string; value: string | number; icon: ReactNode }) {
  return (
    <div className="metric">
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
