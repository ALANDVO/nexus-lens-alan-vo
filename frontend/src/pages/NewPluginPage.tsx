import { useState } from "react";
import { api } from "../api/client";
import type { PluginCreate } from "../api/types";
import PluginForm from "../components/PluginForm";

interface Props {
  onSuccess: (id: number) => void;
  onCancel: () => void;
}

export default function NewPluginPage({ onSuccess, onCancel }: Props) {
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const handleSubmit = async (data: PluginCreate) => {
    setSubmitting(true);
    setApiError(null);
    try {
      const plugin = await api.createPlugin(data);
      onSuccess(plugin.id);
    } catch (err) {
      if (err instanceof Error) {
        setApiError(err.message);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h2>Register New Plugin</h2>
        <button className="btn" onClick={onCancel} disabled={submitting}>
          ← Back
        </button>
      </div>
      {apiError && <div className="form-error">{apiError}</div>}
      <PluginForm onSubmit={handleSubmit} loading={submitting} />
    </div>
  );
}