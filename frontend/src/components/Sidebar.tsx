'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, PackageSearch, Truck, ShieldCheck, UploadCloud } from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', path: '/results', icon: LayoutDashboard },
    { name: 'Upload', path: '/upload', icon: UploadCloud },
    { name: 'Tracking', path: '/tracking', icon: Truck },
    { name: 'AI Analysis', path: '/analysis', icon: ShieldCheck },
  ];

  const getOrderId = () => {
    // Basic extraction to keep sidebar links active for the current order
    if (typeof window !== 'undefined') {
       const match = window.location.pathname.match(/\/([a-f0-9\-]{36})/i);
       return match ? `/${match[1]}` : '/default';
    }
    return '';
  };

  const idSuffix = getOrderId();

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <PackageSearch style={{verticalAlign: 'middle', marginRight: '8px'}}/>
        SmartLogistics
      </div>
      <nav>
        {navItems.map((item) => {
          const Icon = item.icon;
          // Only append ID to results/tracking/analysis if we are not on upload
          const path = item.path === '/upload' || item.path === '/' 
            ? item.path 
            : `${item.path}${idSuffix === '/default' ? '' : idSuffix}`;
            
          const isActive = pathname?.startsWith(item.path);

          return (
            <Link key={item.name} href={path} className={`nav-item ${isActive ? 'active' : ''}`}>
              <Icon size={20} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
