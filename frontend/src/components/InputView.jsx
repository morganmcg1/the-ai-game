import React, { useState } from 'react';
import { motion } from 'framer-motion';

export function InputView({ round, playerId, onSubmit }) {
    const [strategy, setStrategy] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

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

    return (
        <div className="card input-card">
            <h3>YOUR STRATEGY</h3>
            <p className="hint-text">How do you survive this scenario? Be creative...</p>
            <div className="input-wrapper">
                <textarea
                    value={strategy}
                    onChange={(e) => setStrategy(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="I would use the..."
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
                        <span className="spinner"></span> TRANSMITTING...
                    </>
                ) : (
                    <>
                        TRANSMIT STRATEGY <span className="shortcut-hint">[⌘↵]</span>
                    </>
                )}
            </button>
        </div>
    );
}
