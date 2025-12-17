import React from 'react';
import { motion } from 'framer-motion';
import { Skull, Heart, Trophy, Medal, Users } from 'lucide-react';

export function ResultsView({ round, players }) {
    const sortedPlayers = Object.values(players).sort((a, b) => b.score - a.score);
    const isCooperativeRound = round.type === 'cooperative';

    const getRankStyle = (index) => {
        if (index === 0) return { color: '#FFD700', icon: '1st' }; // Gold
        if (index === 1) return { color: '#C0C0C0', icon: '2nd' }; // Silver
        if (index === 2) return { color: '#CD7F32', icon: '3rd' }; // Bronze
        return { color: '#888', icon: `${index + 1}th` };
    };

    return (
        <div style={{ width: '100%', maxWidth: '800px' }}>
            <h1 className="glitch-text" style={{ textAlign: 'center', marginBottom: '2rem' }}>
                {isCooperativeRound ? 'COOPERATION RESULTS' : 'JUDGEMENT DAY'}
            </h1>

            {/* Cooperative Round: Team Outcome Card */}
            {isCooperativeRound && (
                <motion.div
                    className="card"
                    style={{
                        marginBottom: '2rem',
                        textAlign: 'center',
                        padding: '2rem',
                        border: `2px solid ${round.coop_team_survived ? 'var(--success)' : 'var(--danger)'}`
                    }}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                >
                    <Users size={48} color={round.coop_team_survived ? 'var(--success)' : 'var(--danger)'} style={{ marginBottom: '1rem' }} />
                    <h2 style={{ color: round.coop_team_survived ? 'var(--success)' : 'var(--danger)', fontSize: '2rem', marginBottom: '1rem' }}>
                        {round.coop_team_survived ? 'TEAM SURVIVED!' : 'TEAM FAILED!'}
                    </h2>

                    {/* Show winning strategy */}
                    {round.coop_winning_strategy_id && players[round.coop_winning_strategy_id] && (
                        <p style={{ color: '#ccc', marginBottom: '1rem' }}>
                            Winning strategy by: <strong style={{ color: 'var(--secondary)' }}>{players[round.coop_winning_strategy_id]?.name}</strong>
                        </p>
                    )}

                    {/* Show random bonus/penalty */}
                    {round.coop_team_winner_id && players[round.coop_team_winner_id] && (
                        <div style={{
                            marginTop: '1rem',
                            padding: '0.75rem 1rem',
                            background: 'rgba(0, 255, 148, 0.15)',
                            borderRadius: '8px',
                            color: 'var(--success)',
                            fontWeight: 'bold'
                        }}>
                            {players[round.coop_team_winner_id]?.name} received +200 BONUS!
                        </div>
                    )}
                    {!round.coop_team_survived && (
                        <div style={{
                            marginTop: '1rem',
                            padding: '0.75rem 1rem',
                            background: 'rgba(255, 46, 46, 0.15)',
                            borderRadius: '8px',
                            color: 'var(--danger)',
                            fontWeight: 'bold'
                        }}>
                            All players lost -100 points!
                        </div>
                    )}

                    {/* Team result image */}
                    {round.scenario_image_url && (
                        <div style={{ marginTop: '1.5rem', borderRadius: '8px', overflow: 'hidden' }}>
                            <img src={round.scenario_image_url} alt="Team Result" style={{ width: '100%', maxWidth: '500px', height: 'auto', display: 'block', margin: '0 auto' }} />
                        </div>
                    )}
                </motion.div>
            )}

            {/* Cooperative Round: Vote Points Breakdown */}
            {isCooperativeRound && Object.keys(round.coop_vote_points || {}).length > 0 && (
                <motion.div
                    className="card"
                    style={{ marginBottom: '2rem', padding: '1.5rem' }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <h3 style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'var(--secondary)' }}>
                        VOTING RESULTS
                    </h3>
                    {sortedPlayers.map((player) => {
                        const votePoints = round.coop_vote_points[player.id] || 0;
                        return (
                            <div
                                key={player.id}
                                style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: '0.75rem 1rem',
                                    borderBottom: '1px solid #333'
                                }}
                            >
                                <span style={{ color: '#fff' }}>{player.name}</span>
                                <span style={{
                                    color: votePoints > 0 ? 'var(--success)' : votePoints < 0 ? 'var(--danger)' : '#888',
                                    fontWeight: 'bold',
                                    fontSize: '1.1rem'
                                }}>
                                    {votePoints > 0 ? '+' : ''}{votePoints} PTS
                                </span>
                            </div>
                        );
                    })}
                </motion.div>
            )}

            {/* Non-cooperative: Show individual player cards */}
            {!isCooperativeRound && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
                    {sortedPlayers.map((player) => (
                        <motion.div
                            key={player.id}
                            className="card"
                            style={{
                                width: 'auto',
                                padding: '1.5rem',
                                border: player.is_alive ? '2px solid var(--success)' : '2px solid var(--danger)',
                                opacity: player.is_alive ? 1 : 0.8
                            }}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: player.is_alive ? 1 : 0.8, y: 0 }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                <h3 style={{ color: player.is_alive ? 'var(--success)' : 'var(--danger)', fontSize: '1.3rem' }}>{player.name}</h3>
                                {player.is_alive ? <Heart color="var(--success)" size={24} /> : <Skull color="var(--danger)" size={24} />}
                            </div>

                            <div style={{ marginBottom: '1rem', fontStyle: 'italic', color: '#ccc', fontSize: '1rem', lineHeight: '1.4' }}>
                                "{player.strategy || "No strategy..."}"
                            </div>

                            {!player.is_alive && (
                                <div style={{ color: 'var(--danger)', fontWeight: 'bold', fontSize: '1rem', marginBottom: '0.75rem' }}>
                                    Cause of Death: {player.death_reason || "Unknown"}
                                </div>
                            )}

                            {player.is_alive && player.survival_reason && (
                                <div style={{ color: 'var(--success)', fontWeight: 'bold', fontSize: '1rem', marginBottom: '0.75rem' }}>
                                    Survived: {player.survival_reason}
                                </div>
                            )}

                            <div style={{
                                color: player.is_alive ? 'var(--success)' : 'var(--danger)',
                                fontWeight: 'bold',
                                fontSize: '1.4rem',
                                marginTop: '1rem',
                                padding: '0.5rem',
                                background: player.is_alive ? 'rgba(0, 255, 0, 0.1)' : 'rgba(255, 0, 0, 0.1)',
                                borderRadius: '4px',
                                textAlign: 'center'
                            }}>
                                {player.is_alive ? '+100 PTS' : '+0 PTS'}
                            </div>

                            {player.result_image_url ? (
                                <div style={{ marginTop: '1rem', borderRadius: '8px', overflow: 'hidden' }}>
                                    <img src={player.result_image_url} alt="Result" style={{ width: '100%', height: 'auto', display: 'block' }} />
                                </div>
                            ) : (
                                <div className="card" style={{ marginTop: '1rem', height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed #444' }}>
                                    <span className="spinner"></span> Generating Evidence...
                                </div>
                            )}
                        </motion.div>
                    ))}
                </div>
            )}

            {/* Leaderboard Section */}
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                style={{ marginTop: '3rem' }}
            >
                <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'var(--primary)' }}>
                    <Trophy size={24} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />
                    LEADERBOARD
                </h2>
                <div className="card" style={{ width: '100%', padding: '1rem' }}>
                    {sortedPlayers.map((player, index) => {
                        const rankStyle = getRankStyle(index);
                        return (
                            <motion.div
                                key={player.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.6 + index * 0.1 }}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    padding: '0.75rem 1rem',
                                    borderBottom: index < sortedPlayers.length - 1 ? '1px solid #333' : 'none',
                                    background: index === 0 ? 'rgba(255, 215, 0, 0.1)' : 'transparent'
                                }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                    <span style={{
                                        color: rankStyle.color,
                                        fontWeight: 'bold',
                                        fontSize: '1.1rem',
                                        minWidth: '40px'
                                    }}>
                                        {rankStyle.icon}
                                    </span>
                                    <span style={{ color: '#fff', fontSize: '1rem' }}>{player.name}</span>
                                </div>
                                <span style={{
                                    color: 'var(--primary)',
                                    fontWeight: 'bold',
                                    fontSize: '1.1rem'
                                }}>
                                    {player.score.toLocaleString()} PTS
                                </span>
                            </motion.div>
                        );
                    })}
                </div>
            </motion.div>
        </div>
    );
}
