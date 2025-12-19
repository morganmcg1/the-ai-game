import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export function CoopVotingView({ round, playerId, onVote, players }) {
    const currentVote = round.coop_votes?.[playerId] || null;
    const [votingFor, setVotingFor] = useState(null);
    const [showFallback, setShowFallback] = useState(false);

    // Check if images are still generating
    const entries = Object.entries(round.strategy_images || {});

    // Set fallback timer when no images exist
    useEffect(() => {
        if (entries.length === 0) {
            const timer = setTimeout(() => setShowFallback(true), 30000);
            return () => clearTimeout(timer);
        } else {
            setShowFallback(false);
        }
    }, [entries.length]);

    const handleVote = async (targetId) => {
        if (targetId === playerId || targetId === currentVote || votingFor) return;
        setVotingFor(targetId);
        await onVote(targetId);
        setVotingFor(null);
    };

    // Get alive players with strategies for fallback
    const playersWithStrategies = Object.values(players).filter(
        p => p.is_alive && p.strategy
    );

    // If no images and fallback triggered, show text-based voting
    if (entries.length === 0 && showFallback) {
        return (
            <div style={{ width: '100%', maxWidth: '1000px' }}>
                <h1 style={{ textAlign: 'center', marginBottom: '1rem', color: 'var(--secondary)', fontFamily: 'monospace' }}>
                    SYNC PROTOCOL SELECTION
                </h1>
                <p style={{ textAlign: 'center', marginBottom: '1rem', color: '#ff6b6b', fontFamily: 'monospace' }}>
                    Visual rendering failed. Vote based on strategy text.
                </p>
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {playersWithStrategies.map(p => {
                        const isOwnStrategy = p.id === playerId;
                        const isCurrentVote = currentVote === p.id;
                        const isVoting = votingFor === p.id;
                        const canClick = !isOwnStrategy && !isVoting && !isCurrentVote;

                        return (
                            <motion.div
                                key={p.id}
                                whileHover={canClick ? { scale: 1.02 } : {}}
                                onClick={() => canClick && handleVote(p.id)}
                                style={{
                                    cursor: isOwnStrategy ? 'not-allowed' : (canClick ? 'pointer' : 'default'),
                                    border: isCurrentVote ? '3px solid var(--success)' : '2px solid #333',
                                    borderRadius: '12px',
                                    padding: '1rem',
                                    opacity: isOwnStrategy ? 0.6 : 1,
                                    background: isCurrentVote ? 'rgba(0, 255, 0, 0.1)' : 'rgba(0,0,0,0.3)',
                                    position: 'relative'
                                }}
                            >
                                <div style={{ fontWeight: 'bold', color: 'var(--accent)', marginBottom: '0.5rem' }}>
                                    {p.name}
                                    {isOwnStrategy && <span style={{ marginLeft: '0.5rem', color: '#888' }}>(YOUR STRATEGY)</span>}
                                    {isCurrentVote && <span style={{ marginLeft: '0.5rem', color: 'var(--success)' }}>(YOUR VOTE)</span>}
                                </div>
                                <div style={{ color: '#ccc', fontStyle: 'italic' }}>{p.strategy}</div>
                                {isVoting && (
                                    <div style={{
                                        position: 'absolute',
                                        inset: 0,
                                        background: 'rgba(0,0,0,0.5)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        borderRadius: '12px'
                                    }}>
                                        <span className="spinner" style={{ width: '32px', height: '32px' }}></span>
                                    </div>
                                )}
                            </motion.div>
                        );
                    })}
                </div>
                {currentVote && (
                    <p style={{ textAlign: 'center', marginTop: '1.5rem', color: 'var(--success)', fontFamily: 'monospace' }}>
                        Vote registered. Click another strategy to change your vote.
                    </p>
                )}
            </div>
        );
    }

    // If no images and no fallback yet, show loading
    if (entries.length === 0) {
        return (
            <div className="card" style={{ textAlign: 'center' }}>
                <h2 className="glitch-text">RENDERING PROTOCOLS...</h2>
                <p style={{ color: 'var(--secondary)', marginBottom: '2rem', fontFamily: 'monospace' }}>
                    Generating visual representations of user strategies...
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
                Vote for the strategy image most likely to save the entire team of players. Everyone's survival depends on it.
            </p>

            {/* 2-column grid with centered last card for odd counts */}
            {(() => {
                const count = entries.length;
                const isOdd = count % 2 === 1;
                const pairedEntries = isOdd ? entries.slice(0, -1) : entries;
                const lastEntry = isOdd ? entries[entries.length - 1] : null;

                const renderCard = ([pid, url], index) => {
                    const isOwnStrategy = pid === playerId;
                    const isCurrentVote = currentVote === pid;
                    const isVoting = votingFor === pid;
                    const canClick = !isOwnStrategy && !isVoting && !isCurrentVote;

                    return (
                        <motion.div
                            key={pid}
                            whileHover={canClick ? { scale: 1.03 } : {}}
                            onClick={() => canClick && handleVote(pid)}
                            style={{
                                cursor: isOwnStrategy ? 'not-allowed' : (canClick ? 'pointer' : 'default'),
                                border: isCurrentVote ? '4px solid var(--success)' : '2px solid #333',
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
                                    top: 8,
                                    right: 8,
                                    background: 'rgba(0,0,0,0.8)',
                                    padding: '6px 10px',
                                    borderRadius: '6px',
                                    fontSize: '11px',
                                    color: 'var(--accent)',
                                    fontWeight: 'bold'
                                }}>
                                    YOUR STRATEGY
                                </div>
                            )}
                            {isCurrentVote && (
                                <div style={{
                                    position: 'absolute',
                                    top: 8,
                                    left: 8,
                                    background: 'var(--success)',
                                    padding: '6px 10px',
                                    borderRadius: '6px',
                                    fontSize: '11px',
                                    color: 'black',
                                    fontWeight: 'bold'
                                }}>
                                    YOUR VOTE
                                </div>
                            )}
                            {isVoting && (
                                <div style={{
                                    position: 'absolute',
                                    inset: 0,
                                    background: 'rgba(0,0,0,0.5)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}>
                                    <span className="spinner" style={{ width: '32px', height: '32px' }}></span>
                                </div>
                            )}
                        </motion.div>
                    );
                };

                return (
                    <>
                        {/* 2-column grid for paired entries */}
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(2, 1fr)',
                            gap: '1.5rem'
                        }}>
                            {pairedEntries.map((entry, index) => renderCard(entry, index))}
                        </div>

                        {/* Centered last card for odd counts */}
                        {lastEntry && (
                            <div style={{
                                display: 'flex',
                                justifyContent: 'center',
                                marginTop: '1.5rem'
                            }}>
                                <div style={{ width: 'calc(50% - 0.75rem)' }}>
                                    {renderCard(lastEntry, entries.length - 1)}
                                </div>
                            </div>
                        )}
                    </>
                );
            })()}

            {currentVote && (
                <p style={{ textAlign: 'center', marginTop: '1.5rem', color: 'var(--success)', fontFamily: 'monospace' }}>
                    Vote registered. Click another strategy to change your vote.
                </p>
            )}
        </div>
    );
}
