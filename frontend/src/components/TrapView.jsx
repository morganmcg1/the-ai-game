import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';

const DEFAULT_TIMEOUT_SECONDS = 30;

export function TrapView({ round, playerId, onSubmit, config = {} }) {
    const timeoutSeconds = config.submission_timeout_seconds || DEFAULT_TIMEOUT_SECONDS;
    const [trapText, setTrapText] = useState('');
    const [loading, setLoading] = useState(false);
    const [timeLeft, setTimeLeft] = useState(timeoutSeconds);

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
        if (!trapText.trim()) return;
        setLoading(true);
        await onSubmit(trapText);
        setLoading(false);
    }, [trapText, onSubmit]);

    // Keyboard shortcut: Cmd/Ctrl + Enter to submit
    useEffect(() => {
        const handleKeyDown = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && !loading && trapText.trim()) {
                e.preventDefault();
                handleSubmit();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [loading, trapText, handleSubmit]);

    // Timer color based on urgency
    const getTimerColor = () => {
        if (timeLeft <= 5) return '#ff0000';
        if (timeLeft <= 10) return '#ff6600';
        if (timeLeft <= 15) return '#ffcc00';
        return 'var(--accent)';
    };

    const timerColor = getTimerColor();
    const isUrgent = timeLeft <= 10;

    if (round.trap_proposals && round.trap_proposals[playerId]) {
        return (
            <div className="card" style={{ textAlign: 'center' }}>
                <h2 style={{ fontFamily: 'monospace', color: 'var(--accent)' }}>ENVIRONMENT UPLOADED</h2>
                <p style={{ fontFamily: 'monospace', color: '#0f0' }}>&gt; Rendering deadly scenario...</p>
                <span className="loader"></span>
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
                background: `rgba(${timeLeft <= 10 ? '255, 0, 0' : '255, 0, 0'}, 0.1)`,
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
                        HURRY!
                    </span>
                )}
            </div>

            {/* System breach header */}
            <div style={{
                fontFamily: 'monospace',
                color: '#f00',
                fontSize: '0.8rem',
                marginBottom: '1rem',
                padding: '0.5rem',
                background: 'rgba(255, 0, 0, 0.1)',
                border: '1px solid rgba(255, 0, 0, 0.3)',
                borderRadius: '4px',
                animation: 'flicker 2s infinite'
            }}>
                &gt; SECURITY BREACH // ARCHITECT PERMISSIONS GRANTED
            </div>

            <h2 style={{ marginBottom: '1rem', color: 'var(--accent)', fontFamily: 'monospace' }}>ARCHITECT MODE</h2>
            <p style={{ marginBottom: '1.5rem', opacity: 0.8, fontFamily: 'monospace' }}>
                You have accessed the simulation's core. Design a deadly environment for other users.
            </p>

            <textarea
                value={trapText}
                onChange={(e) => setTrapText(e.target.value)}
                placeholder="A laboratory where gravity reverses every 10 seconds..."
                style={{
                    width: '100%',
                    minHeight: '120px',
                    background: 'rgba(0,0,0,0.3)',
                    border: '1px solid var(--accent)',
                    color: 'white',
                    padding: '1rem',
                    borderRadius: '8px',
                    marginBottom: '1.5rem',
                    resize: 'vertical',
                    fontFamily: 'inherit'
                }}
            />

            <button
                className="primary"
                onClick={handleSubmit}
                disabled={loading || !trapText.trim()}
                style={{ width: '100%', backgroundColor: 'var(--accent)', color: 'black' }}
            >
                {loading ? 'COMPILING ENVIRONMENT...' : 'UPLOAD ENVIRONMENT'}
                {!loading && <span style={{ opacity: 0.6, fontSize: '0.75rem', marginLeft: '0.5rem' }}>(⌘↵)</span>}
            </button>
        </div>
    );
}
