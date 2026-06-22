import { Edit3, Plus, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { DataTable } from "../components/DataTable";
import { Field, TextArea, TextInput } from "../components/FormField";
import { EmptyState, ErrorState, LoadingState } from "../components/State";
import { api, type Product } from "../services/api";

type ProductForm = {
  name: string;
  sku: string;
  description: string;
  quantity: string;
  price: string;
};

const emptyForm: ProductForm = { name: "", sku: "", description: "", quantity: "0", price: "0.00" };

export function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [form, setForm] = useState<ProductForm>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  async function loadProducts() {
    setIsLoading(true);
    setError(null);
    try {
      setProducts(await api.products());
    } catch (caught) {
      setError((caught as Error).message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadProducts();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const quantity = Number(form.quantity);
    const price = Number(form.price);
    if (!form.name.trim() || !form.sku.trim() || quantity < 0 || price < 0) {
      setError("Name, SKU, non-negative quantity, and non-negative price are required.");
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      const payload = {
        name: form.name.trim(),
        sku: form.sku.trim(),
        description: form.description.trim() || null,
        quantity,
        price: price.toFixed(2),
      };
      if (editingId === null) {
        await api.createProduct(payload);
      } else {
        await api.updateProduct(editingId, payload);
      }
      setForm(emptyForm);
      setEditingId(null);
      await loadProducts();
    } catch (caught) {
      setError((caught as Error).message);
    } finally {
      setIsSaving(false);
    }
  }

  function editProduct(product: Product) {
    setEditingId(product.id);
    setForm({
      name: product.name,
      sku: product.sku,
      description: product.description ?? "",
      quantity: String(product.quantity),
      price: product.price,
    });
  }

  async function deleteProduct(id: number) {
    setError(null);
    try {
      await api.deleteProduct(id);
      await loadProducts();
    } catch (caught) {
      setError((caught as Error).message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h1>Products</h1>
          <p>Manage SKU, price, and on-hand inventory.</p>
        </div>
      </header>

      {error && <ErrorState message={error} />}

      <div className="work-grid">
        <form className="panel form-panel" onSubmit={handleSubmit}>
          <div className="panel-header">
            <h2>{editingId === null ? "Add Product" : "Edit Product"}</h2>
          </div>
          <Field label="Name">
            <TextInput value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
          </Field>
          <Field label="SKU">
            <TextInput value={form.sku} onChange={(event) => setForm({ ...form, sku: event.target.value })} required />
          </Field>
          <Field label="Description">
            <TextArea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} rows={3} />
          </Field>
          <div className="form-row">
            <Field label="Quantity">
              <TextInput min="0" type="number" value={form.quantity} onChange={(event) => setForm({ ...form, quantity: event.target.value })} required />
            </Field>
            <Field label="Price">
              <TextInput min="0" step="0.01" type="number" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} required />
            </Field>
          </div>
          <div className="actions">
            <button className="primary" disabled={isSaving} type="submit">
              <Plus size={16} />
              {editingId === null ? "Create" : "Save"}
            </button>
            {editingId !== null && (
              <button type="button" onClick={() => { setEditingId(null); setForm(emptyForm); }}>
                Cancel
              </button>
            )}
          </div>
        </form>

        <section className="panel">
          <div className="panel-header">
            <h2>Product List</h2>
            <span>{products.length} records</span>
          </div>
          {isLoading ? (
            <LoadingState message="Loading products" />
          ) : products.length === 0 ? (
            <EmptyState message="No products found." />
          ) : (
            <DataTable
              columns={[
                { key: "sku", label: "SKU", render: (row) => row.sku },
                { key: "name", label: "Name", render: (row) => row.name },
                { key: "quantity", label: "Qty", render: (row) => row.quantity },
                { key: "price", label: "Price", render: (row) => `$${row.price}` },
                {
                  key: "actions",
                  label: "",
                  render: (row) => (
                    <div className="row-actions">
                      <button aria-label={`Edit ${row.name}`} onClick={() => editProduct(row)} type="button"><Edit3 size={15} /></button>
                      <button aria-label={`Delete ${row.name}`} onClick={() => void deleteProduct(row.id)} type="button"><Trash2 size={15} /></button>
                    </div>
                  ),
                },
              ]}
              getRowKey={(row) => row.id}
              rows={products}
            />
          )}
        </section>
      </div>
    </section>
  );
}
