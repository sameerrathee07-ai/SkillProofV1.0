import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { ChatResponse } from '../types'
import { useAuth } from '../hooks/useAuth'

export default function PitchPage() {
  const { id } = useParams<{ id: string }>()
  const [step, setStep] = useState(1)
  const [_reply, setReply] = useState('')
  const [pitchComplete, setPitchComplete] = useState(false)
  const [remainingTokens, setRemainingTokens] = useState(0)
  const [messages, setMessages] = useState<{ role: 'assistant' | 'user'; content: string }[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    api.post(`/pitch/problems/${id}/start`).then(r => {
      setStep(r.data.current_step)
      setReply(r.data.reply)
      setRemainingTokens(r.data.remaining_tokens)
      setMessages(r.data.messages || [{ role: 'assistant', content: r.data.reply }])
    }).catch(() => navigate('/'))
  }, [id, navigate])

  const sendMessage = async () => {
    if (!input.trim() || sending) return
    setError('')
    setSending(true)
    const userMsg = input
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setInput('')
    try {
      const resp = await api.post(`/pitch/${id}/chat`, { content: userMsg })
      const data: ChatResponse = resp.data
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
      setStep(data.current_step)
      setPitchComplete(data.pitch_complete)
      setRemainingTokens(data.remaining_tokens)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send')
      setMessages(prev => prev.slice(0, -1))
      setInput(userMsg)
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!user || user.role !== 'solver') {
    return <div className="container">Only solvers can pitch.</div>
  }

  return (
    <div className="chat-container" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div className="chat-header">
        <h2>Guided Pitch — Step {step} of 5</h2>
        <div className="meta">
          Pass mark: 6/10 | Tokens: <span className="token-display">{remainingTokens}</span>
        </div>
      </div>
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      {error && <div className="error" style={{ margin: '0 16px 16px' }}>{error}</div>}
      {!pitchComplete && (
        <div className="chat-input">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your answer..."
            disabled={sending}
          />
          <button onClick={sendMessage} disabled={sending || !input.trim()}>Send</button>
        </div>
      )}
      {pitchComplete && (
        <div className="chat-input" style={{ justifyContent: 'center' }}>
          <button onClick={() => navigate(`/results/${id}`)} style={{ minWidth: 200 }}>View Results</button>
        </div>
      )}
    </div>
  )
}