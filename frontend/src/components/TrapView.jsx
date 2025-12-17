import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';

export function TrapView({ round, playerId, onSubmit }) {
    const [trapText, setTrapText] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = useCallback(async () => {
        if (!trapText.trim()) return;
        setLoading(true);
        await onSubmit(trapText);
        setLoading(false);
    }, [trapText, onSubmit]);

    // Keyboard shortcut: Cmd/Ctrl + Enter to submit
    useEffect(() => {
        const handleKeyDown = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && !loading && trapText.trim()) {
                e.preventDefault();
                handleSubmit();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [loading, trapText, handleSubmit]);

    if (round.trap_proposals && round.trap_proposals[playerId]) {
        return (
            <div className="card" style={{ textAlign: 'center' }}>
                <h2>TRAP DESIGNED</h2>
                <p>Your blueprint has been submitted. The AI is visualizing your doom...</p>
                <span className="loader"></span>
            </div>
        );
    }

    return (
        <div className="card">
            <h2 style={{ marginBottom: '1rem', color: 'var(--accent)' }}>BLIND ARCHITECT</h2>
            <p style={{ marginBottom: '1.5rem', opacity: 0.8 }}>
                Design a scenario to kill your opponents. The best visual wins.
            </p>

            <textarea
                value={trapText}
                onChange={(e) => setTrapText(e.target.value)}
                placeholder="A room filled with laser sharks..."
                style={{
                    width: '100%',
                    minHeight: '120px',
                    background: 'rgba(0,0,0,0.3)',
                    border: '1px solid var(--accent)',
                    color: 'white',
                    padding: '1rem',
                    borderRadius: '8px',
                    marginBottom: '1.5rem',
                    resize: 'vertical'
                }}
            />

            <button
                className="primary"
                onClick={handleSubmit}
                disabled={loading || !trapText.trim()}
                style={{ width: '100%', backgroundColor: 'var(--accent)', color: 'black' }}
            >
                {loading ? 'CONSTRUCTING...' : 'SUBMIT TRAP'}
                {!loading && <span style={{ opacity: 0.6, fontSize: '0.75rem', marginLeft: '0.5rem' }}>(⌘↵)</span>}
            </button>
        </div>
    );
}
