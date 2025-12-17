import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, Skull, Users } from 'lucide-react';

export function SacrificeVolunteerView({ round, playerId, players, isAdmin, onVolunteer, onAdvance }) {
    const [loading, setLoading] = useState(false);
    const [hasVolunteered, setHasVolunteered] = useState(
        round.sacrifice_volunteers && round.sacrifice_volunteers[playerId]
    );

    const handleVolunteer = useCallback(async () => {
        if (hasVolunteered || loading) return;
        setLoading(true);
        await onVolunteer();
        setHasVolunteered(true);
        setLoading(false);
    }, [hasVolunteered, loading, onVolunteer]);

    const handleAdvance = useCallback(async () => {
        setLoading(true);
        await onAdvance();
        setLoading(false);
    }, [onAdvance]);

    // Get list of volunteers
    const volunteers = Object.entries(round.sacrifice_volunteers || {})
        .filter(([, volunteered]) => volunteered)
        .map(([pid]) => players[pid])
        .filter(Boolean);

    const volunteerCount = volunteers.length;

    return (
        <div className="card">
            {/* Header with dramatic flair */}
            <div style={{
                fontFamily: 'monospace',
                color: '#ff4444',
                fontSize: '0.8rem',
                marginBottom: '1rem',
                padding: '0.5rem',
                background: 'rgba(255, 0, 0, 0.1)',
                border: '1px solid rgba(255, 0, 0, 0.3)',
                borderRadius: '4px',
                animation: 'flicker 2s infinite'
            }}>
                &gt; CRITICAL FAILURE // SACRIFICE PROTOCOL INITIATED
            </div>

            <h2 style={{
                marginBottom: '1rem',
                color: '#ff6b6b',
                fontFamily: 'monospace',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem'
            }}>
                <Skull size={24} />
                SACRIFICE REQUIRED
                <Skull size={24} />
            </h2>

            <p style={{
                marginBottom: '2rem',
                opacity: 0.8,
                fontFamily: 'monospace',
                textAlign: 'center',
                lineHeight: 1.6
            }}>
                The simulation demands a sacrifice. One player must fall so others may survive.
                <br />
                <span style={{ color: '#ffd700' }}>Who will volunteer as tribute?</span>
            </p>

            {/* Volunteer button */}
            {!hasVolunteered ? (
                <motion.button
                    className="primary"
                    onClick={handleVolunteer}
                    disabled={loading}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    style={{
                        width: '100%',
                        backgroundColor: '#ff4444',
                        color: 'white',
                        fontFamily: 'monospace',
                        fontSize: '1.1rem',
                        padding: '1rem 2rem',
                        border: '2px solid #ff6b6b',
                        boxShadow: '0 0 20px rgba(255, 68, 68, 0.4)',
                        marginBottom: '1.5rem'
                    }}
                >
                    {loading ? (
                        'PROCESSING...'
                    ) : (
                        <>
                            <Heart size={18} style={{ marginRight: '0.5rem' }} />
                            I VOLUNTEER AS TRIBUTE
                            <Heart size={18} style={{ marginLeft: '0.5rem' }} />
                        </>
                    )}
                </motion.button>
            ) : (
                <div style={{
                    width: '100%',
                    backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    color: '#ffd700',
                    fontFamily: 'monospace',
                    fontSize: '1rem',
                    padding: '1rem',
                    border: '2px solid #ffd700',
                    borderRadius: '8px',
                    textAlign: 'center',
                    marginBottom: '1.5rem'
                }}>
                    <Heart size={18} style={{ marginRight: '0.5rem' }} />
                    YOU HAVE VOLUNTEERED
                    <Heart size={18} style={{ marginLeft: '0.5rem' }} />
                </div>
            )}

            {/* List of volunteers */}
            <div style={{
                borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                paddingTop: '1rem',
                marginTop: '1rem'
            }}>
                <div style={{
                    fontFamily: 'monospace',
                    color: 'var(--accent)',
                    marginBottom: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                }}>
                    <Users size={16} />
                    VOLUNTEERS: {volunteerCount}
                </div>

                <AnimatePresence>
                    {volunteers.length > 0 ? (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                            {volunteers.map((player) => (
                                <motion.span
                                    key={player.id}
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    style={{
                                        background: player.id === playerId
                                            ? 'rgba(255, 215, 0, 0.2)'
                                            : 'rgba(255, 68, 68, 0.2)',
                                        padding: '0.4rem 0.8rem',
                                        borderRadius: '4px',
                                        fontFamily: 'monospace',
                                        fontSize: '0.9rem',
                                        color: player.id === playerId ? '#ffd700' : '#ff6b6b',
                                        border: `1px solid ${player.id === playerId ? '#ffd700' : '#ff6b6b'}`
                                    }}
                                >
                                    {player.name}
                                    {player.id === playerId && ' (YOU)'}
                                </motion.span>
                            ))}
                        </div>
                    ) : (
                        <p style={{
                            fontFamily: 'monospace',
                            opacity: 0.5,
                            fontStyle: 'italic',
                            fontSize: '0.9rem'
                        }}>
                            No volunteers yet... Will anyone be brave enough?
                        </p>
                    )}
                </AnimatePresence>
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
                        marginTop: '1.5rem',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        color: 'white',
                        fontFamily: 'monospace',
                        padding: '0.75rem',
                        border: '1px solid rgba(255, 255, 255, 0.3)',
                        borderRadius: '8px',
                        cursor: 'pointer'
                    }}
                >
                    {loading ? 'ADVANCING...' : volunteerCount > 0
                        ? 'PROCEED TO VOTING'
                        : 'DRAFT INVOLUNTARY TRIBUTES'
                    }
                </motion.button>
            )}

            {!isAdmin && (
                <p style={{
                    fontFamily: 'monospace',
                    fontSize: '0.8rem',
                    opacity: 0.5,
                    textAlign: 'center',
                    marginTop: '1rem'
                }}>
                    Waiting for admin to proceed...
                </p>
            )}
        </div>
    );
}
