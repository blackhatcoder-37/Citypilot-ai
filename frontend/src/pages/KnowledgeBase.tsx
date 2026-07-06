import { useState, useEffect, useRef } from 'react';
import { UploadCloud, File as FileIcon, Trash2, BookOpen, FileText, Table, Loader2 } from 'lucide-react';

interface DBDocument {
  id: number;
  original_filename: string;
  stored_filename: string;
  file_type: string;
  file_size_bytes: number;
  upload_date: string;
  status: string;
  is_embedded: boolean;
}

const getFileIcon = (name: string) => {
  if (name.endsWith('.pdf')) return <FileText size={18} className="text-danger" />;
  if (name.endsWith('.csv')) return <Table size={18} className="text-success" />;
  return <FileIcon size={18} className="text-info" />;
};

const KnowledgeBase = () => {
  const [docs, setDocs] = useState<DBDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocs = () => {
    setLoading(true);
    fetch('http://localhost:8000/upload/documents')
      .then(res => res.json())
      .then(json => {
        if (json.success && json.data) {
          setDocs(json.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching documents:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setUploading(true);
      const fileToUpload = e.target.files[0];
      const formData = new FormData();
      formData.append('file', fileToUpload);

      fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      })
        .then(res => res.json())
        .then(json => {
          setUploading(false);
          if (json.success) {
            fetchDocs();
          }
        })
        .catch(err => {
          console.error('Upload failed:', err);
          setUploading(false);
        });
    }
  };

  const removeFile = (id: number) => {
    fetch(`http://localhost:8000/upload/documents/${id}`, {
      method: 'DELETE',
    })
      .then(res => res.json())
      .then(json => {
        if (json.success) {
          fetchDocs();
        }
      })
      .catch(err => console.error('Error deleting document:', err));
  };

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary tracking-tight flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
            <BookOpen size={20} className="text-primary" />
          </div>
          Knowledge Base
        </h1>
        <p className="text-sm text-text-muted mt-2 ml-12">Upload city policies, protocols, and data to enhance AI decision context</p>
      </div>

      {/* Upload Zone */}
      <div
        className="glass rounded-xl p-10 border-2 border-dashed border-border hover:border-primary/30 transition-all cursor-pointer flex flex-col items-center justify-center max-w-3xl"
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <div className="w-14 h-14 rounded-xl bg-white/[0.03] border border-border flex items-center justify-center mb-4">
          {uploading ? (
            <Loader2 size={24} className="text-primary animate-spin" />
          ) : (
            <UploadCloud size={24} className="text-text-muted" />
          )}
        </div>
        <h3 className="text-sm font-semibold text-text-primary mb-1">
          {uploading ? 'Processing and Embedding...' : 'Drop files here or click to browse'}
        </h3>
        <p className="text-xs text-text-muted">PDF, DOCX, CSV — max 50MB per file</p>
        <input
          type="file"
          accept=".pdf,.docx,.csv"
          className="hidden"
          ref={fileInputRef}
          onChange={handleFileChange}
          disabled={uploading}
        />
      </div>

      {/* File List */}
      {loading && docs.length === 0 ? (
        <div className="flex items-center gap-2 text-sm text-text-muted">
          <Loader2 className="animate-spin" size={16} />
          <span>Loading knowledge directory...</span>
        </div>
      ) : docs.length > 0 ? (
        <div className="max-w-3xl">
          <h3 className="text-sm font-semibold text-text-primary mb-3">Uploaded Documents ({docs.length})</h3>
          <div className="space-y-2">
            {docs.map((doc) => (
              <div key={doc.id} className="glass rounded-lg p-3.5 flex items-center gap-3 group hover:glass-hover transition-all">
                <div className="w-9 h-9 rounded-lg bg-white/[0.03] border border-border flex items-center justify-center shrink-0">
                  {getFileIcon(doc.original_filename)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text-primary font-medium truncate">{doc.original_filename}</p>
                  <p className="text-[10px] text-text-muted mt-0.5">
                    {(doc.file_size_bytes / 1024 / 1024).toFixed(2)} MB &bull; Status: <span className="text-primary-light font-medium">{doc.status}</span>
                  </p>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); removeFile(doc.id); }}
                  className="p-2 rounded-lg text-text-muted hover:text-danger hover:bg-danger/10 transition-colors opacity-0 group-hover:opacity-100"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="max-w-3xl py-8 text-center bg-white/[0.01] border border-dashed border-border rounded-xl">
          <p className="text-xs text-text-muted italic">No documents uploaded. Upload emergency protocols to train the RAG engine.</p>
        </div>
      )}
    </div>
  );
};

export default KnowledgeBase;
