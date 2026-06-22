import { BarChart3, Boxes, ClipboardList, Users } from "lucide-react";
import { useState } from "react";

import { CustomersPage } from "./pages/CustomersPage";
import { DashboardPage } from "./pages/DashboardPage";
import { OrdersPage } from "./pages/OrdersPage";
import { ProductsPage } from "./pages/ProductsPage";

type PageKey = "dashboard" | "products" | "customers" | "orders";

const pages: { key: PageKey; label: string; icon: typeof BarChart3 }[] = [
  { key: "dashboard", label: "Dashboard", icon: BarChart3 },
  { key: "products", label: "Products", icon: Boxes },
  { key: "customers", label: "Customers", icon: Users },
  { key: "orders", label: "Orders", icon: ClipboardList },
];

export default function App() {
  const [activePage, setActivePage] = useState<PageKey>("dashboard");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Boxes aria-hidden="true" size={28} />
          <div>
            <strong>Inventory</strong>
            <span>Operations</span>
          </div>
        </div>
        <nav aria-label="Main navigation">
          {pages.map((page) => {
            const Icon = page.icon;
            return (
              <button
                className={activePage === page.key ? "nav-item active" : "nav-item"}
                key={page.key}
                onClick={() => setActivePage(page.key)}
                type="button"
              >
                <Icon aria-hidden="true" size={18} />
                <span>{page.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="content">
        {activePage === "dashboard" && <DashboardPage />}
        {activePage === "products" && <ProductsPage />}
        {activePage === "customers" && <CustomersPage />}
        {activePage === "orders" && <OrdersPage />}
      </main>
    </div>
  );
}
