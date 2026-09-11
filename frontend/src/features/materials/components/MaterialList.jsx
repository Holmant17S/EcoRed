/**
 * Lista presentacional de publicaciones de materiales.
 */
export default function MaterialList({ items }) {
  if (items.length === 0) {
    return (
      <p className="text-muted mb-0">No hay publicaciones registradas todavía.</p>
    );
  }

  return (
    <div className="list-group list-group-flush">
      {items.map((item) => (
        <article key={item.id} className="list-group-item px-0 py-3">
          <div className="d-flex justify-content-between gap-3 flex-wrap">
            <div>
              <h3 className="h6 mb-1">{item.material_type}</h3>
              <p className="mb-1">
                Cantidad: {item.quantity} {item.unit}
              </p>
              {item.descripcion && (
                <p className="mb-1 text-muted">{item.descripcion}</p>
              )}
              <small className="text-muted d-block">
                Ubicación: {item.location}
              </small>
              {item.precio != null && item.precio !== "" && (
                <small className="text-muted d-block">
                  Precio: {item.precio}
                </small>
              )}
            </div>
            {item.status && (
              <span className="badge text-bg-light align-self-start">
                {item.status}
              </span>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}
