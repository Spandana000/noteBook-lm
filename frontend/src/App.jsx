import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Image as ImageIcon, Sun, Moon, Plus, FileText, Loader2, Bot, User, X, Trash2, FileCheck, Mic, Menu, MoreVertical, Pin, Edit2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './App.css';
import WordOverlay from './WordOverlay';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [includeImages, setIncludeImages] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [loading, setLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  // Session State
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);

  // Menu State
  const [activeMenuId, setActiveMenuId] = useState(null);
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editTitle, setEditTitle] = useState("");

  // History State (Renamed to avoid conflict)
  const [localPromptHistory, setLocalPromptHistory] = useState([]);
  const [localHistoryIndex, setLocalHistoryIndex] = useState(-1);

  // Voice State
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  // Overlay State
  const [overlayData, setOverlayData] = useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  // Initial Load
  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const res = await axios.get("http://localhost:8000/sessions");
      setSessions(res.data);
    } catch (err) {
      console.error("Failed to fetch sessions", err);
    }
  };

  const createSession = async () => {
    try {
      const res = await axios.post("http://localhost:8000/sessions");
      setCurrentSessionId(res.data.session_id);
      setMessages([]);
      setUploadedFile(null);
      fetchSessions();
      // Close mobile sidebar
      if (window.innerWidth < 768) setSidebarOpen(false);
    } catch (err) {
      console.error("Failed to create session", err);
    }
  };

  const loadSession = async (sessionId) => {
    if (sessionId === currentSessionId) {
      if (window.innerWidth < 768) setSidebarOpen(false);
      return;
    }
    try {
      setLoading(true);
      setCurrentSessionId(sessionId);
      const res = await axios.get(`http://localhost:8000/sessions/${sessionId}`);
      setMessages(res.data.messages || []);
      setLoading(false);
      if (window.innerWidth < 768) setSidebarOpen(false);
    } catch (err) {
      console.error("Failed to load session", err);
      setLoading(false);
    }
  };

  const updateSession = async (sessionId, updates) => {
    try {
      await axios.put(`http://localhost:8000/sessions/${sessionId}`, updates);
      fetchSessions();
    } catch (err) {
      console.error("Update failed", err);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!confirm("Are you sure you want to delete this chat?")) return;
    try {
      await axios.delete(`http://localhost:8000/sessions/${sessionId}`);
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
        setMessages([]);
      }
      fetchSessions();
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const clearAllSessions = async () => {
    if (!confirm("WARNING: This will delete ALL conversation history. Are you sure?")) return;
    try {
      await axios.delete("http://localhost:8000/sessions");
      setSessions([]);
      setMessages([]);
      setCurrentSessionId(null);
    } catch (err) {
      console.error("Clear all failed", err);
    }
  };

  // Voice Logic
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
        }
        if (finalTranscript) {
          setInput(prev => prev + (prev ? ' ' : '') + finalTranscript);
          if (sendTimeoutRef.current) clearTimeout(sendTimeoutRef.current);
          sendTimeoutRef.current = setTimeout(() => {
            onSend();
            toggleListening();
          }, 1500);
        }
      };

      recognitionRef.current.onerror = (e) => setIsListening(false);
    }
  }, [isListening]);

  const toggleListening = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };
  const sendTimeoutRef = useRef(null);

  // Context Menu Logic
  const handleContextMenu = async (e) => {
    e.preventDefault();
    const selection = window.getSelection();
    let word = selection.toString().trim();
    if (word) {
      setOverlayData({ x: e.clientX, y: e.clientY, word, definition: "Searching..." });
      try {
        const res = await axios.post("http://localhost:8000/define", { word, context: "" });
        setOverlayData(prev => prev ? { ...prev, definition: res.data.definition || "No definition found." } : null);
      } catch (err) {
        setOverlayData(prev => prev ? { ...prev, definition: "Error fetching definition." } : null);
      }
    }
  };

  const handleAskLumina = () => {
    if (overlayData) {
      setInput(`What does "${overlayData.word}" mean?`);
      setOverlayData(null);
    }
  };

  const onSend = async () => {
    if (sendTimeoutRef.current) clearTimeout(sendTimeoutRef.current);
    if (!input.trim() && !uploadedFile) return;
    if (loading) return;

    let activeSession = currentSessionId;
    if (!activeSession) {
      try {
        const sRes = await axios.post("http://localhost:8000/sessions");
        activeSession = sRes.data.session_id;
        setCurrentSessionId(activeSession);
        fetchSessions();
      } catch (e) {
        alert("Failed to start session");
        return;
      }
    }

    const userMsg = input;
    // Update local history
    setLocalPromptHistory(prev => [...prev, userMsg]);
    setLocalHistoryIndex(-1);

    setInput("");
    setUploadedFile(null);
    setLoading(true);

    const optimMsg = { role: 'user', content: userMsg };
    setMessages(prev => [...prev, optimMsg]);

    try {
      const res = await axios.post("http://localhost:8000/chat", {
        message: userMsg,
        include_images: includeImages,
        session_id: activeSession
      });

      const botMsg = {
        role: 'bot',
        content: res.data.answer || "No response.",
        images: res.data.images || []
      };
      setMessages(prev => [...prev, botMsg]);

      fetchSessions();

    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: "Error connecting to server." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploadedFile({ name: file.name, uploading: true });
    const formData = new FormData();
    formData.append('file', file);
    try {
      await axios.post("http://localhost:8000/upload", formData);
      setUploadedFile({ name: file.name, uploading: false });
      textareaRef.current?.focus();
    } catch {
      setUploadedFile(null);
      alert("Upload failed.");
    } finally {
      e.target.value = null;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSend(); return; }
    if (e.key === 'ArrowUp') {
      if (!localPromptHistory.length) return;
      e.preventDefault();
      setLocalHistoryIndex(prev => {
        const idx = prev === -1 ? localPromptHistory.length - 1 : Math.max(0, prev - 1);
        setInput(localPromptHistory[idx]);
        return idx;
      });
    }
    if (e.key === 'ArrowDown') {
      if (!localPromptHistory.length) return;
      e.preventDefault();
      setLocalHistoryIndex(prev => {
        const idx = prev + 1;
        if (idx >= localPromptHistory.length) { setInput(""); return -1; }
        setInput(localPromptHistory[idx]);
        return idx;
      });
    }
  };

  // Typing Animation State
  const [displayText, setDisplayText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    if (messages.length > 0) return; // Pause if not visible

    const word = "User";
    const typeSpeed = isDeleting ? 100 : 150;
    const pauseTime = 2000;

    const timeout = setTimeout(() => {
      if (!isDeleting && displayText === word) {
        setTimeout(() => setIsDeleting(true), pauseTime);
      } else if (isDeleting && displayText === "") {
        setIsDeleting(false);
      } else {
        setDisplayText(word.substring(0, displayText.length + (isDeleting ? -1 : 1)));
      }
    }, typeSpeed);

    return () => clearTimeout(timeout);
  }, [displayText, isDeleting, messages.length]);

  return (
    <div className={`app-wrapper ${darkMode ? 'dark-mode' : 'light-mode'} ${!sidebarOpen ? 'sidebar-collapsed' : ''}`} onClick={() => { setOverlayData(null); setActiveMenuId(null); }}>
      {overlayData && (
        <WordOverlay position={overlayData} word={overlayData.word} definition={overlayData.definition} onClose={() => setOverlayData(null)} onAsk={handleAskLumina} />
      )}

      <button className={`sidebar-toggle-btn ${sidebarOpen ? 'open' : ''}`} onClick={(e) => { e.stopPropagation(); setSidebarOpen(!sidebarOpen); }}>
        <Menu size={20} />
      </button>

      <aside className="gemini-sidebar">
        <div className="sidebar-header">
          <div className="brand" style={{ fontWeight: 700, fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <img src="/logo.png" alt="Lumina Logo" style={{ width: '28px', height: '28px', objectFit: 'contain', borderRadius: '4px' }} />
            Lumina
          </div>
          <button className="new-btn" onClick={createSession} style={{ marginTop: '10px', width: '100%', justifyContent: 'center' }}>
            <Plus size={16} /> New chat
          </button>
        </div>

        <div className="sidebar-nav">
          <div className="section-label">Recent Chats</div>
          {sessions.map(s => (
            <div key={s.id} className={`nav-item ${currentSessionId === s.id ? 'active' : ''}`} onClick={() => loadSession(s.id)}>
              {s.pinned && <Pin size={12} className="pin-icon" style={{ marginRight: 4 }} />}
              {editingSessionId === s.id ? (
                <input
                  autoFocus
                  className="rename-input"
                  value={editTitle}
                  onClick={e => e.stopPropagation()}
                  onChange={e => setEditTitle(e.target.value)}
                  onBlur={() => { updateSession(s.id, { title: editTitle }); setEditingSessionId(null); }}
                  onKeyDown={e => { if (e.key === 'Enter') { updateSession(s.id, { title: editTitle }); setEditingSessionId(null); } }}
                />
              ) : (
                <span className="nav-text" style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.title}</span>
              )}

              <div className="menu-trigger" onClick={(e) => { e.stopPropagation(); setActiveMenuId(activeMenuId === s.id ? null : s.id); }}>
                <MoreVertical size={14} />
              </div>

              {activeMenuId === s.id && (
                <div className="context-menu" onClick={e => e.stopPropagation()}>
                  <div className="menu-item" onClick={() => { setEditTitle(s.title); setEditingSessionId(s.id); setActiveMenuId(null); }}>
                    <Edit2 size={12} /> Rename
                  </div>
                  <div className="menu-item" onClick={() => { updateSession(s.id, { pinned: !s.pinned }); setActiveMenuId(null); }}>
                    <Pin size={12} /> {s.pinned ? 'Unpin' : 'Pin'}
                  </div>
                  <div className="menu-item delete" onClick={() => { deleteSession(s.id); setActiveMenuId(null); }}>
                    <Trash2 size={12} /> Delete
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <button className="footer-btn" onClick={clearAllSessions}>
            <Trash2 size={16} /> Clear all conversations
          </button>
          <button className="footer-btn" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? <Sun size={16} /> : <Moon size={16} />} {darkMode ? 'Light mode' : 'Dark mode'}
          </button>
        </div>
      </aside>

      <main className="gemini-main">
        <div className="top-header">
          <span className="gradient-text">Lumina</span>
        </div>
        <div className="message-container" onContextMenu={handleContextMenu}>
          {!messages.length && !loading && (
            <div className="hero">
              <h1>
                Hey <span className="gradient-text">{displayText}</span><span className="cursor">|</span>
              </h1>
              <p>How can I help you today?</p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`msg-row ${m.role}`}>
              <div className="avatar">{m.role === 'bot' ? <Bot size={18} /> : <User size={18} />}</div>
              <div className="msg-body">
                <div className="markdown-content"><ReactMarkdown>{m.content}</ReactMarkdown></div>
                {m.images?.length > 0 && (
                  <div className="multimedia-gallery-container">
                    <div className="gallery-header">Visual Context</div>
                    <div className="multimedia-grid">
                      {m.images.map((img, idx) => (
                        <div key={idx} className="image-card">
                          <img src={img.url} alt={img.title} />
                          <div className="image-overlay"><span className="context-label">{img.context_label}</span></div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="msg-row bot">
              <div className="avatar"><Bot size={18} /></div>
              <div className="msg-body loading-state"><Loader2 className="spin" size={18} /><span>Lumina is thinking...</span></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-section">
          <div className="input-capsule">
            {uploadedFile && (
              <div className="file-preview-container">
                <div className="file-chip"><FileCheck size={12} /> {uploadedFile.name} <X size={12} onClick={() => setUploadedFile(null)} /></div>
              </div>
            )}
            <div className="left-actions">
              <button className="img-btn" onClick={() => document.getElementById('up').click()}><Plus size={20} /><input id="up" type="file" hidden onChange={handleUpload} /></button>
              <div className={`toggle-switch ${includeImages ? 'active' : ''}`} onClick={() => setIncludeImages(!includeImages)}><div className="toggle-thumb" /></div>
            </div>
            <textarea ref={textareaRef} value={input} onChange={e => setInput(e.target.value)} onKeyDown={handleKeyDown} placeholder="Ask anything..." rows={1} />
            <button className={`img-btn mic-btn ${isListening ? 'listening' : ''}`} onClick={toggleListening}><Mic size={20} /></button>
            <button className="send-btn" onClick={onSend} disabled={!input.trim()}><Send size={18} /></button>
          </div>
          <span className="footer-text">Lumina can make mistakes. Verify information.</span>
        </div>
      </main>
    </div>
  );
}