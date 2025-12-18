import React, { useState } from 'react';
import { motion } from 'framer-motion';

export function CoopVotingView({ round, playerId, onVote, players }) {
    const currentVote = round.coop_votes?.[playerId] || null;
    const [votingFor, setVotingFor] = useState(null); // Track which one is currently being submitted

    const handleVote = async (targetId) => {
        if (targetId === playerId || targetId === currentVote || votingFor) return;
        setVotingFor(targetId);
        await onVote(targetId);
        setVotingFor(null);
    };

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
                    &gt; Vote registered. Click another protocol to change your vote.
                </p>
            )}
        </div>
    );
}
