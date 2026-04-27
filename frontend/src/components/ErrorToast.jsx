import { useState, useEffect, useCallback } from 'react';

export default function ErrorToast({ errors, removeError }) {
  return (
    <div className="error-toast-container">
      {errors.map((error) => (
        <Toast key={error.id} error={error} onClose={() => removeError(error.id)} />
      ))}
    </div>
  );
}

function Toast({ error, onClose }) {
  const [leaving, setLeaving] = useState(false);

  const handleClose = useCallback(() => {
    setLeaving(true);
    setTimeout(onClose, 300);
  }, [onClose]);

  useEffect(() => {
    const timer = setTimeout(handleClose, 5000);
    return () => clearTimeout(timer);
  }, [handleClose]);

  return (
    <div className={`error-toast ${leaving ? 'leaving' : ''}`}>
      <span className="error-toast-icon">⚠️</span>
      <div className="error-toast-body">
        <div className="error-toast-title">Error</div>
        <div className="error-toast-message">{error.message}</div>
      </div>
      <button className="error-toast-close" onClick={handleClose}>✕</button>
    </div>
  );
}
