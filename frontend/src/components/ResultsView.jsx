import React from 'react';
import { motion } from 'framer-motion';
import { Skull, Heart, Trophy, Medal, Users, Terminal } from 'lucide-react';

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
                {isCooperativeRound ? 'TEAM SYNC RESULTS' : 'PROCESSING COMPLETE'}
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
                        {round.coop_team_survived ? 'SYNC SUCCESSFUL' : 'SYNC FAILED'}
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

            {/* Non-cooperative: Show individual player cards in a compact grid */}
            {!isCooperativeRound && (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                    gap: '1rem'
                }}>
                    {sortedPlayers.map((player, index) => (
                        <motion.div
                            key={player.id}
                            className="card"
                            style={{
                                padding: '0',
                                overflow: 'hidden',
                                border: player.is_alive ? '2px solid var(--success)' : '2px solid var(--danger)',
                            }}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.05 }}
                        >
                            {/* Image first - prominent, full aspect ratio */}
                            {player.result_image_url ? (
                                <div style={{ position: 'relative' }}>
                                    <img
                                        src={player.result_image_url}
                                        alt="Result"
                                        style={{ width: '100%', height: 'auto', display: 'block' }}
                                    />
                                    {/* Overlay with status */}
                                    <div style={{
                                        position: 'absolute',
                                        top: '0.5rem',
                                        right: '0.5rem',
                                        background: player.is_alive ? 'var(--success)' : 'var(--danger)',
                                        borderRadius: '50%',
                                        padding: '0.4rem',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center'
                                    }}>
                                        {player.is_alive ? <Heart color="#000" size={16} /> : <Skull color="#000" size={16} />}
                                    </div>
                                </div>
                            ) : (
                                <div style={{
                                    aspectRatio: '16/9',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    background: '#1a1a1a'
                                }}>
                                    <span className="spinner"></span>
                                </div>
                            )}

                            {/* Compact info section */}
                            <div style={{ padding: '1rem' }}>
                                {/* Name and points row */}
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    marginBottom: '0.5rem'
                                }}>
                                    <span style={{
                                        fontWeight: 'bold',
                                        fontSize: '1.1rem',
                                        color: player.is_alive ? 'var(--success)' : 'var(--danger)'
                                    }}>
                                        {player.name}
                                    </span>
                                    <span style={{
                                        color: player.is_alive ? 'var(--success)' : 'var(--danger)',
                                        fontWeight: 'bold',
                                        fontSize: '1rem'
                                    }}>
                                        {player.is_alive ? '+100' : '+0'}
                                    </span>
                                </div>

                                {/* Judgement reason */}
                                <div style={{
                                    fontSize: '0.85rem',
                                    color: player.is_alive ? 'var(--success)' : 'var(--danger)',
                                    lineHeight: '1.3',
                                    fontStyle: 'italic'
                                }}>
                                    <span style={{ fontWeight: 'bold', fontStyle: 'normal' }}>
                                        {player.is_alive ? 'SURVIVED: ' : 'TERMINATED: '}
                                    </span>
                                    {player.is_alive
                                        ? (player.survival_reason || 'Made it through!')
                                        : (player.death_reason || 'Did not survive')}
                                </div>
                            </div>
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
                    INTEGRITY RANKINGS
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
