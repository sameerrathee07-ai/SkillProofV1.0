import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../hooks/useAuth'

export default function PostProblemPage() {
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('Hospitality')
  const [budget_range, setBudgetRange] = useState('')
  const [timeline, setTimeline] = useState('')
  const [errors, setErrors] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const { user } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors([])
    setLoading(true)
    try {
      await api.post('/problems', { description, category, budget_range, timeline })
      navigate('/')
    } catch (err: any) {
      setErrors(err.response?.data?.errors || ['Failed to create problem'])
    } finally {
      setLoading(false)
    }
  }

  if (!user || user.role !== 'poster') {
    return <div className="container">Only problem posters can access this page.</div>
  }

  return (
    <div className="container">
      <h1 style={{ marginBottom: 24 }}>Post a Problem</h1>
      <div className="card">
        {errors.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            {errors.map((err, i) => <div key={i} className="error">{err}</div>)}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Problem Description (min 15 words, include action verb)</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              rows={5}
              required
            />
            <small style={{ color: '#666' }}>E.g., We need an automated system to schedule hotel housekeeping shifts and alert managers when rooms are delayed.</small>
          </div>
          <div className="form-group">
            <label>Category</label>
            <select value={category} onChange={e => setCategory(e.target.value)}>
              <option value="Hospitality">Hospitality</option>
              <option value="Financial Services">Financial Services</option>
              <option value="Education">Education</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label>Budget / Value Range (include currency)</label>
            <input
              type="text"
              value={budget_range}
              onChange={e => setBudgetRange(e.target.value)}
              placeholder="Rs 5000 per month"
              required
            />
          </div>
          <div className="form-group">
            <label>Timeline</label>
            <input
              type="text"
              value={timeline}
              onChange={e => setTimeline(e.target.value)}
              placeholder="2 weeks"
              required
            />
          </div>
          <button type="submit" disabled={loading} style={{ width: '100%' }}>
            {loading ? 'Posting...' : 'Publish Problem'}
          </button>
        </form>
      </div>
    </div>
  )
}