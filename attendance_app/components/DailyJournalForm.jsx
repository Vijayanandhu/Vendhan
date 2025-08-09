import React, { useState, useEffect } from 'react';
import emailjs from '@emailjs/browser';

const TASK_TYPES = ['coding', 'testing', 'review', 'meeting'];
const STATUS_OPTIONS = ['finished', 'pending', 'error'];

function getToday() {
  return new Date().toISOString().slice(0, 10);
}


async function fetchJournalEntry({ employeeId, projectId, date }) {
  const params = new URLSearchParams({ employee_id: employeeId, project_id: projectId, date });
  const res = await fetch(`/api/journal-entries?${params.toString()}`);
  if (!res.ok) return null;
  const data = await res.json();
  return data && data.length > 0 ? data[0] : null;
}

async function saveJournalEntry(entry) {
  const res = await fetch('/api/journal-entries', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry)
  });
  if (!res.ok) throw new Error('Failed to save entry');
  return res.json();
}

// EmailJS config (replace with your actual IDs)
const EMAILJS_SERVICE_ID = 'your_service_id';
const EMAILJS_TEMPLATE_ID = 'your_template_id';
const EMAILJS_PUBLIC_KEY = 'your_public_key';

function sendErrorEmail(entry, users, projects) {
  const employee = users.find(u => u.id === entry.employeeId);
  const project = projects.find(p => p.id === entry.projectId);
  const erroredIds = entry.statusPerObject.filter(s => s.status === 'error').map(s => s.objectId);
  emailjs.send(
    EMAILJS_SERVICE_ID,
    EMAILJS_TEMPLATE_ID,
    {
      projectName: project ? project.name : entry.projectId,
      objectId: erroredIds.join(', '),
      employeeName: employee ? employee.name : entry.employeeId,
      date: new Date(entry.date).toLocaleDateString(),
    },
    EMAILJS_PUBLIC_KEY
  ).then(() => {
    // Optionally show a toast or log
  }).catch(console.error);
}

export default function DailyJournalForm({ projects, employeeId, users }) {
  const [projectId, setProjectId] = useState('');
  const [taskType, setTaskType] = useState('');
  const [hoursSpent, setHoursSpent] = useState('');
  const [objectIds, setObjectIds] = useState('');
  const [statusPerObject, setStatusPerObject] = useState([]);
  const [comments, setComments] = useState('');
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    // Load today's entry if exists from backend
    const today = getToday();
    if (!projectId) return;
    fetchJournalEntry({ employeeId, projectId, date: today })
      .then(found => {
        if (found) {
          setTaskType(found.taskType);
          setHoursSpent(found.hoursSpent);
          setObjectIds(found.objectIds.join(','));
          setStatusPerObject(found.statusPerObject);
          setComments(found.comments || '');
          setSubmitted(true);
        } else {
          setTaskType('');
          setHoursSpent('');
          setObjectIds('');
          setStatusPerObject([]);
          setComments('');
          setSubmitted(false);
        }
      });
  }, [projectId, employeeId]);

  function handleObjectIdsChange(e) {
    const ids = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
    setObjectIds(e.target.value);
    setStatusPerObject(ids.map((id, i) => statusPerObject[i] || { objectId: id, status: 'pending' }));
  }

  function handleStatusChange(idx, status) {
    setStatusPerObject(
      statusPerObject.map((obj, i) => i === idx ? { ...obj, status } : obj)
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    const today = getToday();
    const ids = objectIds.split(',').map(s => s.trim()).filter(Boolean);
    if (!projectId || !taskType || !hoursSpent || ids.length === 0) {
      setError('All fields except comments are required.');
      return;
    }
    const entry = {
      date: today,
      employeeId,
      projectId,
      objectIds: ids,
      taskType,
      hoursSpent: Number(hoursSpent),
      statusPerObject: statusPerObject.map((obj, i) => ({ objectId: ids[i], status: obj.status })),
      comments,
    };
    try {
      await saveJournalEntry(entry);
      setSubmitted(true);
      if (entry.statusPerObject.some(s => s.status === 'error')) {
        sendErrorEmail(entry, users, projects);
      }
    } catch (err) {
      setError('Failed to save entry: ' + (err.message || err));
    }
  }

  // Manual entry for project journal
  async function handleManualEntry() {
    setError('');
    const today = getToday();
    const ids = objectIds.split(',').map(s => s.trim()).filter(Boolean);
    if (!projectId || !taskType || !hoursSpent || ids.length === 0) {
      setError('All fields except comments are required.');
      return;
    }
    const entry = {
      date: today,
      employeeId,
      projectId,
      objectIds: ids,
      taskType,
      hoursSpent: Number(hoursSpent),
      statusPerObject: statusPerObject.map((obj, i) => ({ objectId: ids[i], status: obj.status })),
      comments,
    };
    try {
      await saveJournalEntry(entry);
      setSubmitted(true);
      setError('Manual entry added successfully.');
    } catch (err) {
      setError('Failed to add manual entry: ' + (err.message || err));
    }
  }

  return (
    <form className="max-w-lg mx-auto p-6 bg-white rounded shadow space-y-4" onSubmit={handleSubmit}>
      <h2 className="text-xl font-bold mb-2">Daily Journal Entry</h2>
      {error && <div className="text-red-500">{error}</div>}
      <div>
        <label className="block font-medium">Project</label>
        <select className="w-full border rounded p-2" value={projectId} onChange={e => setProjectId(e.target.value)} required>
          <option value="">Select Project</option>
          {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </div>
      <div>
        <label className="block font-medium">Task Type</label>
        <select className="w-full border rounded p-2" value={taskType} onChange={e => setTaskType(e.target.value)} required>
          <option value="">Select Task Type</option>
          {TASK_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
      <div>
        <label className="block font-medium">Hours Spent</label>
        <input type="number" min="0" step="0.1" className="w-full border rounded p-2" value={hoursSpent} onChange={e => setHoursSpent(e.target.value)} required />
      </div>
      <div>
        <label className="block font-medium">Object IDs (comma separated)</label>
        <input type="text" className="w-full border rounded p-2" value={objectIds} onChange={handleObjectIdsChange} required />
      </div>
      <div>
        <label className="block font-medium">Status per Object</label>
        {statusPerObject.map((obj, idx) => (
          <div key={obj.objectId} className="flex items-center space-x-2 mb-1">
            <span className="w-24">{obj.objectId}</span>
            <select className="border rounded p-1" value={obj.status} onChange={e => handleStatusChange(idx, e.target.value)}>
              {STATUS_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
        ))}
      </div>
      <div>
        <label className="block font-medium">Comments</label>
        <textarea className="w-full border rounded p-2" value={comments} onChange={e => setComments(e.target.value)} />
      </div>
      <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" disabled={submitted}>
        {submitted ? 'Submitted' : 'Save Entry'}
      </button>
      <button type="button" className="ml-2 bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700" onClick={handleManualEntry}>
        Manual Entry
      </button>
    </form>
  );
}
