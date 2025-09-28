'use client';

import { useEffect, useRef, useState } from 'react';

type Investor = {
  name: string;
  type: string;
  focus: string;
  location: string;
  score: number;
};

type Msg = { sender: 'bot' | 'user'; text?: string; investors?: Investor[] };

export default function Home() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([
    { sender: 'bot', text: "Hi! I’m your AI investor matcher. Click Start to begin or just ask me anything." }
  ]);

  // guided flow state
  const [step, setStep] = useState<null | number>(null);
  const [profile, setProfile] = useState<{ industry?: string; stage?: string; region?: string; traction?: string }>({});

  const bottomRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // === call /match (investor matching) ===
  async function sendProfile() {
    const desc = `Industry: ${profile.industry}. Stage: ${profile.stage}. Region: ${profile.region}. Traction: ${profile.traction}`;
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:5000/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: desc })
      });
      const data = await res.json();
      setMessages(m => [
        ...m,
        {
          sender: 'bot',
          text: data?.length === 0 ? '❌ No matches found. Try adding more details.' : undefined,
          investors: Array.isArray(data) ? data : []
        }
      ]);
    } catch {
      setMessages(m => [...m, { sender: 'bot', text: '⚠️ Server error. Is Flask running?' }]);
    } finally {
      setLoading(false);
      setStep(null);
    }
  }

  // === call /chat (Phi-2) ===
  async function sendChatMessage(msg: string) {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      setMessages(m => [...m, { sender: 'bot', text: data.answer }]);
    } catch {
      setMessages(m => [...m, { sender: 'bot', text: '⚠️ Chat server error.' }]);
    } finally {
      setLoading(false);
    }
  }

  // handle guided step answers
  function handleStepSubmit() {
    if (!input.trim()) return;

    const answer = input.trim();
    setMessages(m => [...m, { sender: 'user', text: answer }]);
    setInput('');

    if (step === 1) {
      setProfile(p => ({ ...p, industry: answer }));
      setMessages(m => [...m, { sender: 'bot', text: 'What funding stage are you at? (Pre-seed, Seed, Series A...)' }]);
      setStep(2);
    } else if (step === 2) {
      setProfile(p => ({ ...p, stage: answer }));
      setMessages(m => [...m, { sender: 'bot', text: 'Which region or market are you targeting?' }]);
      setStep(3);
    } else if (step === 3) {
      setProfile(p => ({ ...p, region: answer }));
      setMessages(m => [...m, { sender: 'bot', text: 'Briefly, what traction or milestone have you achieved?' }]);
      setStep(4);
    } else if (step === 4) {
      setProfile(p => ({ ...p, traction: answer }));
      setMessages(m => [...m, { sender: 'bot', text: 'Thanks! Let me find investors for you…' }]);
      sendProfile();
    }
  }

  // handle free chat
  function handleFreeChat() {
    if (!input.trim()) return;
    const msg = input.trim();
    setMessages(m => [...m, { sender: 'user', text: msg }]);
    setInput('');
    sendChatMessage(msg);
  }

  return (
    <main style={styles.page}>
      <div style={styles.card}>
        <div style={styles.header}>AI Investor Chat</div>

        <div style={styles.chat}>
          {messages.map((m, i) => (
            <div key={i} style={{ ...styles.row, justifyContent: m.sender === 'user' ? 'flex-end' : 'flex-start' }}>
              {m.sender === 'user' && (
                <div style={{ ...styles.bubbleUser }}>
                  <div style={styles.senderLabel}>You</div>
                  <div style={styles.text}>{m.text}</div>
                </div>
              )}
              {m.sender === 'bot' && (
                <div style={{ ...styles.bubbleBot }}>
                  <div style={styles.senderLabel}>Bot</div>
                  {m.text && <div style={styles.text}>{m.text}</div>}
                  {m.investors && m.investors.length > 0 && (
                    <div style={styles.grid}>
                      {m.investors.map((inv, j) => (
                        <div key={j} style={styles.cardItem}>
                          <h4 style={{ marginBottom: 6 }}>{inv.name}</h4>
                          <p><strong>Type:</strong> {inv.type || '—'}</p>
                          <p><strong>Focus:</strong> {inv.focus || '—'}</p>
                          <p><strong>Location:</strong> {inv.location || '—'}</p>
                          <p><strong>Score:</strong> {inv.score?.toFixed(2) || '—'}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  {i === 0 && (
                    <button
                      onClick={() => {
                        setMessages(m => [...m, { sender: 'bot', text: 'Great! First, what industry are you in?' }]);
                        setStep(1);
                      }}
                      style={styles.startBtn}
                    >
                      Start Guided Flow
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ ...styles.row, justifyContent: 'flex-start' }}>
              <div style={{ ...styles.bubbleBot }}>
                <div style={styles.senderLabel}>Bot</div>
                <div style={styles.text}>typing…</div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div style={styles.inputBar}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (step ? handleStepSubmit() : handleFreeChat())}
            placeholder="Type your message…"
            disabled={loading}
            style={styles.input}
          />
          <button
            onClick={step ? handleStepSubmit : handleFreeChat}
            disabled={loading || !input.trim()}
            style={styles.button}
          >
            {loading ? '…' : 'Send'}
          </button>
        </div>
      </div>
    </main>
  );
}

/* -------- styles -------- */
const styles: Record<string, React.CSSProperties> = {
  page: { minHeight: '100dvh', background: '#0f172a', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 },
  card: { width: 'min(1280px, 100%)', background: '#0b1220', border: '1px solid #1f2937', borderRadius: 18, boxShadow: '0 12px 34px rgba(0,0,0,0.4)', overflow: 'hidden', color: '#e5e7eb' },
  header: { padding: '16px 20px', fontWeight: 700, fontSize: 18, borderBottom: '1px solid #1f2937', background: 'linear-gradient(90deg,#1e293b,#111827)' },
  chat: { padding: 20, height: 750, overflowY: 'auto', background: 'radial-gradient(1200px 400px at 30% -10%, rgba(99,102,241,0.08), transparent), radial-gradient(1000px 400px at 90% 10%, rgba(34,197,94,0.08), transparent)' },
  row: { display: 'flex', marginBottom: 12 },
  bubbleBot: { background: '#0f172a', border: '1px solid #374151', color: '#e5e7eb', padding: '12px 14px', borderRadius: 14, maxWidth: '100%' },
  bubbleUser: { background: '#1d4ed8', border: '1px solid #60a5fa', color: '#fff', padding: '12px 14px', borderRadius: 14, maxWidth: '90%' },
  senderLabel: { opacity: 0.8, fontSize: 12, marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.4 },
  text: { whiteSpace: 'pre-wrap', wordBreak: 'break-word', overflowWrap: 'anywhere', lineHeight: 1.5, fontSize: 15 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16, marginTop: 12 },
  cardItem: { background: '#111827', border: '1px solid #374151', borderRadius: 12, padding: 12, fontSize: 14, lineHeight: 1.4 },
  inputBar: { display: 'flex', gap: 10, padding: 14, borderTop: '1px solid #1f2937', background: '#0b1220' },
  input: { flex: 1, padding: '12px 14px', borderRadius: 12, border: '1px solid #374151', background: '#0f172a', color: '#e5e7eb', outline: 'none', fontSize: 15 },
  button: { padding: '12px 18px', borderRadius: 12, border: '1px solid #60a5fa', background: '#1d4ed8', color: '#fff', cursor: 'pointer', fontWeight: 600, fontSize: 15 },
  startBtn: { marginTop: 12, padding: '10px 16px', borderRadius: 10, border: '1px solid #60a5fa', background: '#1d4ed8', color: '#fff', cursor: 'pointer', fontWeight: 600 }
};
