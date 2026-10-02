import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { problemsApi } from '../utils/api';
import type { ProblemValidationResponse, ValidationError } from '../types';

const CATEGORIES = ['Hospitality', 'Financial Services', 'Education', 'Other'];

export default function PostProblem() {
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [budget_range, setBudgetRange] = useState('');
  const [timeline, setTimeline] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [validating, setValidating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const navigate = useNavigate();

  const validateField = (field: string, value: string) => {
    const newErrors = { ...errors };
    delete newErrors[field];
    setErrors(newErrors);
  };

  const handleValidate = async () => {
    setValidating(true);
    setErrors({});
    try {
      const res = await problemsApi.validate({ description, category, budget_range, timeline });
      if (!res.data.valid) {
        const newErrors: Record<string, string> = {};
        res.data.errors.forEach((e: ValidationError) => {
          newErrors[e.field] = e.message;
        });
        setErrors(newErrors);
      } else {
        setErrors({});
      }
    } catch (err) {
      console.error('Validation error:', err);
    } finally {
      setValidating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError('');
    setSubmitting(true);
    try {
      const res = await problemsApi.validate({ description, category, budget_range, timeline });
      if (!res.data.valid) {
        const newErrors: Record<string, string> = {};
        res.data.errors.forEach((e: ValidationError) => {
          newErrors[e.field] = e.message;
        });
        setErrors(newErrors);
        return;
      }
      const created = await problemsApi.create({ description, category, budget_range, timeline });
      navigate(`/problems/${created.data.id}`);
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || 'Failed to create problem');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '700px' }}>
      <div className="page-header">
        <h1 className="page-title">Post a Problem</h1>
        <p className="page-subtitle">Describe your operational problem clearly. All fields are validated before publishing.</p>
      </div>

      <div className="card" style={{ padding: '2rem' }}>
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label htmlFor="description" className="label">Problem Description <span className="text-error">*</span></label>
            <textarea
              id="description"
              className={`input ${errors.description ? 'input-error' : ''}`}
              value={description}
              onChange={(e) => { setDescription(e.target.value); validateField('description', e.target.value); }}
              rows={6}
              placeholder="Describe the problem in detail (at least 15 words, include action verbs like automate, schedule, optimize)..."
              required
            />
            {errors.description && <p className="error-text">{errors.description}</p>}
            <p className="text-xs text-secondary mt-1">Minimum 15 words with at least one action verb (automate, schedule, optimize, reduce, etc.)</p>
          </div>

          <div className="mb-6">
            <label htmlFor="category" className="label">Category <span className="text-error">*</span></label>
            <select
              id="category"
              className={`input ${errors.category ? 'input-error' : ''}`}
              value={category}
              onChange={(e) => { setCategory(e.target.value); validateField('category', e.target.value); }}
              required
            >
              <option value="">Select category</option>
              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            {errors.category && <p className="error-text">{errors.category}</p>}
          </div>

          <div className="grid grid-2 mb-6">
            <div>
              <label htmlFor="budget_range" className="label">Budget / Value Range <span className="text-error">*</span></label>
              <input
                id="budget_range"
                type="text"
                className={`input ${errors.budget_range ? 'input-error' : ''}`}
                value={budget_range}
                onChange={(e) => { setBudgetRange(e.target.value); validateField('budget_range', e.target.value); }}
                placeholder="e.g., Rs 50,000 per month"
                required
              />
              {errors.budget_range && <p className="error-text">{errors.budget_range}</p>}
              <p className="text-xs text-secondary mt-1">Must include currency (Rs, INR, ₹, $) and a number</p>
            </div>

            <div>
              <label htmlFor="timeline" className="label">Timeline <span className="text-error">*</span></label>
              <input
                id="timeline"
                type="text"
                className={`input ${errors.timeline ? 'input-error' : ''}`}
                value={timeline}
                onChange={(e) => { setTimeline(e.target.value); validateField('timeline', e.target.value); }}
                placeholder="e.g., 4 weeks, 30 days, 2024-12-31"
                required
              />
              {errors.timeline && <p className="error-text">{errors.timeline}</p>}
              <p className="text-xs text-secondary mt-1">Must include duration (days, weeks, months) or a date</p>
            </div>
          </div>

          {submitError && (
            <div className="badge badge-error mb-4" style={{ width: '100%', justifyContent: 'center' }}>
              {submitError}
            </div>
          )}

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button type="button" onClick={handleValidate} className="btn btn-secondary" disabled={validating}>
              {validating ? 'Validating...' : 'Validate'}
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Publishing...' : 'Publish Problem'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}