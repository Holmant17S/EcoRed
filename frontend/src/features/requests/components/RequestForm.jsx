import { useState } from "react";

const INITIAL_FORM = Object.freeze({
  company_id: "",
  material_id: "",
  quantity: "",
  message: "",
});

export default function RequestForm({ companies, materials, onSubmit }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = ({ target }) => {
    setForm((current) => ({ ...current, [target.name]: target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit({
        company_id: form.company_id,
        material_id: form.material_id,
        quantity: Number(form.quantity),
        message: form.message.trim(),
      });
      setForm(INITIAL_FORM);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formDisabled =
    isSubmitting || companies.length === 0 || materials.length === 0;

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-3">
        <label htmlFor="request-company" className="form-label">
          Empresa solicitante
        </label>
        <select
          id="request-company"
          name="company_id"
          className="form-select"
          value={form.company_id}
          onChange={handleChange}
          required
          disabled={formDisabled}
        >
          <option value="">Seleccione empresa</option>
          {companies.map((company) => (
            <option key={company.id} value={company.id}>
              {company.name}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-3">
        <label htmlFor="request-material" className="form-label">
          Material
        </label>
        <select
          id="request-material"
          name="material_id"
          className="form-select"
          value={form.material_id}
          onChange={handleChange}
          required
          disabled={formDisabled}
        >
          <option value="">Seleccione material</option>
          {materials.map((item) => (
            <option key={item.id} value={item.id}>
              {item.material_type} ({item.quantity} {item.unit})
            </option>
          ))}
        </select>
      </div>

      <div className="mb-3">
        <label htmlFor="request-quantity" className="form-label">
          Cantidad solicitada
        </label>
        <input
          id="request-quantity"
          type="number"
          name="quantity"
          className="form-control"
          min="0.01"
          step="any"
          value={form.quantity}
          onChange={handleChange}
          required
          disabled={formDisabled}
        />
      </div>

      <div className="mb-4">
        <label htmlFor="request-message" className="form-label">
          Mensaje
        </label>
        <textarea
          id="request-message"
          name="message"
          className="form-control"
          rows={3}
          value={form.message}
          onChange={handleChange}
          disabled={formDisabled}
        />
      </div>

      <div className="d-grid">
        <button type="submit" className="btn btn-warning" disabled={formDisabled}>
          {isSubmitting ? "Enviando…" : "Crear solicitud"}
        </button>
      </div>
    </form>
  );
}
