import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export function CoopVotingView({ round, playerId, onVote, players }) {
    const existingVote = round.coop_votes?.[playerId] || null;
    const [selectedId, setSelectedId] = useState(existingVote);
    const [loading, setLoading] = useState(false);
    const [hasVoted, setHasVoted] = useState(!!existingVote);

    // Sync with server state if vote changes externally
    useEffect(() => {
        if (existingVote && !hasVoted) {
            setSelectedId(existingVote);
            setHasVoted(true);
        }
    }, [existingVote, hasVoted]);

    const handleVote = async () => {
        if (!selectedId || selectedId === playerId) return;
        setLoading(true);
        await onVote(selectedId);
        setHasVoted(true);
        setLoading(false);
    };

    const hasChangedVote = hasVoted && selectedId !== existingVote;
    const canSubmit = selectedId && selectedId !== playerId && (!hasVoted || hasChangedVote);

    // Check if images are still generating
    const entries = Object.entries(round.strategy_images || {});
    if (entries.length === 0) {
        return (
            <div className="card" style={{ textAlign: 'center' }}>
                <h2 className="glitch-text">RENDERING PROTOCOLS...</h2>
                <p style={{ color: 'var(--secondary)', marginBottom: '2rem', fontFamily: 'monospace' }}>
                    &gt; Generating visual representations of user protocols...
                </p>
                <span className="loader"></span>
            </div>
        );
    }

    return (
        <div style={{ width: '100%', maxWidth: '1000px' }}>
            <h1 style={{ textAlign: 'center', marginBottom: '1rem', color: 'var(--secondary)', fontFamily: 'monospace' }}>
                SYNC PROTOCOL SELECTION
            </h1>
            <p style={{ textAlign: 'center', marginBottom: '2rem', color: '#ccc', fontFamily: 'monospace' }}>
                &gt; Select the protocol most likely to preserve team integrity. Data points at stake.
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
                            {existingVote === pid && (
                                <div style={{
                                    position: 'absolute',
                                    top: 5,
                                    left: 5,
                                    background: 'var(--success)',
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    fontSize: '10px',
                                    color: 'black',
                                    fontWeight: 'bold'
                                }}>
                                    YOUR VOTE
                                </div>
                            )}
                        </motion.div>
                    );
                })}
            </div>

            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                {hasVoted && !hasChangedVote && (
                    <p style={{ color: 'var(--success)', marginBottom: '1rem', fontFamily: 'monospace' }}>
                        &gt; Selection registered. Select a different protocol to modify.
                    </p>
                )}
                <button
                    className="primary"
                    onClick={handleVote}
                    disabled={!canSubmit || loading}
                    style={{
                        backgroundColor: hasChangedVote ? 'var(--secondary)' : 'var(--accent)',
                        color: 'black',
                        padding: '16px 32px',
                        fontSize: '1.2rem'
                    }}
                >
                    {loading ? 'SYNCING...' : hasChangedVote ? 'UPDATE SELECTION' : 'CONFIRM SELECTION'}
                </button>
            </div>
        </div>
    );
}
