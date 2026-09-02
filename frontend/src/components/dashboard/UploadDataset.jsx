import React, { useState, useRef, useEffect } from "react";
import {
  UploadCloud,
  CheckCircle,
  AlertTriangle,
  File as FileIcon,
  X,
  Loader,
} from "lucide-react";
import apiClient from "../../services/api";
import Button from "../common/Button";

const STATUS_COLORS = {
  UPLOADED: "text-blue-400",
  VALIDATING: "text-yellow-400",
  INGESTING: "text-yellow-400",
  ANALYZING: "text-orange-400",
  GRAPH_BUILDING: "text-purple-400",
  COMPLETED: "text-emerald-400",
  FAILED: "text-red-400",
};

const STATUS_MESSAGES = {
  UPLOADED: "File uploaded, waiting to start...",
  VALIDATING: "Validating CICIDS2017 CSV...",
  INGESTING: "Parsing and normalizing CSV...",
  ANALYZING: "AI Engine detecting anomalies...",
  GRAPH_BUILDING: "Constructing Neo4j attack graph...",
  COMPLETED: "Processing complete!",
  FAILED: "Processing failed.",
};

export const UploadDataset = ({ onUploadComplete }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [datasetId, setDatasetId] = useState(null);
  const [status, setStatus] = useState(null); // UPLOADED, INGESTING, ANALYZING, GRAPH_BUILDING, COMPLETED, ERROR
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    setError(null);
    if (!selectedFile.name.endsWith(".csv")) {
      setError("Please select a valid CSV file (CICIDS2017 format).");
      return;
    }
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // apiClient will use interceptor for the token
      const res = await apiClient.post("/logs/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setDatasetId(res.dataset_id || res.datasetId);
      setStatus("UPLOADED");
    } catch (err) {
      // Extract error message from various response formats
      let errorMsg = "Upload failed";
      if (err?.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err?.response?.data?.message) {
        errorMsg = err.response.data.message;
      } else if (err?.message) {
        errorMsg = err.message;
      }
      setError(errorMsg);
      setUploading(false);
    }
  };

  useEffect(() => {
    let interval;
    if (datasetId && status !== "COMPLETED" && status !== "FAILED") {
      interval = setInterval(async () => {
        try {
          const res = await apiClient.get(`/logs/${datasetId}/status`);
          setStatus(res.status);
          if (res.status === "COMPLETED" || res.status === "FAILED") {
            clearInterval(interval);
            setUploading(false);
            if (res.status === "COMPLETED" && onUploadComplete) {
              onUploadComplete();
            }
          }
        } catch (err) {
          console.error("Failed to poll status", err);
        }
      }, 3000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [datasetId, status, onUploadComplete]);

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
        <h3 className="text-base font-bold text-slate-100">
          Upload Threat Dataset (CICIDS2017)
        </h3>
        {status && (
          <span
            className={`text-xs font-mono font-bold px-2 py-1 rounded bg-slate-800 ${STATUS_COLORS[status]}`}
          >
            {status}
          </span>
        )}
      </div>

      {!uploading && !status && (
        <form
          className={`w-full relative border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center transition-colors ${
            dragActive
              ? "border-cyan-500 bg-cyan-950/20"
              : "border-slate-700 hover:border-slate-500"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onSubmit={(e) => e.preventDefault()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleChange}
          />

          <UploadCloud
            className={`w-12 h-12 mb-4 ${dragActive ? "text-cyan-400" : "text-slate-400"}`}
          />

          {file ? (
            <div className="flex items-center gap-2 mb-4">
              <FileIcon className="w-5 h-5 text-cyan-400" />
              <span className="text-slate-200 text-sm font-mono">
                {file.name}
              </span>
              <button
                type="button"
                onClick={() => setFile(null)}
                className="text-slate-500 hover:text-red-400 ml-2"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <>
              <p className="text-slate-300 font-medium mb-1">
                Drag and drop your CSV dataset here
              </p>
              <p className="text-slate-500 text-xs mb-6">
                Support for CICIDS2017 formatted pcaps/csv
              </p>
            </>
          )}

          <div className="flex gap-4">
            {!file && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => inputRef.current.click()}
              >
                Browse Files
              </Button>
            )}
            {file && (
              <Button variant="primary" size="sm" onClick={handleUpload}>
                Upload & Analyze
              </Button>
            )}
          </div>
        </form>
      )}

      {(uploading || status) && (
        <div className="p-8 flex flex-col items-center justify-center bg-slate-800/30 rounded-lg border border-slate-700/50">
          {status === "FAILED" ? (
            <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />
          ) : status === "COMPLETED" ? (
            <CheckCircle className="w-12 h-12 text-emerald-500 mb-4" />
          ) : (
            <Loader className="w-12 h-12 text-cyan-500 animate-spin mb-4" />
          )}

          <h4 className="text-lg font-bold text-slate-100 mb-2">
            {status === "FAILED"
              ? "Processing Failed"
              : status === "COMPLETED"
                ? "Analysis Complete"
                : "Processing Pipeline Active"}
          </h4>
          <p
            className={`text-sm font-mono ${STATUS_COLORS[status] || "text-slate-400"} mb-6`}
          >
            {STATUS_MESSAGES[status] || "Initializing..."}
          </p>

          {status === "COMPLETED" && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                setStatus(null);
                setFile(null);
              }}
            >
              Upload Another Dataset
            </Button>
          )}
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-950/30 border border-red-500/30 rounded flex items-start gap-2">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
          <p className="text-xs text-red-300">{error}</p>
        </div>
      )}
    </div>
  );
};

export default UploadDataset;
