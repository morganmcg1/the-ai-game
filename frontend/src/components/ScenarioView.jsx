import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';

export function ScenarioView({ round, isSpectating }) {
    if (!round) return null;

    return (
        <motion.div
            className="card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
        >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem', color: 'var(--primary)' }}>
                <AlertTriangle size={24} />
                <h2 style={{ textTransform: 'uppercase' }}>Round {round.number} // DANGER</h2>
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
                    Waiting for players to strategize...
                </div>
            )}
        </motion.div>
    );
}
