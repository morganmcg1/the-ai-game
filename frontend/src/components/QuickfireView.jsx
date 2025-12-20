import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Zap, Clock, CheckCircle } from 'lucide-react';

export function QuickfireView({ round, playerId, onSubmitChoice, players, timeRemaining }) {
    const [selectedChoice, setSelectedChoice] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const currentChoice = round.quickfire_player_choices?.[playerId] || null;
    const choices = round.quickfire_choices || [];
    const hasSubmitted = currentChoice !== null;

    const handleChoice = async (choiceId) => {
        if (hasSubmitted || submitting) return;

        setSelectedChoice(choiceId);
        setSubmitting(true);
        try {
            await onSubmitChoice(choiceId);
        } catch (e) {
            console.error('Failed to submit choice:', e);
            setSelectedChoice(null);
        }
        setSubmitting(false);
    };

    // Count how many players have chosen
    const alivePlayers = Object.values(players).filter(p => p.is_alive && p.in_lobby);
    const choiceCount = Object.keys(round.quickfire_player_choices || {}).length;

    return (
        <div className="card" style={{ maxWidth: '600px', width: '100%' }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem',
                marginBottom: '1.5rem'
            }}>
                <Zap size={28} color="var(--warning)" />
                <h1 style={{
                    color: 'var(--warning)',
                    fontFamily: 'monospace',
                    fontSize: '1.5rem',
                    margin: 0
                }}>
                    QUICK FIRE
                </h1>
                <Zap size={28} color="var(--warning)" />
            </div>

            {/* Timer */}
            {timeRemaining !== undefined && timeRemaining > 0 && (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem',
                    marginBottom: '1rem',
                    color: timeRemaining < 15 ? 'var(--danger)' : '#888'
                }}>
                    <Clock size={16} />
                    <span style={{ fontFamily: 'monospace' }}>{timeRemaining}s</span>
                </div>
            )}

            {/* Scenario */}
            <div style={{
                background: 'rgba(255, 200, 0, 0.1)',
                border: '1px solid rgba(255, 200, 0, 0.3)',
                borderRadius: '8px',
                padding: '1rem',
                marginBottom: '1.5rem',
                textAlign: 'center'
            }}>
                <p style={{
                    color: '#fff',
                    fontSize: '1.1rem',
                    lineHeight: '1.5',
                    margin: 0
                }}>
                    {round.scenario_text}
                </p>
            </div>

            {/* Choices */}
            {hasSubmitted ? (
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    style={{
                        textAlign: 'center',
                        padding: '2rem',
                        background: 'rgba(0, 255, 0, 0.1)',
                        borderRadius: '8px',
                        border: '1px solid rgba(0, 255, 0, 0.3)'
                    }}
                >
                    <CheckCircle size={48} color="var(--success)" style={{ marginBottom: '1rem' }} />
                    <p style={{
                        color: 'var(--success)',
                        fontFamily: 'monospace',
                        fontSize: '1.1rem',
                        marginBottom: '0.5rem'
                    }}>
                        CHOICE LOCKED IN
                    </p>
                    <p style={{
                        color: '#888',
                        fontSize: '0.9rem',
                        margin: 0
                    }}>
                        You chose: <strong style={{ color: 'var(--warning)' }}>{currentChoice}</strong>
                    </p>
                    <p style={{
                        color: '#666',
                        fontSize: '0.8rem',
                        marginTop: '1rem'
                    }}>
                        Waiting for other players... ({choiceCount}/{alivePlayers.length})
                    </p>
                </motion.div>
            ) : (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '1rem'
                }}>
                    {choices.map((choice, index) => (
                        <motion.button
                            key={choice.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            whileHover={!submitting ? { scale: 1.03 } : {}}
                            whileTap={!submitting ? { scale: 0.97 } : {}}
                            onClick={() => handleChoice(choice.id)}
                            disabled={submitting}
                            style={{
                                background: selectedChoice === choice.id
                                    ? 'rgba(255, 200, 0, 0.3)'
                                    : 'rgba(255, 255, 255, 0.05)',
                                border: selectedChoice === choice.id
                                    ? '2px solid var(--warning)'
                                    : '2px solid #333',
                                borderRadius: '12px',
                                padding: '1.25rem',
                                cursor: submitting ? 'wait' : 'pointer',
                                textAlign: 'left',
                                position: 'relative',
                                opacity: submitting && selectedChoice !== choice.id ? 0.5 : 1
                            }}
                        >
                            <div style={{
                                position: 'absolute',
                                top: '0.5rem',
                                left: '0.75rem',
                                background: 'var(--warning)',
                                color: '#000',
                                fontWeight: 'bold',
                                padding: '0.25rem 0.5rem',
                                borderRadius: '4px',
                                fontSize: '0.8rem'
                            }}>
                                {choice.id}
                            </div>
                            <p style={{
                                color: '#fff',
                                margin: '1.5rem 0 0 0',
                                fontSize: '0.95rem',
                                lineHeight: '1.4'
                            }}>
                                {choice.text}
                            </p>
                            {selectedChoice === choice.id && submitting && (
                                <div style={{
                                    position: 'absolute',
                                    inset: 0,
                                    background: 'rgba(0,0,0,0.5)',
                                    borderRadius: '12px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}>
                                    <span className="spinner" style={{ width: '24px', height: '24px' }}></span>
                                </div>
                            )}
                        </motion.button>
                    ))}
                </div>
            )}

            {/* Progress indicator */}
            {!hasSubmitted && (
                <p style={{
                    textAlign: 'center',
                    color: '#666',
                    fontSize: '0.8rem',
                    marginTop: '1rem'
                }}>
                    {choiceCount}/{alivePlayers.length} players have chosen
                </p>
            )}
        </div>
    );
}
