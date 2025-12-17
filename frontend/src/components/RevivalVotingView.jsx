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
    const isUnanimous = totalVotes === survivors.length &&
        new Set(Object.values(round.revival_votes || {})).size === 1;

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
                    &gt; DECEASED // AWAITING POTENTIAL REVIVAL
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
                &gt; REVIVAL PROTOCOL // UNANIMOUS VOTE REQUIRED
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
                    const voteCount = voteCounts[player.id] || 0;

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
                                    ? 'rgba(0, 255, 0, 0.2)'
                                    : 'rgba(0, 0, 0, 0.3)',
                                border: isSelected
                                    ? '2px solid #0f0'
                                    : '1px solid rgba(255, 255, 255, 0.2)',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                textAlign: 'left'
                            }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                                {player.character_image_url ? (
                                    <img
                                        src={player.character_image_url}
                                        alt={player.name}
                                        style={{
                                            width: '50px',
                                            height: '50px',
                                            borderRadius: '50%',
                                            objectFit: 'cover',
                                            border: isSelected ? '2px solid #0f0' : '2px solid #666',
                                            opacity: 0.8
                                        }}
                                    />
                                ) : (
                                    <div style={{
                                        width: '50px',
                                        height: '50px',
                                        borderRadius: '50%',
                                        background: 'rgba(100, 100, 100, 0.3)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center'
                                    }}>
                                        <User size={24} color="#666" />
                                    </div>
                                )}
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
                                        fontSize: '0.75rem',
                                        color: '#666',
                                        fontFamily: 'monospace'
                                    }}>
                                        <Skull size={12} style={{ marginRight: '0.25rem' }} />
                                        DECEASED
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

                            {/* Vote indicator */}
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                marginTop: '0.5rem'
                            }}>
                                <span style={{
                                    fontSize: '0.75rem',
                                    color: voteCount === survivors.length ? '#0f0' : 'rgba(255, 255, 255, 0.5)',
                                    fontFamily: 'monospace'
                                }}>
                                    {voteCount} / {survivors.length} votes
                                </span>
                                {isSelected && (
                                    <Check size={16} color="#0f0" />
                                )}
                            </div>
                        </motion.button>
                    );
                })}
            </div>

            {/* Status */}
            <div style={{
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                textAlign: 'center',
                marginBottom: '1rem'
            }}>
                {isUnanimous ? (
                    <span style={{ color: '#0f0' }}>
                        <Check size={16} style={{ marginRight: '0.5rem' }} />
                        UNANIMOUS! Ready to revive {players[Object.values(round.revival_votes)[0]]?.name}
                    </span>
                ) : totalVotes === survivors.length ? (
                    <span style={{ color: '#ff6b6b' }}>
                        <AlertTriangle size={16} style={{ marginRight: '0.5rem' }} />
                        Votes split - no unanimous agreement
                    </span>
                ) : (
                    <span style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                        Waiting for all survivors to vote ({totalVotes}/{survivors.length})
                    </span>
                )}
            </div>

            {/* Admin advance button */}
            {isAdmin && (
                <motion.button
                    onClick={handleAdvance}
                    disabled={loading}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    style={{
                        width: '100%',
                        backgroundColor: isUnanimous ? '#0f0' : 'rgba(255, 255, 255, 0.1)',
                        color: isUnanimous ? 'black' : 'white',
                        fontFamily: 'monospace',
                        padding: '0.75rem',
                        border: isUnanimous ? 'none' : '1px solid rgba(255, 255, 255, 0.3)',
                        borderRadius: '8px',
                        cursor: 'pointer'
                    }}
                >
                    {loading ? 'PROCESSING...' : isUnanimous
                        ? 'EXECUTE REVIVAL'
                        : 'SKIP REVIVAL (No Consensus)'
                    }
                </motion.button>
            )}

            {!isAdmin && (
                <p style={{
                    fontFamily: 'monospace',
                    fontSize: '0.8rem',
                    opacity: 0.5,
                    textAlign: 'center'
                }}>
                    Waiting for admin to proceed...
                </p>
            )}
        </div>
    );
}
