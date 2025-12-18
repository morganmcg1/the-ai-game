import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Skull, Heart, Clock } from 'lucide-react';

const DEFAULT_TIMEOUT_SECONDS = 45;

export function SacrificeSubmissionView({ round, playerId, players, onSubmit, config = {} }) {
    const timeoutSeconds = config.sacrifice_submission_timeout_seconds || DEFAULT_TIMEOUT_SECONDS;
    const [speech, setSpeech] = useState('');
    const [loading, setLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [timeLeft, setTimeLeft] = useState(timeoutSeconds);

    const isMartyr = round.martyr_id === playerId;
    const martyrPlayer = players[round.martyr_id];

    // Countdown timer effect
    useEffect(() => {
        if (!round.submission_start_time) return;

        const updateTimer = () => {
            const elapsed = (Date.now() / 1000) - round.submission_start_time;
            const remaining = Math.max(0, timeoutSeconds - elapsed);
            setTimeLeft(Math.ceil(remaining));
        };

        updateTimer(); // Initial update
        const interval = setInterval(updateTimer, 100);
        return () => clearInterval(interval);
    }, [round.submission_start_time, timeoutSeconds]);

    const handleSubmit = useCallback(async () => {
        if (!speech.trim() || loading) return;
        setLoading(true);
        await onSubmit(speech);
        setSubmitted(true);
        setLoading(false);
    }, [speech, loading, onSubmit]);

    // Keyboard shortcut: Cmd/Ctrl + Enter to submit
    useEffect(() => {
        if (!isMartyr) return;

        const handleKeyDown = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && !loading && speech.trim()) {
                e.preventDefault();
                handleSubmit();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isMartyr, loading, speech, handleSubmit]);

    // Timer color based on urgency
    const getTimerColor = () => {
        if (timeLeft <= 5) return '#ff0000';
        if (timeLeft <= 10) return '#ff6600';
        if (timeLeft <= 15) return '#ffcc00';
        return '#ffd700';
    };

    const timerColor = getTimerColor();
    const isUrgent = timeLeft <= 10;

    // Martyr view - submit death speech
    if (isMartyr) {
        if (submitted) {
            return (
                <div className="card" style={{ textAlign: 'center' }}>
                    <div style={{
                        fontFamily: 'monospace',
                        color: '#ffd700',
                        fontSize: '0.8rem',
                        marginBottom: '1rem',
                        padding: '0.5rem',
                        background: 'rgba(255, 215, 0, 0.1)',
                        border: '1px solid rgba(255, 215, 0, 0.3)',
                        borderRadius: '4px'
                    }}>
                        SACRIFICE RECORDED // EVALUATING HEROISM
                    </div>
                    <h2 style={{ fontFamily: 'monospace', color: '#ffd700' }}>
                        <Heart size={24} style={{ marginRight: '0.5rem' }} />
                        YOUR SACRIFICE HAS BEEN WITNESSED
                    </h2>
                    <p style={{ fontFamily: 'monospace', color: '#0f0', marginTop: '1rem' }}>
                        Evaluating the epicness of your death...
                    </p>
                    <span className="loader" style={{ marginTop: '1rem' }}></span>
                </div>
            );
        }

        return (
            <div className="card">
                {/* Timer display */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    gap: '0.5rem',
                    marginBottom: '1rem',
                    padding: '0.75rem',
                    background: `rgba(${timeLeft <= 10 ? '255, 0, 0' : '255, 215, 0'}, 0.1)`,
                    border: `2px solid ${timerColor}`,
                    borderRadius: '8px',
                    animation: isUrgent ? 'pulse 0.5s infinite' : 'none'
                }}>
                    <Clock size={20} color={timerColor} />
                    <span style={{
                        fontFamily: 'monospace',
                        fontSize: '1.5rem',
                        fontWeight: 'bold',
                        color: timerColor,
                        textShadow: isUrgent ? `0 0 10px ${timerColor}` : 'none'
                    }}>
                        {timeLeft}s
                    </span>
                    {timeLeft <= 10 && (
                        <span style={{
                            fontFamily: 'monospace',
                            fontSize: '0.8rem',
                            color: timerColor,
                            marginLeft: '0.5rem'
                        }}>
                            SPEAK NOW OR DOOM EVERYONE!
                        </span>
                    )}
                </div>

                <div style={{
                    fontFamily: 'monospace',
                    color: '#ffd700',
                    fontSize: '0.8rem',
                    marginBottom: '1rem',
                    padding: '0.5rem',
                    background: 'rgba(255, 215, 0, 0.1)',
                    border: '1px solid rgba(255, 215, 0, 0.3)',
                    borderRadius: '4px',
                    animation: 'flicker 2s infinite'
                }}>
                    YOU HAVE BEEN CHOSEN // PREPARE YOUR FINAL MOMENTS
                </div>

                <h2 style={{
                    marginBottom: '1rem',
                    color: '#ffd700',
                    fontFamily: 'monospace',
                    textAlign: 'center'
                }}>
                    <Skull size={20} style={{ marginRight: '0.5rem' }} />
                    YOU ARE THE MARTYR
                    <Skull size={20} style={{ marginLeft: '0.5rem' }} />
                </h2>

                <p style={{
                    marginBottom: '1.5rem',
                    opacity: 0.9,
                    fontFamily: 'monospace',
                    textAlign: 'center',
                    lineHeight: 1.6
                }}>
                    Your death can save the others - but only if it's <span style={{ color: '#ffd700' }}>EPIC</span>.
                    <br />
                    Describe your heroic final moments. Make it dramatic!
                </p>

                <textarea
                    value={speech}
                    onChange={(e) => setSpeech(e.target.value)}
                    placeholder="I charge headfirst into the swarm, my battle cry echoing through the halls. As the creatures overwhelm me, I pull the pin on my last grenade and whisper: 'See you in hell...' The explosion takes them all with me."
                    style={{
                        width: '100%',
                        minHeight: '150px',
                        background: 'rgba(0,0,0,0.3)',
                        border: '1px solid #ffd700',
                        color: 'white',
                        padding: '1rem',
                        borderRadius: '8px',
                        marginBottom: '1rem',
                        resize: 'vertical',
                        fontFamily: 'inherit'
                    }}
                />

                <p style={{
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    opacity: 0.6,
                    marginBottom: '1rem',
                    textAlign: 'center'
                }}>
                    Tips: Be creative! Dramatic speeches, heroic actions, or funny last words all count.
                    <br />
                    If your death is judged EPIC: You get +500 pts and everyone else survives (+100 pts each).
                    <br />
                    If your death is judged LAME: Everyone dies. No points for anyone.
                </p>

                <motion.button
                    className="primary"
                    onClick={handleSubmit}
                    disabled={loading || !speech.trim()}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    style={{
                        width: '100%',
                        backgroundColor: '#ffd700',
                        color: 'black',
                        fontFamily: 'monospace',
                        fontSize: '1rem'
                    }}
                >
                    {loading ? 'SUBMITTING...' : 'EMBRACE YOUR FATE'}
                    {!loading && <span style={{ opacity: 0.6, fontSize: '0.75rem', marginLeft: '0.5rem' }}>(+Enter)</span>}
                </motion.button>
            </div>
        );
    }

    // Non-martyr view - waiting with timer showing
    return (
        <div className="card" style={{ textAlign: 'center' }}>
            {/* Timer display for spectators */}
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '1rem',
                padding: '0.75rem',
                background: `rgba(${timeLeft <= 10 ? '255, 0, 0' : '255, 215, 0'}, 0.1)`,
                border: `2px solid ${timerColor}`,
                borderRadius: '8px',
                animation: isUrgent ? 'pulse 0.5s infinite' : 'none'
            }}>
                <Clock size={20} color={timerColor} />
                <span style={{
                    fontFamily: 'monospace',
                    fontSize: '1.5rem',
                    fontWeight: 'bold',
                    color: timerColor,
                    textShadow: isUrgent ? `0 0 10px ${timerColor}` : 'none'
                }}>
                    {timeLeft}s
                </span>
                {timeLeft <= 10 && (
                    <span style={{
                        fontFamily: 'monospace',
                        fontSize: '0.8rem',
                        color: timerColor,
                        marginLeft: '0.5rem'
                    }}>
                        TIME RUNNING OUT!
                    </span>
                )}
            </div>

            <div style={{
                fontFamily: 'monospace',
                color: 'var(--accent)',
                fontSize: '0.8rem',
                marginBottom: '1rem',
                padding: '0.5rem',
                background: 'rgba(0, 255, 255, 0.1)',
                border: '1px solid rgba(0, 255, 255, 0.3)',
                borderRadius: '4px'
            }}>
                SACRIFICE IN PROGRESS // WITNESS MODE ACTIVE
            </div>

            <h2 style={{
                marginBottom: '1rem',
                fontFamily: 'monospace',
                color: 'var(--accent)'
            }}>
                <Clock size={24} style={{ marginRight: '0.5rem' }} />
                AWAITING SACRIFICE
            </h2>

            <p style={{
                fontFamily: 'monospace',
                opacity: 0.8,
                marginBottom: '1.5rem'
            }}>
                <span style={{ color: '#ff6b6b', fontWeight: 'bold' }}>
                    {martyrPlayer?.name || 'The chosen one'}
                </span>
                {' '}is preparing their final moments.
            </p>

            <div style={{
                background: 'rgba(255, 68, 68, 0.1)',
                border: '1px solid rgba(255, 68, 68, 0.3)',
                borderRadius: '8px',
                padding: '1rem',
                marginBottom: '1rem'
            }}>
                <p style={{
                    fontFamily: 'monospace',
                    fontSize: '0.9rem',
                    color: 'rgba(255, 255, 255, 0.7)'
                }}>
                    If their sacrifice is <span style={{ color: '#ffd700' }}>EPIC</span>:
                    <br />
                    You survive and earn <span style={{ color: '#0f0' }}>+100 points</span>
                </p>
                <p style={{
                    fontFamily: 'monospace',
                    fontSize: '0.9rem',
                    color: 'rgba(255, 255, 255, 0.7)',
                    marginTop: '0.5rem'
                }}>
                    If their sacrifice is <span style={{ color: '#666' }}>LAME</span>:
                    <br />
                    <span style={{ color: '#ff4444' }}>Everyone dies. No points.</span>
                </p>
            </div>

            <span className="loader"></span>
            <p style={{
                fontFamily: 'monospace',
                fontSize: '0.8rem',
                opacity: 0.5,
                marginTop: '1rem'
            }}>
                Pray for a good death...
            </p>
        </div>
    );
}
