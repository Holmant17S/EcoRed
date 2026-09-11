import { useEffect, useState } from "react";
import { listCompanies } from "../../companies/services/companyService.js";
import { listMaterials } from "../../materials/services/materialService.js";
import AlertMessage from "../../../shared/components/AlertMessage.jsx";
import LoadingSpinner from "../../../shared/components/LoadingSpinner.jsx";
import PageHeader from "../../../shared/components/PageHeader.jsx";
import { getErrorMessage } from "../../../shared/utils/getErrorMessage.js";
import RequestForm from "../components/RequestForm.jsx";
import RequestList from "../components/RequestList.jsx";
import { createRequest, listRequests } from "../services/requestService.js";

export default function RequestsPage() {
  const [companies, setCompanies] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    const load = async () => {
      setLoading(true);
      setFeedback(null);
      try {
        const [companyData, materialData, requestData] = await Promise.all([
          listCompanies({ signal: controller.signal }),
          listMaterials({ signal: controller.signal }),
          listRequests({ signal: controller.signal }),
        ]);
        setCompanies(Array.isArray(companyData) ? companyData : []);
        setMaterials(Array.isArray(materialData) ? materialData : []);
        setItems(Array.isArray(requestData) ? requestData : []);
      } catch (error) {
        if (error.code !== "ERR_CANCELED") {
          setFeedback({
            type: "danger",
            message: getErrorMessage(error, "No fue posible cargar solicitudes."),
          });
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    load();
    return () => controller.abort();
  }, []);

  const handleCreate = async (payload) => {
    setFeedback(null);
    try {
      await createRequest(payload);
      const refreshed = await listRequests();
      setItems(Array.isArray(refreshed) ? refreshed : []);
      setFeedback({ type: "success", message: "Solicitud creada correctamente." });
    } catch (error) {
      setFeedback({
        type: "danger",
        message: getErrorMessage(error, "No fue posible crear la solicitud."),
      });
    }
  };

  return (
    <section aria-labelledby="requests-title">
      <PageHeader
        id="requests-title"
        title="Solicitudes"
        subtitle="Pide materiales publicados. Este módulo usa el microservicio requests-service."
      />
      {feedback && (
        <AlertMessage type={feedback.type} message={feedback.message} />
      )}
      {loading ? (
        <LoadingSpinner label="Cargando solicitudes" />
      ) : (
        <div className="row g-4">
          <div className="col-lg-5">
            <div className="card shadow-sm">
              <div className="card-body">
                <h2 className="h5 mb-3">Nueva solicitud</h2>
                <RequestForm
                  companies={companies}
                  materials={materials}
                  onSubmit={handleCreate}
                />
              </div>
            </div>
          </div>
          <div className="col-lg-7">
            <div className="card shadow-sm">
              <div className="card-body">
                <h2 className="h5 mb-3">Mis solicitudes</h2>
                <RequestList items={items} />
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
