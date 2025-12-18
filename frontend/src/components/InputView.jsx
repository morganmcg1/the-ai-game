import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';

const DEFAULT_TIMEOUT_SECONDS = 30;

export function InputView({ round, playerId, onSubmit, flatTop = false, config = {} }) {
    const timeoutSeconds = config.submission_timeout_seconds || DEFAULT_TIMEOUT_SECONDS;
    const [strategy, setStrategy] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
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

    const handleSubmit = async () => {
        if (!strategy.trim() || isSubmitting) return;
        setIsSubmitting(true);
        try {
            await onSubmit(strategy);
            // Don't reset isSubmitting here, wait for parent to unmount us
            // But if there is an error, we might need to reset.
            // For now, parent "optimistic" update should hide us instantly.
        } catch (e) {
            setIsSubmitting(false);
            alert("Failed to submit");
        }
    };

    const handleKeyDown = (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            if (strategy.trim() && !isSubmitting) {
                handleSubmit();
            }
        }
    };

    // Timer color based on urgency
    const getTimerColor = () => {
        if (timeLeft <= 5) return '#ff0000';
        if (timeLeft <= 10) return '#ff6600';
        if (timeLeft <= 15) return '#ffcc00';
        return 'var(--primary)';
    };

    const timerColor = getTimerColor();
    const isUrgent = timeLeft <= 10;

    return (
        <div className="card input-card" style={flatTop ? { borderTopLeftRadius: 0, borderTopRightRadius: 0, marginTop: 0 } : {}}>
            {/* Timer display */}
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '1rem',
                padding: '0.75rem',
                background: `rgba(${timeLeft <= 10 ? '255, 0, 0' : '0, 255, 255'}, 0.1)`,
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

            <h3 style={{ fontFamily: 'monospace', color: 'var(--secondary)' }}>SURVIVAL PROTOCOL</h3>
            <p className="hint-text" style={{ fontFamily: 'monospace' }}>Input your survival strategy.</p>
            <div className="input-wrapper">
                <textarea
                    value={strategy}
                    onChange={(e) => setStrategy(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="I would..."
                    disabled={isSubmitting}
                    autoFocus
                    data-testid="strategy-input"
                />
            </div>
            <button
                className="primary full-width"
                onClick={handleSubmit}
                disabled={!strategy.trim() || isSubmitting}
                data-testid="submit-strategy-btn"
            >
                {isSubmitting ? (
                    <>
                        <span className="spinner"></span> UPLOADING PROTOCOL...
                    </>
                ) : (
                    <>
                        SUBMIT PROTOCOL <span className="shortcut-hint">[⌘↵]</span>
                    </>
                )}
            </button>
        </div>
    );
}
