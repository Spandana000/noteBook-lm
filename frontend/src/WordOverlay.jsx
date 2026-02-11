import React from 'react';
import ReactDOM from 'react-dom';
import { X, Sparkles } from 'lucide-react';

const WordOverlay = ({ position, word, definition, onClose, onAsk }) => {
    if (!position) return null;

    // Ensure it doesn't go off-screen
    const style = {
        top: Math.min(position.y, window.innerHeight - 320) + 'px',
        left: Math.min(position.x, window.innerWidth - 340) + 'px',
    };

    return ReactDOM.createPortal(
        <div className="word-overlay-container" style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', zIndex: 1000, pointerEvents: 'none' }}>
            <div className="word-overlay" style={{ ...style, pointerEvents: 'auto' }}>
                <div className="overlay-header">
                    <span className="overlay-word">{word}</span>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', display: 'flex' }}>
                        <X size={18} />
                    </button>
                </div>

                <div className="overlay-def">
                    {definition ? (
                        <p>{definition}</p>
                    ) : (
                        <div style={{ padding: '10px 0', opacity: 0.7 }}>Analyzing with Intelligence...</div>
                    )}
                </div>

                <button className="overlay-btn" onClick={() => { onAsk(); onClose(); }}>
                    <Sparkles size={16} /> Ask Lumina Context
                </button>
            </div>
        </div>,
        document.body
    );
};

export default WordOverlay;
