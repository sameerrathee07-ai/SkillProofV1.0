import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { pitchApi } from '../utils/api';
import type { PitchSession, Message, PitchChatResponse } from '../types';

const STEP_QUESTIONS = [
  "Step 1 — Idea: In one sentence, what does your solution do for this problem? Specific enough that a stranger could explain it back.",
  "Step 2 — Customer: Who at the company faces this problem (role or team) and what exactly is the pain?",
  "Step 3 — Cost & Value: What will it cost the company, and how is that justified?",
  "Step 4 — Alternatives: Name at least 2 alternative ways to solve this (tools, vendors or manual approaches) and why yours is better.",
  "Step 5 — Solver: What relevant experience do you have, and what is your unfair advantage?",
];

export default function PitchChat() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [session, setSession] = useState<PitchSession | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [answer, setAnswer] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [pitchComplete, setPitchComplete] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const [sessionRes, messagesRes] = await Promise.all([
          pitchApi.get(parseInt(sessionId!)),
          pitchApi.messages(parseInt(sessionId!)),
        ]);
        setSession(sessionRes.data);
        setMessages(messagesRes.data);
        setPitchComplete(sessionRes.data.completed);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load session');
      }
    };
    fetchSession();
  }, [sessionId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim() || sending) return;

    setError('');
    setSending(true);
    const currentAnswer = answer;
    setAnswer('');

    try {
      const res = await pitchApi.chat(parseInt(sessionId!), currentAnswer);
      setMessages(prev => [...prev, { id: Date.now(), session_id: parseInt(sessionId!), role: 'user', content: currentAnswer, created_at: new Date().toISOString() }, { id: Date.now() + 1, session_id: parseInt(sessionId!), role: 'assistant', content: res.data.reply, created_at: new Date().toISOString() }]);
      setSession(prev => prev ? { ...prev, current_step: res.data.current_step, completed: res.data.pitch_complete } : null);
      setPitchComplete(res.data.pitch_complete);
      if (res.data.pitch_complete) {
        navigate(`/pitch/${sessionId}/results`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send answer');
      setAnswer(currentAnswer);
    } finally {
      setSending(false);
    }
  };

  if (!session) {
    return <div className="text-center text-secondary py-8">Loading session...</div>;
  }

  const currentStep = session.current_step;
  const progress = ((currentStep - 1) / 5) * 100;

  return (
    <div style={{ maxWidth: '800px' }}>
      <div className="page-header">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="page-title">Guided Pitch</h1>
            <p className="page-subtitle">Problem ID: {session.problem_id} • Attempt {session.attempt_no}</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-secondary">Tokens: {session.current_step > 1 ? '—' : '—'}</div>
            <div className="text-lg font-semibold text-primary">{session.current_step}/5</div>
          </div>
        </div>
        <div style={{ height: '6px', background: 'var(--color-border)', borderRadius: '3px', overflow: 'hidden' }}>
          <div style={{ height: '100%', background: 'var(--color-primary)', width: `${progress}%`, transition: 'width 0.3s ease' }} />
        </div>
      </div>

      <div className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', height: '60vh' }}>
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem' }}>
          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
              <div
                className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-primary text-white rounded-br-none' : 'bg-gray-100 text-gray-900 rounded-bl-none'}`}
                style={{ background: msg.role === 'user' ? 'var(--color-primary)' : 'var(--color-bg)', color: msg.role === 'user' ? 'white' : 'var(--color-text)', borderRadius: msg.role === 'user' ? 'var(--radius-lg) var(--radius-lg) 0 var(--radius-lg)' : 'var(--radius-lg) var(--radius-lg) var(--radius-lg) 0' }}
              >
                <div className="text-sm">{msg.content}</div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {!pitchComplete && (
          <div className="border-t border-gray-200 pt-4 mt-4">
            <div className="mb-3">
              <span className="badge badge-info mb-1">Step {currentStep} of 5</span>
              <p className="text-secondary">{STEP_QUESTIONS[currentStep - 1]}</p>
            </div>

            {error && (
              <div className="badge badge-error mb-3" style={{ width: '100%', justifyContent: 'center' }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <textarea
                className="input mb-3"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                rows={3}
                placeholder="Type your answer here..."
                disabled={sending}
                required
              />
              <button type="submit" className="btn btn-primary w-full" disabled={sending || !answer.trim()}>
                {sending ? 'Submitting...' : 'Submit Answer'}
              </button>
            </form>
          </div>
        )}

        {pitchComplete && (
          <div className="text-center py-8">
            <div className="badge badge-success mb-3" style={{ fontSize: '1rem', padding: '0.75rem 1.5rem' }}>
              Pitch Complete!
            </div>
            <p className="text-secondary mb-6">Your pitch has been submitted for scoring.</p>
            <button onClick={() => navigate(`/pitch/${sessionId}/results`)} className="btn btn-primary">
              View Results
            </button>
          </div>
        )}
      </div>
    </div>
  );
}