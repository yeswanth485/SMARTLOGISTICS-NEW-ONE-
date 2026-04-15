'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { ShipmentOption } from '@/types';
import { Truck, Star, Clock, CheckCircle2, Navigation } from 'lucide-react';

export default function TrackingPage({ params }: { params: { id?: string } }) {
  const orderId = params.id;
  const [shipments, setShipments] = useState<ShipmentOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (orderId && orderId !== 'default') {
      api.getShipmentOptions(orderId).then(res => {
        setShipments(res);
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
    return <div style={{display: 'flex', justifyContent: 'center', marginTop: '100px'}}><div className="status-pill transit">Loading Tracking...</div></div>
  }

  if (shipments.length === 0) {
    return <div>No shipment data found for this order.</div>
  }

  return (
    <div className="animate-in delay-100">
      <div className="page-header">
        <h1>Carrier Simulation</h1>
        <p>Live tracking and multi-carrier cost comparison</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
        {shipments.map((carrier, i) => {
           let badgeClass = 'status-pill transit';
           if (carrier.status === 'Delivered') badgeClass = 'status-pill delivered';
           if (carrier.status === 'Delayed') badgeClass = 'status-pill delayed';

           return (
              <div key={carrier.id} className={`glass-card delay-${(i+1)*100} animate-in glow-violet`} style={{ position: 'relative', overflow: 'hidden' }}>
                 {/* Top stripe */}
                 <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '4px', background: carrier.color || 'var(--accent-violet)' }}></div>
                 
                 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                   <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ background: 'rgba(255,255,255,0.05)', padding: '12px', borderRadius: '12px' }}>
                        <Truck size={24} color={carrier.color || 'white'} />
                      </div>
                      <div>
                        <h3 style={{ margin: 0 }}>{carrier.carrier_name}</h3>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                           {carrier.tracking_id}
                        </div>
                      </div>
                   </div>
                   <div className={badgeClass}>{carrier.status}</div>
                 </div>

                 <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
                    <div style={{ background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
                       <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Est. Cost</div>
                       <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>₹{carrier.estimated_cost.toFixed(2)}</div>
                    </div>
                    <div style={{ background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
                       <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Delivery</div>
                       <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{carrier.delivery_time} Days</div>
                    </div>
                 </div>

                 {/* Simulated animated progress bar */}
                 <div style={{ marginBottom: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '8px', color: 'var(--text-secondary)' }}>
                       <span style={{color: carrier.status === 'Delivered' ? 'var(--status-green)' : 'inherit'}}>Dispatched</span>
                       <span>Midpoint</span>
                       <span>Delivered</span>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', position: 'relative' }}>
                       <div style={{ 
                           position: 'absolute', top: 0, left: 0, bottom: 0, 
                           width: carrier.status === 'Delivered' ? '100%' : (carrier.status === 'Delayed' ? '30%' : '65%'),
                           background: carrier.status === 'Delivered' ? 'var(--status-green)' : (carrier.color || 'var(--accent-cyan)'),
                           borderRadius: '3px',
                           boxShadow: carrier.status === 'In Transit' ? `0 0 10px ${carrier.color}` : 'none'
                       }}></div>
                    </div>
                 </div>

                 <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'rgb(250 204 21)', fontSize: '0.9rem', justifyContent: 'flex-end' }}>
                    <Star size={16} fill="rgb(250 204 21)"/> {carrier.rating} / 5.0
                 </div>
              </div>
           )
        })}
      </div>
    </div>
  );
}
