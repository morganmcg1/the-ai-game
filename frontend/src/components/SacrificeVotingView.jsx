import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Skull, Check, User } from 'lucide-react';

export function SacrificeVotingView({ round, playerId, players, onVote }) {
    const [selectedId, setSelectedId] = useState(round.sacrifice_votes?.[playerId] || null);
    const [loading, setLoading] = useState(false);

    // Determine eligible candidates
    // If there are volunteers, only they are eligible
    // If no volunteers, everyone (except self) is eligible
    const volunteers = Object.entries(round.sacrifice_volunteers || {})
        .filter(([, volunteered]) => volunteered)
        .map(([pid]) => pid);

    const hasVolunteers = volunteers.length > 0;
    const eligiblePlayers = hasVolunteers
        ? Object.values(players).filter(p => volunteers.includes(p.id))
        : Object.values(players).filter(p => p.id !== playerId && p.is_alive);

    const handleVote = useCallback(async (targetId) => {
        if (targetId === playerId) return; // Can't vote for self
        if (loading) return;

        setSelectedId(targetId);
        setLoading(true);
        await onVote(targetId);
        setLoading(false);
    }, [playerId, loading, onVote]);

    // Count votes for display
    const voteCounts = {};
    Object.values(round.sacrifice_votes || {}).forEach(target => {
        voteCounts[target] = (voteCounts[target] || 0) + 1;
    });

    const totalVotes = Object.values(round.sacrifice_votes || {}).length;
    const totalPlayers = Object.values(players).filter(p => p.is_alive).length;

    return (
        <div className="card">
            {/* Header */}
            <div style={{
                fontFamily: 'monospace',
                color: '#ff4444',
                fontSize: '0.8rem',
                marginBottom: '1rem',
                padding: '0.5rem',
                background: 'rgba(255, 0, 0, 0.1)',
                border: '1px solid rgba(255, 0, 0, 0.3)',
                borderRadius: '4px'
            }}>
                &gt; SACRIFICE SELECTION // CHOOSE THE MARTYR
            </div>

            <h2 style={{
                marginBottom: '1rem',
                color: '#ff6b6b',
                fontFamily: 'monospace',
                textAlign: 'center'
            }}>
                <Skull size={20} style={{ marginRight: '0.5rem' }} />
                SELECT THE TRIBUTE
                <Skull size={20} style={{ marginLeft: '0.5rem' }} />
            </h2>

            <p style={{
                marginBottom: '1.5rem',
                opacity: 0.8,
                fontFamily: 'monospace',
                textAlign: 'center',
                fontSize: '0.9rem'
            }}>
                {hasVolunteers
                    ? 'Vote for which volunteer will make the ultimate sacrifice.'
                    : 'No volunteers! Vote to draft an involuntary tribute.'}
            </p>

            {/* Voting grid */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '1rem',
                marginBottom: '1.5rem'
            }}>
                {eligiblePlayers.map((player) => {
                    const isSelected = selectedId === player.id;
                    const isVolunteer = volunteers.includes(player.id);
                    const voteCount = voteCounts[player.id] || 0;

                    return (
                        <motion.button
                            key={player.id}
                            onClick={() => handleVote(player.id)}
                            disabled={loading}
                            whileHover={{ scale: 1.03 }}
                            whileTap={{ scale: 0.97 }}
                            style={{
                                position: 'relative',
                                padding: '1.25rem',
                                background: isSelected
                                    ? 'rgba(255, 68, 68, 0.3)'
                                    : 'rgba(0, 0, 0, 0.3)',
                                border: isSelected
                                    ? '2px solid #ff4444'
                                    : '1px solid rgba(255, 255, 255, 0.2)',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                textAlign: 'center',
                                transition: 'all 0.2s ease'
                            }}
                        >
                            {/* Player avatar or icon */}
                            {player.character_image_url ? (
                                <img
                                    src={player.character_image_url}
                                    alt={player.name}
                                    style={{
                                        width: '60px',
                                        height: '60px',
                                        borderRadius: '50%',
                                        objectFit: 'cover',
                                        margin: '0 auto 0.5rem',
                                        display: 'block',
                                        border: isSelected ? '2px solid #ff4444' : '2px solid transparent'
                                    }}
                                />
                            ) : (
                                <div style={{
                                    width: '60px',
                                    height: '60px',
                                    borderRadius: '50%',
                                    background: 'rgba(255, 255, 255, 0.1)',
                                    margin: '0 auto 0.5rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}>
                                    <User size={28} color="white" />
                                </div>
                            )}

                            <span style={{
                                fontFamily: 'monospace',
                                color: isSelected ? '#ff4444' : 'white',
                                fontWeight: isSelected ? 'bold' : 'normal',
                                display: 'block',
                                marginBottom: '0.25rem'
                            }}>
                                {player.name}
                            </span>

                            {/* Volunteer badge */}
                            {isVolunteer && (
                                <span style={{
                                    fontSize: '0.7rem',
                                    color: '#ffd700',
                                    fontFamily: 'monospace',
                                    display: 'block',
                                    marginBottom: '0.25rem'
                                }}>
                                    VOLUNTEER
                                </span>
                            )}

                            {/* Vote count */}
                            {voteCount > 0 && (
                                <span style={{
                                    fontSize: '0.75rem',
                                    color: 'rgba(255, 255, 255, 0.6)',
                                    fontFamily: 'monospace'
                                }}>
                                    {voteCount} vote{voteCount !== 1 ? 's' : ''}
                                </span>
                            )}

                            {/* Selected checkmark */}
                            {isSelected && (
                                <div style={{
                                    position: 'absolute',
                                    top: '0.5rem',
                                    right: '0.5rem',
                                    background: '#ff4444',
                                    borderRadius: '50%',
                                    padding: '0.25rem'
                                }}>
                                    <Check size={14} color="white" />
                                </div>
                            )}
                        </motion.button>
                    );
                })}
            </div>

            {/* Status */}
            <div style={{
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                color: 'rgba(255, 255, 255, 0.6)',
                textAlign: 'center'
            }}>
                {selectedId ? (
                    <span style={{ color: '#ff6b6b' }}>
                        <Check size={14} style={{ marginRight: '0.25rem' }} />
                        Your vote: {players[selectedId]?.name}
                    </span>
                ) : (
                    'Select a tribute to cast your vote'
                )}
                <br />
                <span style={{ marginTop: '0.5rem', display: 'inline-block' }}>
                    {totalVotes} / {totalPlayers} votes cast
                </span>
            </div>
        </div>
    );
}
