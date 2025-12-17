import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Terminal } from 'lucide-react';

export function ScenarioView({ round, isSpectating, maxRounds }) {
    if (!round) return null;

    // Calculate "corruption" percentage based on round progression
    const corruptionLevel = Math.min(95, 40 + (round.number * 12));

    return (
        <motion.div
            className="card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
        >
            {/* System Header */}
            <div className="system-header" style={{
                fontFamily: 'monospace',
                marginBottom: '1.5rem',
                padding: '0.75rem 1rem',
                background: 'rgba(0, 255, 0, 0.05)',
                border: '1px solid rgba(0, 255, 0, 0.2)',
                borderRadius: '4px'
            }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '0.5rem'
                }}>
                    <span className="glitch-text" style={{
                        color: '#0f0',
                        fontSize: '0.9rem',
                        letterSpacing: '0.1em'
                    }}>
                        <Terminal size={14} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'middle' }} />
                        LEVEL {round.number} // {round.sector_name || 'UNKNOWN SECTOR'}
                    </span>
                    <span style={{
                        color: corruptionLevel > 70 ? '#f00' : corruptionLevel > 50 ? '#ff0' : '#0f0',
                        fontSize: '0.8rem',
                        animation: corruptionLevel > 70 ? 'flicker 2s infinite' : 'none'
                    }}>
                        DATA INTEGRITY: {100 - corruptionLevel}%
                    </span>
                </div>
                {round.system_message && (
                    <div style={{
                        marginTop: '0.5rem',
                        color: '#0f0',
                        fontSize: '0.75rem',
                        opacity: 0.8
                    }}>
                        &gt; {round.system_message}
                    </div>
                )}
            </div>

            {/* Scenario Content */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem', color: 'var(--primary)' }}>
                <AlertTriangle size={24} />
                <h2 style={{ textTransform: 'uppercase' }}>ENVIRONMENT LOADED</h2>
            </div>

            <div style={{ fontSize: '1.5rem', lineHeight: '1.4', marginBottom: '2rem', fontWeight: 300 }}>
                {round.scenario_text}
            </div>

            {round.scenario_image_url && (
                <motion.img
                    src={round.scenario_image_url}
                    alt="Scenario"
                    style={{ width: '100%', borderRadius: '8px', marginBottom: '2rem' }}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                />
            )}

            {isSpectating && (
                <div style={{ textAlign: 'center', color: '#888', marginTop: '1rem' }}>
                    <span className="loader" style={{ width: '16px', height: '16px', marginRight: '8px' }}></span>
                    Awaiting user survival protocols...
                </div>
            )}
        </motion.div>
    );
}
