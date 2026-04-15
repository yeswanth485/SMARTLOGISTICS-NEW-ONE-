'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { UploadCloud, Plus, Trash2, Box, Eye } from 'lucide-react';

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<string[][]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [products, setProducts] = useState([
    { name: '', length: 0, width: 0, height: 0, weight: 0, quantity: 1 }
  ]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      
      try {
        const text = await selectedFile.text();
        const rows = text.split('\n')
          .map(row => row.split(','))
          .filter(row => row.length > 1 && row.some(col => col.trim() !== ''));
        
        // Show up to 5 rows as preview
        setPreviewData(rows.slice(0, 6)); 
      } catch (err) {
        console.error("Failed to read preview", err);
      }
    }
  };

  const handleFileUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.uploadOptimize(file);
      router.push(`/results/${res.order_id}`);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleManualSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      for (let i = 0; i < products.length; i++) {
        const p = products[i];
        if (!p.name) throw new Error(`Row ${i + 1}: Missing product name`);
        if (p.length <= 0) throw new Error(`Row ${i + 1}: Length must be greater than 0`);
        if (p.width <= 0) throw new Error(`Row ${i + 1}: Width must be greater than 0`);
        if (p.height <= 0) throw new Error(`Row ${i + 1}: Height must be greater than 0`);
        if (p.weight <= 0) throw new Error(`Row ${i + 1}: Weight must be greater than 0`);
        if (p.quantity <= 0) throw new Error(`Row ${i + 1}: Quantity must be at least 1`);
      }
      const res = await api.optimize({ products });
      router.push(`/results/${res.order_id}`);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  const updateProduct = (index: number, field: string, value: any) => {
    const newProducts = [...products];
    newProducts[index] = { ...newProducts[index], [field]: value };
    setProducts(newProducts);
  };

  const addProduct = () => {
    setProducts([...products, { name: '', length: 0, width: 0, height: 0, weight: 0, quantity: 1 }]);
  };

  const removeProduct = (index: number) => {
    if (products.length > 1) {
      const newProducts = [...products];
      newProducts.splice(index, 1);
      setProducts(newProducts);
    }
  };

  return (
    <div className="animate-in delay-100">
      <div className="page-header">
        <h1>Optimize Packaging</h1>
        <p>Upload a CSV file or enter products manually to calculate optimal boxing and carrier rates.</p>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#fca5a5', padding: '16px', borderRadius: '8px', marginBottom: '24px', border: '1px solid rgba(239,68,68,0.3)' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
        {/* CSV Upload & Preview Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="glass-card glow-cyan" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyItems: 'center', minHeight: '300px', cursor: 'pointer', position: 'relative' }}>
                <input type="file" accept=".csv" onChange={handleFileChange} style={{position: 'absolute', width: '100%', height: '100%', opacity: 0, cursor: 'pointer', zIndex: 5}} />
                <div style={{marginTop: '40px'}} />
                <UploadCloud size={64} color="var(--accent-cyan)" style={{ marginBottom: '16px' }} />
                <h3 style={{ marginBottom: '8px' }}>Upload CSV Data</h3>
                <p style={{ color: 'var(--text-secondary)', textAlign: 'center', fontSize: '0.9rem' }}>
                  Drag and drop or click to upload.<br/>
                  Required Columns: name, length, width, height, weight
                </p>
                {file && (
                  <div style={{ marginTop: '24px', fontWeight: 'bold', color: 'var(--accent-cyan)' }}>
                    File Ready: {file.name}
                  </div>
                )}
                
                <button 
                  className="btn-primary" 
                  style={{ marginTop: '24px', zIndex: 10, width: '100%', maxWidth: '250px' }}
                  onClick={(e) => { e.stopPropagation(); handleFileUpload(); }}
                  disabled={!file || loading}
                >
                  {loading ? 'Optimizing Data...' : 'Run Optimization'}
                </button>
            </div>

            {/* CSV Data Preview Table */}
            {previewData.length > 0 && (
               <div className="glass-card animate-in delay-200" style={{ padding: '24px' }}>
                  <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                     <Eye size={20} color="var(--accent-cyan)"/>
                     CSV Preview Mode
                  </h3>
                  <div style={{ overflowX: 'auto', borderRadius: '8px' }}>
                     <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                        <thead>
                           <tr>
                              {previewData[0].map((header, idx) => (
                                 <th key={idx} style={{ textAlign: 'left', padding: '12px', background: 'rgba(0,0,0,0.5)', color: 'var(--accent-cyan)', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                    {header.trim()}
                                 </th>
                              ))}
                           </tr>
                        </thead>
                        <tbody>
                           {previewData.slice(1).map((row, idx) => (
                              <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                 {row.map((cell, cidx) => (
                                    <td key={cidx} style={{ padding: '12px', color: 'var(--text-secondary)' }}>
                                       {cell.trim()}
                                    </td>
                                 ))}
                              </tr>
                           ))}
                        </tbody>
                     </table>
                  </div>
                  {previewData.length >= 6 && <p style={{marginTop: '12px', fontSize: '0.8rem', color: 'var(--text-secondary)'}}>Showing first 5 rows...</p>}
               </div>
            )}
        </div>

        {/* Manual Entry */}
        <div className="glass-card glow-violet" style={{ alignSelf: 'flex-start' }}>
           <h3 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Box size={20} color="var(--accent-violet)"/>
              Manual Entry Engine
           </h3>

           {products.map((p, i) => (
             <div key={i} style={{ display: 'grid', gridTemplateColumns: 'minmax(80px, 2fr) 1fr 1fr 1fr 1fr 1fr auto', gap: '8px', marginBottom: '16px', alignItems: 'center' }}>
                <input className="input-base" placeholder="Item Name" value={p.name} onChange={e => updateProduct(i, 'name', e.target.value)} />
                <input className="input-base" type="number" placeholder="L(cm)" value={p.length || ''} onChange={e => updateProduct(i, 'length', parseFloat(e.target.value))} />
                <input className="input-base" type="number" placeholder="W(cm)" value={p.width || ''} onChange={e => updateProduct(i, 'width', parseFloat(e.target.value))} />
                <input className="input-base" type="number" placeholder="H(cm)" value={p.height || ''} onChange={e => updateProduct(i, 'height', parseFloat(e.target.value))} />
                <input className="input-base" type="number" placeholder="Wt(kg)" value={p.weight || ''} onChange={e => updateProduct(i, 'weight', parseFloat(e.target.value))} />
                <input className="input-base" type="number" placeholder="Qty" value={p.quantity} onChange={e => updateProduct(i, 'quantity', parseInt(e.target.value))} />
                <button style={{ background: 'translateZ(0)', border: 'none', color: 'var(--status-red)', cursor: 'pointer', opacity: 0.8 }} onClick={() => removeProduct(i)} className="hover:opacity-100">
                  <Trash2 size={20} />
                </button>
             </div>
           ))}

           <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px' }}>
              <button className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }} onClick={addProduct}>
                <Plus size={16} /> Add Item Row
              </button>

              <button className="btn-primary" onClick={handleManualSubmit} disabled={loading} style={{ background: 'var(--accent-violet)', boxShadow: 'var(--glow-violet)' }}>
                 {loading ? 'Optimizing Data...' : 'Compute Optimization'}
              </button>
           </div>
        </div>
      </div>
    </div>
  );
}
