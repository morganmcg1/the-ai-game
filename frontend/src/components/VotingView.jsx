import React, { useState } from 'react';
import { motion } from 'framer-motion';

export function VotingView({ round, playerId, onVote }) {
    const [selectedId, setSelectedId] = useState(null);
    const [loading, setLoading] = useState(false);

    // Filter out self if you want, or allow voting for self? 
    // Let's allow voting for anyone for chaos.
    // Actually, usually you can't vote for self.
    // We don't have easy way to know which image matches which player unless we show names.
    // User request: "people see their teamates' strategies visualised as a single image without seeing the text"
    // So we show Images without Text/Names if possible?
    // But we need to know who is who to not vote for self? 
    // For MVP, show Images and maybe small ID. Blind voting usually means anon.

    const handleVote = async () => {
        if (!selectedId) return;
        setLoading(true);
        await onVote(selectedId);
        setLoading(false);
    };

    // Check if I already voted
    if (round.votes && round.votes[playerId]) {
        return (
            <div className="card" style={{ textAlign: 'center' }}>
                <h2>VOTE CAST</h2>
                <p>Waiting for the consensus...</p>
                <span className="loader"></span>
            </div>
        );
    }

    const entries = Object.entries(round.trap_images || {});

    return (
        <div style={{ width: '100%', maxWidth: '1000px' }}>
            <h1 style={{ textAlign: 'center', marginBottom: '2rem' }}>CHOOSE YOUR DOOM</h1>
            <p style={{ textAlign: 'center', marginBottom: '2rem' }}>Vote for the most interesting trap.</p>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '2rem'
            }}>
                {entries.map(([pid, url]) => (
                    <motion.div
                        key={pid}
                        whileHover={{ scale: 1.05 }}
                        onClick={() => setSelectedId(pid)}
                        style={{
                            cursor: 'pointer',
                            border: selectedId === pid ? '4px solid var(--accent)' : '1px solid transparent',
                            borderRadius: '12px',
                            overflow: 'hidden',
                            position: 'relative'
                        }}
                    >
                        <img src={url} alt="Trap" style={{ width: '100%', display: 'block' }} />
                        {pid === playerId && (
                            <div style={{ position: 'absolute', top: 5, right: 5, background: 'rgba(0,0,0,0.5)', padding: '4px', borderRadius: '4px', fontSize: '10px' }}>
                                YOU
                            </div>
                        )}
                    </motion.div>
                ))}
            </div>

            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                <button
                    className="primary"
                    onClick={handleVote}
                    disabled={!selectedId || loading}
                    style={{ backgroundColor: 'var(--accent)', color: 'black', padding: '16px 32px', fontSize: '1.2rem' }}
                >
                    {loading ? 'VOTING...' : 'CONFIRM VOTE'}
                </button>
            </div>
        </div>
    );
}
