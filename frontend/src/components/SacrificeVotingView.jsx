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

    // Count only players who CAN vote (exclude players who are the only eligible candidate)
    const alivePlayers = Object.values(players).filter(p => p.is_alive);
    const playersWhoCanVote = alivePlayers.filter(p => {
        if (hasVolunteers) {
            // Player can vote if there's at least one volunteer that isn't themselves
            return volunteers.some(vid => vid !== p.id);
        } else {
            // If no volunteers, player can vote if there's anyone else alive
            return alivePlayers.length > 1;
        }
    });
    const totalExpectedVotes = playersWhoCanVote.length;

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
                    const isSelf = player.id === playerId;

                    return (
                        <motion.button
                            key={player.id}
                            onClick={() => !isSelf && handleVote(player.id)}
                            disabled={loading || isSelf}
                            whileHover={isSelf ? {} : { scale: 1.03 }}
                            whileTap={isSelf ? {} : { scale: 0.97 }}
                            title={isSelf ? "You cannot vote for yourself" : `Vote for ${player.name}`}
                            style={{
                                position: 'relative',
                                padding: '1.25rem',
                                background: isSelected
                                    ? 'rgba(255, 68, 68, 0.3)'
                                    : 'rgba(0, 0, 0, 0.3)',
                                border: isSelected
                                    ? '2px solid #ff4444'
                                    : isSelf
                                        ? '1px dashed rgba(255, 255, 255, 0.15)'
                                        : '1px solid rgba(255, 255, 255, 0.2)',
                                borderRadius: '8px',
                                cursor: isSelf ? 'not-allowed' : 'pointer',
                                textAlign: 'center',
                                transition: 'all 0.2s ease',
                                opacity: isSelf ? 0.4 : 1,
                                filter: isSelf ? 'grayscale(50%)' : 'none'
                            }}
                        >
                            {/* "YOU" badge for own card */}
                            {isSelf && (
                                <div style={{
                                    position: 'absolute',
                                    top: '0.5rem',
                                    left: '0.5rem',
                                    background: 'rgba(100, 100, 100, 0.9)',
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    fontSize: '10px',
                                    color: '#999',
                                    fontFamily: 'monospace',
                                    fontWeight: 'bold'
                                }}>
                                    YOU
                                </div>
                            )}

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
                                        border: isSelected ? '2px solid #ff4444' : isSelf ? '2px solid #666' : '2px solid transparent',
                                        filter: isSelf ? 'grayscale(100%)' : 'none'
                                    }}
                                />
                            ) : (
                                <div style={{
                                    width: '60px',
                                    height: '60px',
                                    borderRadius: '50%',
                                    background: isSelf ? 'rgba(100, 100, 100, 0.3)' : 'rgba(255, 255, 255, 0.1)',
                                    margin: '0 auto 0.5rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}>
                                    <User size={28} color={isSelf ? '#666' : 'white'} />
                                </div>
                            )}

                            <span style={{
                                fontFamily: 'monospace',
                                color: isSelf ? '#666' : isSelected ? '#ff4444' : 'white',
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
                    {totalVotes} / {totalExpectedVotes} votes cast
                </span>
            </div>
        </div>
    );
}
