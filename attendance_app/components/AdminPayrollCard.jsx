import React, { useEffect, useState } from 'react';

export default function AdminPayrollCard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/billing/summary')
      .then(res => res.json())
      .then(data => {
        setSummary(data.summary);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load payroll summary');
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading payroll summary...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!summary) return null;

  return (
    <div className="rounded shadow p-4" style={{ background: '#E8F5E8' }}>
      <div className="font-bold text-lg mb-2" style={{ color: '#2D5016' }}>Payroll Summary</div>
      <div className="mb-1">Total Payout: <span className="font-bold">${summary.totalPayout}</span></div>
      <div className="mb-1">Billable Revenue: <span className="font-bold">${summary.billableRevenue}</span></div>
      <div className="mb-1">Pending Actions: <span className="font-bold">{summary.pendingActions}</span></div>
      <button className="bg-green-700 text-white px-4 py-2 rounded mt-2">Process All</button>
    </div>
  );
}
