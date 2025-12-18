import React from 'react';
import { motion } from 'framer-motion';
import { Terminal } from 'lucide-react';

export function ScenarioView({ round, isSpectating, maxRounds, flatBottom = false }) {
    if (!round) return null;

    return (
        <motion.div
            className="card"
            style={flatBottom ? { borderBottomLeftRadius: 0, borderBottomRightRadius: 0, marginBottom: 0 } : {}}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
        >
            {/* Round Header */}
            <div style={{
                fontFamily: 'monospace',
                marginBottom: '1.5rem',
                padding: '1rem 1.25rem',
                background: 'rgba(0, 240, 255, 0.05)',
                border: '1px solid rgba(0, 240, 255, 0.2)',
                borderRadius: '4px'
            }}>
                <div className="glitch-text" style={{
                    color: '#00F0FF',
                    fontSize: '1.25rem',
                    letterSpacing: '0.1em',
                    marginBottom: round.system_message ? '0.5rem' : 0
                }}>
                    <Terminal size={18} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'middle' }} />
                    ROUND {round.number}
                </div>
                {round.system_message && (
                    <div style={{
                        color: '#00F0FF',
                        fontSize: '1rem',
                        letterSpacing: '0.05em'
                    }}>
                        {round.system_message}
                    </div>
                )}
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
