import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Heart, Skull, Check, User, Users, AlertTriangle } from 'lucide-react';

export function RevivalVotingView({ round, playerId, players, isAdmin, onVote, onAdvance }) {
    const [selectedId, setSelectedId] = useState(round.revival_votes?.[playerId] || null);
    const [loading, setLoading] = useState(false);

    const currentPlayer = players[playerId];
    const isSurvivor = currentPlayer?.is_alive;

    // Get dead players and survivors
    const deadPlayers = Object.values(players).filter(p => !p.is_alive);
    const survivors = Object.values(players).filter(p => p.is_alive);

    const handleVote = useCallback(async (targetId) => {
        if (!isSurvivor || loading) return;
        setSelectedId(targetId);
        setLoading(true);
        await onVote(targetId);
        setLoading(false);
    }, [isSurvivor, loading, onVote]);

    const handleAdvance = useCallback(async () => {
        if (loading) return;
        setLoading(true);
        await onAdvance();
        setLoading(false);
    }, [loading, onAdvance]);

    // Count votes for each dead player
    const voteCounts = {};
    Object.values(round.revival_votes || {}).forEach(target => {
        voteCounts[target] = (voteCounts[target] || 0) + 1;
    });

    const totalVotes = Object.keys(round.revival_votes || {}).length;

    // Dead player view
    if (!isSurvivor) {
        return (
            <div className="card" style={{ textAlign: 'center' }}>
                <div style={{
                    fontFamily: 'monospace',
                    color: '#666',
                    fontSize: '0.8rem',
                    marginBottom: '1rem',
                    padding: '0.5rem',
                    background: 'rgba(100, 100, 100, 0.1)',
                    border: '1px solid rgba(100, 100, 100, 0.3)',
                    borderRadius: '4px'
                }}>
                    DECEASED // AWAITING POTENTIAL REVIVAL
                </div>

                <h2 style={{
                    marginBottom: '1rem',
                    fontFamily: 'monospace',
                    color: '#666'
                }}>
                    <Skull size={24} style={{ marginRight: '0.5rem' }} />
                    YOU HAVE FALLEN
                </h2>

                <p style={{
                    fontFamily: 'monospace',
                    opacity: 0.7,
                    marginBottom: '1.5rem'
                }}>
                    The survivors may choose to revive <span style={{ color: '#0f0' }}>ONE</span> fallen player.
                    <br />
                    But they must vote <span style={{ color: '#ffd700' }}>UNANIMOUSLY</span>.
                </p>

                <div style={{
                    background: 'rgba(0, 255, 0, 0.1)',
                    border: '1px solid rgba(0, 255, 0, 0.3)',
                    borderRadius: '8px',
                    padding: '1rem',
                    marginBottom: '1rem'
                }}>
                    <p style={{
                        fontFamily: 'monospace',
                        fontSize: '0.9rem',
                        color: 'rgba(255, 255, 255, 0.8)'
                    }}>
                        <Users size={16} style={{ marginRight: '0.5rem' }} />
                        {survivors.length} survivor{survivors.length !== 1 ? 's' : ''} voting
                    </p>
                    <p style={{
                        fontFamily: 'monospace',
                        fontSize: '0.85rem',
                        color: 'rgba(255, 255, 255, 0.6)',
                        marginTop: '0.5rem'
                    }}>
                        Votes for you: {voteCounts[playerId] || 0} / {survivors.length}
                    </p>
                </div>

                <span className="loader"></span>
                <p style={{
                    fontFamily: 'monospace',
                    fontSize: '0.8rem',
                    opacity: 0.5,
                    marginTop: '1rem'
                }}>
                    Will your teammates save you?
                </p>
            </div>
        );
    }

    // Survivor view - can vote
    return (
        <div className="card">
            <div style={{
                fontFamily: 'monospace',
                color: '#0f0',
                fontSize: '0.8rem',
                marginBottom: '1rem',
                padding: '0.5rem',
                background: 'rgba(0, 255, 0, 0.1)',
                border: '1px solid rgba(0, 255, 0, 0.3)',
                borderRadius: '4px'
            }}>
                REVIVAL PROTOCOL // UNANIMOUS VOTE REQUIRED
            </div>

            <h2 style={{
                marginBottom: '1rem',
                color: '#0f0',
                fontFamily: 'monospace',
                textAlign: 'center'
            }}>
                <Heart size={20} style={{ marginRight: '0.5rem' }} />
                CHOOSE WHO TO REVIVE
                <Heart size={20} style={{ marginLeft: '0.5rem' }} />
            </h2>

            <div style={{
                background: 'rgba(255, 215, 0, 0.1)',
                border: '1px solid rgba(255, 215, 0, 0.3)',
                borderRadius: '8px',
                padding: '0.75rem',
                marginBottom: '1.5rem',
                textAlign: 'center'
            }}>
                <AlertTriangle size={16} style={{ marginRight: '0.5rem', color: '#ffd700' }} />
                <span style={{
                    fontFamily: 'monospace',
                    fontSize: '0.85rem',
                    color: '#ffd700'
                }}>
                    ALL {survivors.length} SURVIVORS MUST AGREE
                </span>
            </div>

            {/* Dead players to vote for */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '1rem',
                marginBottom: '1.5rem'
            }}>
                {deadPlayers.map((player) => {
                    const isSelected = selectedId === player.id;

                    return (
                        <motion.button
                            key={player.id}
                            onClick={() => handleVote(player.id)}
                            disabled={loading}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            style={{
                                position: 'relative',
                                padding: '1rem',
                                background: isSelected
                                    ? 'rgba(0, 255, 0, 0.15)'
                                    : 'rgba(255, 0, 0, 0.05)',
                                border: isSelected
                                    ? '2px solid #0f0'
                                    : '2px solid rgba(255, 68, 68, 0.5)',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                textAlign: 'left',
                                boxShadow: isSelected
                                    ? '0 0 15px rgba(0, 255, 0, 0.3)'
                                    : '0 0 10px rgba(255, 0, 0, 0.1)'
                            }}
                        >
                            {/* Deceased badge */}
                            <div style={{
                                position: 'absolute',
                                top: '-8px',
                                right: '10px',
                                background: '#ff4444',
                                padding: '2px 8px',
                                borderRadius: '4px',
                                fontSize: '10px',
                                color: 'white',
                                fontFamily: 'monospace',
                                fontWeight: 'bold',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                            }}>
                                <Skull size={10} />
                                DECEASED
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem', marginTop: '0.25rem' }}>
                                {/* Avatar with skull overlay */}
                                <div style={{ position: 'relative' }}>
                                    {player.character_image_url ? (
                                        <img
                                            src={player.character_image_url}
                                            alt={player.name}
                                            style={{
                                                width: '50px',
                                                height: '50px',
                                                borderRadius: '50%',
                                                objectFit: 'cover',
                                                border: isSelected ? '2px solid #0f0' : '2px solid #ff4444',
                                                filter: isSelected ? 'none' : 'grayscale(30%)'
                                            }}
                                        />
                                    ) : (
                                        <div style={{
                                            width: '50px',
                                            height: '50px',
                                            borderRadius: '50%',
                                            background: 'rgba(255, 68, 68, 0.2)',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            border: isSelected ? '2px solid #0f0' : '2px solid #ff4444'
                                        }}>
                                            <Skull size={24} color="#ff4444" />
                                        </div>
                                    )}
                                    {/* Small skull indicator on avatar */}
                                    {!isSelected && player.character_image_url && (
                                        <div style={{
                                            position: 'absolute',
                                            bottom: '-2px',
                                            right: '-2px',
                                            background: '#ff4444',
                                            borderRadius: '50%',
                                            padding: '3px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            <Skull size={10} color="white" />
                                        </div>
                                    )}
                                </div>
                                <div>
                                    <span style={{
                                        fontFamily: 'monospace',
                                        color: isSelected ? '#0f0' : 'white',
                                        fontWeight: isSelected ? 'bold' : 'normal',
                                        display: 'block'
                                    }}>
                                        {player.name}
                                    </span>
                                    <span style={{
                                        fontSize: '0.7rem',
                                        color: isSelected ? 'rgba(0, 255, 0, 0.7)' : '#ff6b6b',
                                        fontFamily: 'monospace'
                                    }}>
                                        {isSelected ? '✓ Selected for revival' : 'Click to vote'}
                                    </span>
                                </div>
                            </div>

                            {/* Their death reason */}
                            {player.death_reason && (
                                <p style={{
                                    fontFamily: 'monospace',
                                    fontSize: '0.75rem',
                                    color: 'rgba(255, 255, 255, 0.5)',
                                    marginBottom: '0.5rem',
                                    fontStyle: 'italic'
                                }}>
                                    "{player.death_reason}"
                                </p>
                            )}

                            {/* Their strategy preview */}
                            {player.strategy && (
                                <p style={{
                                    fontFamily: 'monospace',
                                    fontSize: '0.7rem',
                                    color: 'rgba(255, 255, 255, 0.4)',
                                    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                                    paddingTop: '0.5rem',
                                    marginTop: '0.5rem'
                                }}>
                                    Strategy: {player.strategy.substring(0, 80)}{player.strategy.length > 80 ? '...' : ''}
                                </p>
                            )}

                            {/* Selection indicator - no vote counts shown to keep voting secret */}
                            {isSelected && (
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'flex-end',
                                    alignItems: 'center',
                                    marginTop: '0.5rem'
                                }}>
                                    <Check size={16} color="#0f0" />
                                </div>
                            )}
                        </motion.button>
                    );
                })}
            </div>

            {/* Status - don't reveal vote results to keep it secret */}
            <div style={{
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                textAlign: 'center',
                marginBottom: '1rem'
            }}>
                {totalVotes === survivors.length ? (
                    <span style={{ color: '#ffd700' }}>
                        <Check size={16} style={{ marginRight: '0.5rem' }} />
                        All votes cast - processing result...
                    </span>
                ) : selectedId ? (
                    <span style={{ color: 'rgba(0, 255, 0, 0.7)' }}>
                        <Check size={16} style={{ marginRight: '0.5rem' }} />
                        Vote recorded ({totalVotes}/{survivors.length} votes cast)
                    </span>
                ) : (
                    <span style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                        Select a fallen player to revive ({totalVotes}/{survivors.length} votes cast)
                    </span>
                )}
            </div>

            {/* Admin advance button - only shown as fallback, game auto-advances when all vote */}
            {isAdmin && totalVotes < survivors.length && (
                <motion.button
                    onClick={handleAdvance}
                    disabled={loading}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    style={{
                        width: '100%',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        color: 'white',
                        fontFamily: 'monospace',
                        padding: '0.75rem',
                        border: '1px solid rgba(255, 255, 255, 0.3)',
                        borderRadius: '8px',
                        cursor: 'pointer'
                    }}
                >
                    {loading ? 'PROCESSING...' : 'SKIP REVIVAL (Force Proceed)'}
                </motion.button>
            )}

            {!isAdmin && !selectedId && (
                <p style={{
                    fontFamily: 'monospace',
                    fontSize: '0.8rem',
                    opacity: 0.5,
                    textAlign: 'center'
                }}>
                    Cast your vote above
                </p>
            )}
        </div>
    );
}
