import React, { useState } from 'react';
import { motion } from 'framer-motion';

export function CoopVotingView({ round, playerId, onVote, players }) {
    const [selectedId, setSelectedId] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleVote = async () => {
        if (!selectedId || selectedId === playerId) return;
        setLoading(true);
        await onVote(selectedId);
        setLoading(false);
    };

    // Check if already voted
    if (round.coop_votes && round.coop_votes[playerId]) {
        return (
            <div className="card" style={{ textAlign: 'center' }}>
                <h2>VOTE CAST</h2>
                <p>Waiting for others to vote...</p>
                <span className="loader"></span>
            </div>
        );
    }

    // Check if images are still generating
    const entries = Object.entries(round.strategy_images || {});
    if (entries.length === 0) {
        return (
            <div className="card" style={{ textAlign: 'center' }}>
                <h2 className="glitch-text">VISUALIZING STRATEGIES...</h2>
                <p style={{ color: 'var(--secondary)', marginBottom: '2rem' }}>
                    The AI is creating images for each strategy.
                </p>
                <span className="loader"></span>
            </div>
        );
    }

    return (
        <div style={{ width: '100%', maxWidth: '1000px' }}>
            <h1 style={{ textAlign: 'center', marginBottom: '1rem', color: 'var(--secondary)' }}>
                COOPERATIVE VOTE
            </h1>
            <p style={{ textAlign: 'center', marginBottom: '2rem', color: '#ccc' }}>
                Which strategy looks most likely to succeed? Points are at stake!
            </p>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '2rem'
            }}>
                {entries.map(([pid, url]) => {
                    const isOwnStrategy = pid === playerId;
                    return (
                        <motion.div
                            key={pid}
                            whileHover={!isOwnStrategy ? { scale: 1.05 } : {}}
                            onClick={() => !isOwnStrategy && setSelectedId(pid)}
                            style={{
                                cursor: isOwnStrategy ? 'not-allowed' : 'pointer',
                                border: selectedId === pid ? '4px solid var(--accent)' : '1px solid transparent',
                                borderRadius: '12px',
                                overflow: 'hidden',
                                position: 'relative',
                                opacity: isOwnStrategy ? 0.6 : 1
                            }}
                        >
                            <img src={url} alt="Strategy" style={{ width: '100%', display: 'block' }} />
                            {isOwnStrategy && (
                                <div style={{
                                    position: 'absolute',
                                    top: 5,
                                    right: 5,
                                    background: 'rgba(0,0,0,0.7)',
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    fontSize: '10px',
                                    color: 'var(--accent)'
                                }}>
                                    YOUR STRATEGY
                                </div>
                            )}
                        </motion.div>
                    );
                })}
            </div>

            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                <button
                    className="primary"
                    onClick={handleVote}
                    disabled={!selectedId || selectedId === playerId || loading}
                    style={{
                        backgroundColor: 'var(--accent)',
                        color: 'black',
                        padding: '16px 32px',
                        fontSize: '1.2rem'
                    }}
                >
                    {loading ? 'VOTING...' : 'CONFIRM VOTE'}
                </button>
            </div>
        </div>
    );
}
