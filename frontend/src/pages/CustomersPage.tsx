import { Edit3, Plus, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { DataTable } from "../components/DataTable";
import { Field, TextInput } from "../components/FormField";
import { EmptyState, ErrorState, LoadingState } from "../components/State";
import { api, type Customer } from "../services/api";

type CustomerForm = {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  company: string;
};

const emptyForm: CustomerForm = { first_name: "", last_name: "", email: "", phone: "", company: "" };

export function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [form, setForm] = useState<CustomerForm>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  async function loadCustomers() {
    setIsLoading(true);
    setError(null);
    try {
      setCustomers(await api.customers());
    } catch (caught) {
      setError((caught as Error).message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadCustomers();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!form.first_name.trim() || !form.last_name.trim() || !form.email.includes("@")) {
      setError("First name, last name, and a valid email are required.");
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      const payload = {
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim() || null,
        company: form.company.trim() || null,
      };
      if (editingId === null) {
        await api.createCustomer(payload);
      } else {
        await api.updateCustomer(editingId, payload);
      }
      setForm(emptyForm);
      setEditingId(null);
      await loadCustomers();
    } catch (caught) {
      setError((caught as Error).message);
    } finally {
      setIsSaving(false);
    }
  }

  function editCustomer(customer: Customer) {
    setEditingId(customer.id);
    setForm({
      first_name: customer.first_name,
      last_name: customer.last_name,
      email: customer.email,
      phone: customer.phone ?? "",
      company: customer.company ?? "",
    });
  }

  async function deleteCustomer(id: number) {
    setError(null);
    try {
      await api.deleteCustomer(id);
      await loadCustomers();
    } catch (caught) {
      setError((caught as Error).message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h1>Customers</h1>
          <p>Maintain customer contact records for order creation.</p>
        </div>
      </header>

      {error && <ErrorState message={error} />}

      <div className="work-grid">
        <form className="panel form-panel" onSubmit={handleSubmit}>
          <div className="panel-header">
            <h2>{editingId === null ? "Add Customer" : "Edit Customer"}</h2>
          </div>
          <div className="form-row">
            <Field label="First name">
              <TextInput value={form.first_name} onChange={(event) => setForm({ ...form, first_name: event.target.value })} required />
            </Field>
            <Field label="Last name">
              <TextInput value={form.last_name} onChange={(event) => setForm({ ...form, last_name: event.target.value })} required />
            </Field>
          </div>
          <Field label="Email">
            <TextInput type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
          </Field>
          <div className="form-row">
            <Field label="Phone">
              <TextInput value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
            </Field>
            <Field label="Company">
              <TextInput value={form.company} onChange={(event) => setForm({ ...form, company: event.target.value })} />
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
            <h2>Customer List</h2>
            <span>{customers.length} records</span>
          </div>
          {isLoading ? (
            <LoadingState message="Loading customers" />
          ) : customers.length === 0 ? (
            <EmptyState message="No customers found." />
          ) : (
            <DataTable
              columns={[
                { key: "name", label: "Name", render: (row) => `${row.first_name} ${row.last_name}` },
                { key: "email", label: "Email", render: (row) => row.email },
                { key: "company", label: "Company", render: (row) => row.company ?? "-" },
                {
                  key: "actions",
                  label: "",
                  render: (row) => (
                    <div className="row-actions">
                      <button aria-label={`Edit ${row.email}`} onClick={() => editCustomer(row)} type="button"><Edit3 size={15} /></button>
                      <button aria-label={`Delete ${row.email}`} onClick={() => void deleteCustomer(row.id)} type="button"><Trash2 size={15} /></button>
                    </div>
                  ),
                },
              ]}
              getRowKey={(row) => row.id}
              rows={customers}
            />
          )}
        </section>
      </div>
    </section>
  );
}
