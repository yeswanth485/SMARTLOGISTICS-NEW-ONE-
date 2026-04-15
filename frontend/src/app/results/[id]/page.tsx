'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { PackingResult } from '@/types';
import { PackageOpen, Ruler, Percent, DollarSign, Box } from 'lucide-react';

export default function ResultsPage({ params }: { params: { id?: string } }) {
  const orderId = params.id;
  const [result, setResult] = useState<PackingResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (orderId && orderId !== 'default') {
      api.getPackingResult(orderId).then(res => {
        setResult(res);
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
     return <div style={{display: 'flex', justifyContent: 'center', marginTop: '100px'}}><div className="status-pill transit">Loading Dashboard...</div></div>
  }

  if (!result) {
    return <div>No results found for this order. Please upload an order first.</div>
  }

  const stats = [
    { label: 'Selected Box', value: result.box_type, icon: PackageOpen, color: 'var(--accent-cyan)' },
    { label: 'Dimensions', value: result.box_dimensions, icon: Ruler, color: 'var(--accent-violet)' },
    { label: 'Utilization', value: `${result.utilization.toFixed(1)}%`, icon: Percent, color: 'var(--status-green)' },
    { label: 'Total Items', value: result.items_count, icon: Box, color: 'var(--status-orange)' },
  ];

  return (
    <div className="animate-in delay-100">
      <div className="page-header">
        <h1>Optimization Results</h1>
        <p>Order ID: <span style={{fontFamily: 'monospace', color: 'var(--text-secondary)'}}>{result.order_id}</span></p>
      </div>

      <div className="stat-grid">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className={`glass-card delay-${(i+2)*100} animate-in`} style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
               <div style={{ background: `${stat.color}20`, padding: '16px', borderRadius: '12px', color: stat.color }}>
                 <Icon size={32} />
               </div>
               <div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '4px' }}>{stat.label}</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{stat.value}</div>
               </div>
            </div>
          )
        })}
      </div>

      <div className="glass-card animate-in delay-500 glow-cyan" style={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
         <h3 style={{ marginBottom: '24px' }}>3D Bin Packing Visualizer</h3>
         <div style={{ 
            flex: 1, 
            background: 'rgba(0,0,0,0.3)', 
            borderRadius: '12px', 
            position: 'relative',
            perspective: '1000px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden'
         }}>
           {/* Improved CSS 3D visualizer showing multiple items scaled relative to container */}
           <div style={{
               width: '300px',
               height: '200px',
               background: 'rgba(0, 212, 255, 0.05)',
               border: '2px dashed var(--accent-cyan)',
               transformStyle: 'preserve-3d',
               transform: 'rotateX(-20deg) rotateY(30deg)',
               position: 'relative'
           }}>
              <div style={{position:'absolute', inset:0, background: 'rgba(0,0,0,0.4)', transform: 'translateZ(-20px)'}}></div>
              
              {result.items_placed && result.items_placed.length > 0 ? (
                 result.items_placed.map((item, idx) => {
                    // Normalize position based on box dimensions assuming box is roughly 300x200 
                    // This is just a conceptual dynamic visualizer
                    const box_l = parseFloat(result.box_dimensions.split('x')[0]); // max roughly 50-80
                    const box_w = parseFloat(result.box_dimensions.split('x')[1]); 
                    const box_h = parseFloat(result.box_dimensions.split('x')[2]);
                    
                    const scaleX = 300 / (box_l || 100);
                    const scaleY = 200 / (box_w || 100);
                    
                    const item_w = (item.length * scaleX) || 40;
                    const item_h = (item.width * scaleY) || 40;
                    
                    const colorList = ['rgba(124, 58, 237, 0.7)', 'rgba(0, 212, 255, 0.7)', 'rgba(0, 255, 135, 0.7)', 'rgba(249, 115, 22, 0.7)'];
                    const bgColor = colorList[idx % colorList.length];

                    return (
                        <div key={idx} style={{
                            position: 'absolute', 
                            bottom: `${(item.y * scaleY) || 10}px`, 
                            left: `${(item.x * scaleX) || 10}px`, 
                            width: `${item_w}px`, 
                            height: `${item_h}px`, 
                            background: bgColor, 
                            border: '1px solid rgba(255,255,255,0.4)', 
                            transform: `translateZ(${(item.z * 5 + idx * 5)}px)`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            boxShadow: '0 4px 15px rgba(0,0,0,0.5)'
                        }}>
                           <div style={{padding: '2px', fontSize: '9px', fontWeight: 'bold', color: 'white', textAlign: 'center', textOverflow: 'ellipsis', overflow: 'hidden'}}>{item.name}</div>
                        </div>
                    )
                 })
              ) : (
                <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%'}}>
                   <span style={{color: 'var(--accent-cyan)'}}>Visualization Unavailable</span>
                </div>
              )}
           </div>
           
           <div style={{ position: 'absolute', bottom: 16, right: 16, background: 'rgba(0,0,0,0.5)', padding: '8px 16px', borderRadius: '8px', fontSize: '0.8rem' }}>
              Base Cost: <strong style={{color: 'var(--status-green)', fontSize: '1rem'}}>₹{result.cost.toFixed(2)}</strong>
           </div>
         </div>
      </div>
    </div>
  );
}
