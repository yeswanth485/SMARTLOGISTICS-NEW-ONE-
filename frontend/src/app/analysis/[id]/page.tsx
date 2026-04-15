'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { ShipmentAnalysis, ShipmentOption } from '@/types';
import { Bot, TrendingDown, CheckCircle2, Award } from 'lucide-react';

export default function AnalysisPage({ params }: { params: { id?: string } }) {
  const orderId = params.id;
  const [analysis, setAnalysis] = useState<ShipmentAnalysis | null>(null);
  const [shipments, setShipments] = useState<ShipmentOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (orderId && orderId !== 'default') {
      Promise.all([
        api.getShipmentAnalysis(orderId),
        api.getShipmentOptions(orderId)
      ]).then(([aiData, carrierData]) => {
         setAnalysis(aiData);
         setShipments(carrierData);
         setLoading(false);
      }).catch(err => {
         console.error(err);
         setLoading(false);
      });
    } else {
       setLoading(false);
    }
  }, [orderId]);

  if (loading) {
    return <div style={{display: 'flex', justifyContent: 'center', marginTop: '100px'}}><div className="status-pill transit">Running AI Analysis...</div></div>
  }

  if (!analysis) {
    return <div>No AI Analysis found.</div>
  }

  // Find best carrier details
  const bestCarrier = shipments.find(s => s.carrier_name === analysis.best_option);

  return (
    <div className="animate-in delay-100">
      <div className="page-header">
        <h1>AI Recommendation Engine</h1>
        <p>OpenRouter (GPT-4o) powered Carrier Analysis</p>
      </div>

      <div className="glass-card glow-cyan animate-in delay-200" style={{ marginBottom: '32px', position: 'relative', overflow: 'hidden', padding: '32px' }}>
         <div style={{ position: 'absolute', top: '-50px', right: '-50px', opacity: 0.1 }}>
            <Bot size={240} />
         </div>
         
         <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
             <div style={{ background: 'rgba(0, 212, 255, 0.2)', padding: '12px', borderRadius: '50%' }}>
                 <Award size={32} color="var(--accent-cyan)" />
             </div>
             <div>
                <div style={{ color: 'var(--accent-cyan)', fontWeight: 'bold', letterSpacing: '2px', fontSize: '0.8rem', textTransform: 'uppercase' }}>Recommended Carrier</div>
                <h2 style={{ fontSize: '2.5rem', margin: 0 }}>{analysis.best_option}</h2>
             </div>
         </div>
         
         <div style={{ background: 'rgba(0,0,0,0.3)', padding: '24px', borderRadius: '12px', borderLeft: '4px solid var(--accent-cyan)', marginBottom: '24px' }}>
             <p style={{ fontSize: '1.1rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>
                "{analysis.reason}"
             </p>
         </div>
         
         <div style={{ display: 'flex', gap: '24px' }}>
             {analysis.cost_saving > 0 && (
                 <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--status-green)', background: 'rgba(0,255,135,0.1)', padding: '8px 16px', borderRadius: '8px' }}>
                     <TrendingDown size={20} />
                     <strong>Est. Savings: ₹{analysis.cost_saving.toFixed(2)}</strong>
                 </div>
             )}
             <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-violet)', background: 'rgba(124,58,237,0.1)', padding: '8px 16px', borderRadius: '8px' }}>
                 <CheckCircle2 size={20} />
                 <strong>Confidence: {(analysis.confidence * 100).toFixed(1)}%</strong>
             </div>
             {bestCarrier && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)', background: 'rgba(255,255,255,0.05)', padding: '8px 16px', borderRadius: '8px' }}>
                    <strong>Final Cost: ₹{bestCarrier.estimated_cost.toFixed(2)}</strong> (Base Shipping)
                </div>
             )}
         </div>
      </div>

      <h3 style={{ marginBottom: '24px' }}>Carrier Comparison Overview</h3>
      <div className="glass-card animate-in delay-300" style={{ padding: 0, overflow: 'hidden' }}>
         <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', minWidth: '600px', borderCollapse: 'collapse', textAlign: 'left' }}>
               <thead>
                   <tr style={{ background: 'rgba(0,0,0,0.4)', color: 'var(--text-secondary)' }}>
                       <th style={{ padding: '16px 24px', borderBottom: '1px solid var(--card-border)', whiteSpace: 'nowrap' }}>Carrier</th>
                       <th style={{ padding: '16px 24px', borderBottom: '1px solid var(--card-border)', whiteSpace: 'nowrap' }}>Estimated Cost</th>
                       <th style={{ padding: '16px 24px', borderBottom: '1px solid var(--card-border)', whiteSpace: 'nowrap' }}>Delivery Time</th>
                       <th style={{ padding: '16px 24px', borderBottom: '1px solid var(--card-border)', whiteSpace: 'nowrap' }}>Reliability</th>
                       <th style={{ padding: '16px 24px', borderBottom: '1px solid var(--card-border)', whiteSpace: 'nowrap' }}>AI Preference</th>
                   </tr>
               </thead>
               <tbody>
                   {shipments.map((s, idx) => {
                      const isBest = s.carrier_name === analysis.best_option;
                      return (
                        <tr key={s.id} style={{ 
                            background: isBest ? 'rgba(0, 212, 255, 0.05)' : 'transparent',
                            borderBottom: idx === shipments.length - 1 ? 'none' : '1px solid var(--card-border)',
                            transition: 'background 0.3s ease, transform 0.2s ease',
                            cursor: 'default'
                        }} className="hover:bg-white/5">
                            <td style={{ padding: '16px 24px', fontWeight: isBest ? 'bold' : 'normal', color: isBest ? 'var(--accent-cyan)' : 'inherit', display: 'flex', alignItems: 'center', gap: '8px' }}>
                               {s.carrier_name}
                               {isBest && <Award size={16} />}
                            </td>
                            <td style={{ padding: '16px 24px', fontWeight: '500' }}>₹{s.estimated_cost.toFixed(2)}</td>
                            <td style={{ padding: '16px 24px' }}>{s.delivery_time} Days</td>
                            <td style={{ padding: '16px 24px' }}>
                                 <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                     <div style={{ width: '40px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                                         <div style={{ width: `${(s.rating / 5) * 100}%`, height: '100%', background: s.rating > 4 ? 'var(--status-green)' : 'var(--status-orange)' }}></div>
                                     </div>
                                     {s.rating}
                                 </div>
                            </td>
                            <td style={{ padding: '16px 24px' }}>
                               {isBest ? (
                                  <span style={{ color: 'var(--status-green)', fontWeight: 'bold' }}>Optimal Choice</span>
                               ) : (
                                  <span style={{ color: 'var(--text-secondary)' }}>Alternative</span>
                               )}
                            </td>
                        </tr>
                      )
                   })}
               </tbody>
            </table>
         </div>
      </div>
    </div>
  );
}
