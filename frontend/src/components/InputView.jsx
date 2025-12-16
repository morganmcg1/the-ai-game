import React, { useState } from 'react';
import { motion } from 'framer-motion';

export function InputView({ round, playerId, onSubmit }) {
    const [strategy, setStrategy] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        if (!strategy.trim()) return;
        setLoading(true);
        await onSubmit(strategy);
        setLoading(false);
    };

    const hasSubmitted = round.players_submitted?.includes(playerId); // Not strictly in model yet but logic handle outside or via local state if needed. 
    // For MVP, we pass 'hasSubmitted' prop or rely on parent state. 
    // Actually, parent App.jsx will handle knowing if we submitted based on player state.

    return (
        <div className="card">
            <h2 style={{ marginBottom: '1rem', color: 'var(--secondary)' }}>STRATEGY</h2>
            <p style={{ marginBottom: '1.5rem', opacity: 0.8 }}>
                How do you survive this scenario?
            </p>

            <textarea
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                placeholder="I would use the..."
                style={{
                    width: '100%',
                    minHeight: '120px',
                    background: 'rgba(0,0,0,0.3)',
                    border: '1px solid var(--secondary)',
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
                disabled={loading || !strategy.trim()}
                style={{ width: '100%' }}
            >
                {loading ? 'TRANSMITTING...' : 'SUBMIT STRATEGY'}
            </button>
        </div>
    );
}
