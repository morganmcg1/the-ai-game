import React from 'react';
import { motion } from 'framer-motion';
import { Skull, Heart, Trophy } from 'lucide-react';

export function ResultsView({ round, players }) {
    // Identify deaths and survivors
    // In the real app, round results would be structured.
    // Here we iterate players to find who died in this round (logic might need fetching death history or just current state)
    // For MVP: Show all players status.

    const sortedPlayers = Object.values(players).sort((a, b) => b.score - a.score);

    return (
        <div style={{ width: '100%', maxWidth: '800px' }}>
            <h1 className="glitch-text" style={{ textAlign: 'center', marginBottom: '2rem' }}>JUDGEMENT DAY</h1>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                {sortedPlayers.map((player) => (
                    <motion.div
                        key={player.id}
                        className="card"
                        style={{
                            width: 'auto',
                            border: player.is_alive ? '1px solid var(--success)' : '1px solid var(--danger)',
                            opacity: player.is_alive ? 1 : 0.7
                        }}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: player.is_alive ? 1 : 0.7, y: 0 }}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <h3 style={{ color: player.is_alive ? 'var(--success)' : 'var(--danger)' }}>{player.name}</h3>
                            {player.is_alive ? <Heart color="var(--success)" size={20} /> : <Skull color="var(--danger)" size={20} />}
                        </div>

                        <div style={{ marginBottom: '1rem', fontStyle: 'italic', color: '#ccc', fontSize: '0.9rem' }}>
                            "{player.strategy || "No strategy..."}"
                        </div>

                        {!player.is_alive && (
                            <div style={{ color: 'var(--danger)', fontWeight: 'bold', fontSize: '0.9rem' }}>
                                Cause of Death: {player.death_reason || "Unknown"}
                            </div>
                        )}

                        {player.is_alive && (
                            <div style={{ color: 'var(--success)', fontWeight: 'bold' }}>
                                +100 PTS
                            </div>
                        )}

                        {/* If we had images per player result, allow showing here.  */}
                        {/* For now, just styling. */}
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
