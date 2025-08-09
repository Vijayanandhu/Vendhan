import React, { useEffect, useState } from 'react';

export default function AdminLeaveWidget() {
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/leave-requests?status=pending')
      .then(res => res.json())
      .then(data => {
        setLeaveRequests(data.requests || []);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load leave requests');
        setLoading(false);
      });
  }, []);

  function handleAction(requestId, status) {
    setLoading(true);
    fetch(`/api/leave-requests/${requestId}/${status}`, { method: 'POST' })
      .then(res => res.json())
      .then(() => {
        setLeaveRequests(lr => lr.filter(r => r.id !== requestId));
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to update leave request');
        setLoading(false);
      });
  }

  if (loading) return <div>Loading leave requests...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="bg-white rounded shadow p-4">
      <h3 className="font-bold text-lg mb-2">Pending Leave Requests</h3>
      {leaveRequests.length === 0 ? (
        <div>No pending requests.</div>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Dates</th>
              <th>Type</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {leaveRequests.map(req => (
              <tr key={req.id}>
                <td>{req.employeeName}</td>
                <td>{req.startDate} to {req.endDate}</td>
                <td>{req.leaveType}</td>
                <td>
                  <button className="bg-green-600 text-white px-2 py-1 rounded mr-2" onClick={() => handleAction(req.id, 'approve')}>Approve</button>
                  <button className="bg-red-600 text-white px-2 py-1 rounded" onClick={() => handleAction(req.id, 'deny')}>Reject</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
