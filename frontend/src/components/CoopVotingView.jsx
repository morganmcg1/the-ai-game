import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sword, Sparkles, AlertTriangle } from 'lucide-react';

// Helper to render character traits compactly
const CharacterTraits = ({ traits }) => {
    if (!traits) return null;
    const { weapon, talent, flaw } = traits;
    if (!weapon && !talent && !flaw) return null;

    return (
        <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.5rem',
            marginTop: '0.5rem',
            fontSize: '0.75rem'
        }}>
            {weapon && (
                <span style={{
                    background: 'rgba(255, 107, 107, 0.2)',
                    color: '#ff6b6b',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '3px'
                }}>
                    <Sword size={10} /> {weapon}
                </span>
            )}
            {talent && (
                <span style={{
                    background: 'rgba(72, 219, 251, 0.2)',
                    color: '#48dbfb',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '3px'
                }}>
                    <Sparkles size={10} /> {talent}
                </span>
            )}
            {flaw && (
                <span style={{
                    background: 'rgba(254, 202, 87, 0.2)',
                    color: '#feca57',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '3px'
                }}>
                    <AlertTriangle size={10} /> {flaw}
                </span>
            )}
        </div>
    );
};

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
                    COLLABORATIVE ROUND: TEAM VOTE
                </h1>

                {/* Clear instructions box */}
                <div style={{
                    background: 'rgba(0, 240, 255, 0.1)',
                    border: '1px solid rgba(0, 240, 255, 0.3)',
                    borderRadius: '8px',
                    padding: '1rem 1.5rem',
                    marginBottom: '1.5rem'
                }}>
                    <p style={{ textAlign: 'center', color: '#fff', fontFamily: 'monospace', marginBottom: '0.75rem', fontSize: '1.1rem' }}>
                        <strong>HOW THIS WORKS:</strong>
                    </p>
                    <ul style={{ color: '#ccc', fontFamily: 'monospace', margin: 0, paddingLeft: '1.5rem', lineHeight: '1.6' }}>
                        <li><strong style={{ color: 'var(--primary)' }}>Vote for the best strategy</strong> — The most-voted strategy will be judged</li>
                        <li><strong style={{ color: 'var(--success)' }}>If it succeeds:</strong> Everyone survives! Random player gets +200 bonus</li>
                        <li><strong style={{ color: 'var(--danger)' }}>If it fails:</strong> Everyone dies and loses -100 points</li>
                    </ul>
                </div>

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
                                <div style={{ fontWeight: 'bold', color: 'var(--accent)', marginBottom: '0.25rem' }}>
                                    {p.name}
                                    {isOwnStrategy && <span style={{ marginLeft: '0.5rem', color: '#888' }}>(YOUR STRATEGY)</span>}
                                    {isCurrentVote && <span style={{ marginLeft: '0.5rem', color: 'var(--success)' }}>(YOUR VOTE)</span>}
                                </div>
                                <CharacterTraits traits={p.character_traits} />
                                <div style={{ color: '#ccc', fontStyle: 'italic', marginTop: '0.5rem' }}>{p.strategy}</div>
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
                COLLABORATIVE ROUND: TEAM VOTE
            </h1>

            {/* Clear instructions box */}
            <div style={{
                background: 'rgba(0, 240, 255, 0.1)',
                border: '1px solid rgba(0, 240, 255, 0.3)',
                borderRadius: '8px',
                padding: '1rem 1.5rem',
                marginBottom: '2rem'
            }}>
                <p style={{ textAlign: 'center', color: '#fff', fontFamily: 'monospace', marginBottom: '0.75rem', fontSize: '1.1rem' }}>
                    <strong>HOW THIS WORKS:</strong>
                </p>
                <ul style={{ color: '#ccc', fontFamily: 'monospace', margin: 0, paddingLeft: '1.5rem', lineHeight: '1.6' }}>
                    <li><strong style={{ color: 'var(--primary)' }}>Vote for the best strategy</strong> — The most-voted strategy will be judged</li>
                    <li><strong style={{ color: 'var(--success)' }}>If it succeeds:</strong> Everyone survives! Random player gets +200 bonus</li>
                    <li><strong style={{ color: 'var(--danger)' }}>If it fails:</strong> Everyone dies and loses -100 points</li>
                    <li><strong style={{ color: '#ffd700' }}>Vote points:</strong> 1st: +200, 2nd: +100, Last: -100</li>
                </ul>
                <p style={{ textAlign: 'center', color: '#888', fontFamily: 'monospace', marginTop: '0.75rem', fontSize: '0.85rem' }}>
                    You cannot vote for your own strategy
                </p>
            </div>

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
                    const player = players[pid];

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
                                opacity: isOwnStrategy ? 0.6 : 1,
                                background: '#1a1a1a'
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
                            {/* Player info section below image */}
                            {player && (
                                <div style={{ padding: '0.75rem', borderTop: '1px solid #333' }}>
                                    <div style={{
                                        fontWeight: 'bold',
                                        color: 'var(--accent)',
                                        fontSize: '0.9rem',
                                        marginBottom: '0.25rem'
                                    }}>
                                        {player.name}
                                    </div>
                                    <CharacterTraits traits={player.character_traits} />
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
