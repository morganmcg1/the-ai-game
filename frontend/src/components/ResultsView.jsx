import React from 'react';
import { motion } from 'framer-motion';
import { Skull, Heart, Trophy, Medal, Users, Terminal } from 'lucide-react';

export function ResultsView({ round, players }) {
    const sortedPlayers = Object.values(players).sort((a, b) => b.score - a.score);
    const isCooperativeRound = round.type === 'cooperative';
    const isRankedRound = round.type === 'ranked';
    const isSacrificeRound = round.type === 'sacrifice';

    const getRankStyle = (index) => {
        if (index === 0) return { color: '#FFD700', icon: '1st' }; // Gold
        if (index === 1) return { color: '#C0C0C0', icon: '2nd' }; // Silver
        if (index === 2) return { color: '#CD7F32', icon: '3rd' }; // Bronze
        return { color: '#888', icon: `${index + 1}th` };
    };

    // For ranked rounds, sort players by their rank
    const rankedPlayers = isRankedRound
        ? Object.values(players)
            .filter(p => round.ranked_results && round.ranked_results[p.id])
            .sort((a, b) => (round.ranked_results[a.id] || 99) - (round.ranked_results[b.id] || 99))
        : [];

    // Get sacrifice outcome summary
    const getSacrificeSummary = () => {
        if (!isSacrificeRound || !round.martyr_id) return null;
        const martyr = players[round.martyr_id];
        if (!martyr) return null;

        if (round.martyr_epic) {
            return {
                text: `${martyr.name} sacrificed themselves with an epic death so that the others could live.`,
                color: 'var(--success)'
            };
        } else {
            return {
                text: `${martyr.name}'s sacrifice was too lame to save anyone. Everyone perished.`,
                color: 'var(--danger)'
            };
        }
    };

    const sacrificeSummary = getSacrificeSummary();

    // Get round outcome summary for survival-type rounds
    const getRoundSummary = () => {
        // Skip for round types with their own summaries
        if (isSacrificeRound || isCooperativeRound) return null;

        const alivePlayers = Object.values(players).filter(p => p.is_alive);
        const deadPlayers = Object.values(players).filter(p => !p.is_alive);
        const total = Object.keys(players).length;

        if (isRankedRound) {
            // For ranked rounds, show who survived
            const survivor = alivePlayers[0];
            if (survivor) {
                return {
                    text: `${survivor.name} ranked #1 and survived. ${deadPlayers.length} eliminated.`,
                    color: 'var(--warning)'
                };
            } else {
                return { text: "No one survived the rankings.", color: 'var(--danger)' };
            }
        }

        if (deadPlayers.length === total) {
            return { text: "Total wipeout. No survivors.", color: 'var(--danger)' };
        } else if (alivePlayers.length === total) {
            return { text: "Everyone made it out alive.", color: 'var(--success)' };
        } else {
            return {
                text: `${alivePlayers.length} survived. ${deadPlayers.length} didn't make it.`,
                color: 'var(--warning)'
            };
        }
    };

    const roundSummary = getRoundSummary();

    const getTitle = () => {
        if (isCooperativeRound) return 'TEAM SYNC RESULTS';
        if (isRankedRound) return 'SURVIVAL RANKINGS';
        return 'PROCESSING COMPLETE';
    };

    return (
        <div style={{ width: '100%', maxWidth: '1100px' }}>
            <h1 className="glitch-text" style={{ textAlign: 'center', marginBottom: (sacrificeSummary || roundSummary) ? '1rem' : '2rem', color: isRankedRound ? '#ffd700' : undefined }}>
                {getTitle()}
            </h1>

            {/* Sacrifice round outcome summary */}
            {sacrificeSummary && (
                <p style={{
                    textAlign: 'center',
                    marginBottom: '2rem',
                    color: sacrificeSummary.color,
                    fontFamily: 'monospace',
                    fontSize: '1.1rem',
                    fontStyle: 'italic'
                }}>
                    {sacrificeSummary.text}
                </p>
            )}

            {/* Survival round outcome summary */}
            {roundSummary && (
                <p style={{
                    textAlign: 'center',
                    marginBottom: '2rem',
                    color: roundSummary.color,
                    fontFamily: 'monospace',
                    fontSize: '1.1rem',
                    fontStyle: 'italic'
                }}>
                    {roundSummary.text}
                </p>
            )}

            {/* Cooperative Round: Side-by-side layout with leaderboard on right */}
            {isCooperativeRound && (
                <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
                    {/* Left side: Team Outcome + Vote Points (3/4 width) */}
                    <div style={{ flex: '3' }}>
                        {/* Team Outcome Card */}
                        <motion.div
                            className="card"
                            style={{
                                marginBottom: '1.5rem',
                                textAlign: 'center',
                                padding: '2rem',
                                border: `2px solid ${round.coop_team_survived ? 'var(--success)' : 'var(--danger)'}`,
                                maxWidth: round.coop_team_survived ? undefined : '600px',
                                marginLeft: round.coop_team_survived ? undefined : 'auto',
                                marginRight: round.coop_team_survived ? undefined : 'auto'
                            }}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                        >
                            <Users size={48} color={round.coop_team_survived ? 'var(--success)' : 'var(--danger)'} style={{ marginBottom: '1rem' }} />
                            <h2 style={{ color: round.coop_team_survived ? 'var(--success)' : 'var(--danger)', fontSize: '2rem', marginBottom: '1rem' }}>
                                {round.coop_team_survived ? 'STRATEGY SYNC SUCCESSFUL' : 'STRATEGY SYNC FAILED'}
                            </h2>

                            {/* Show voted strategy and who submitted it */}
                            {round.coop_winning_strategy_id && players[round.coop_winning_strategy_id] && (
                                <div style={{ marginBottom: '1rem' }}>
                                    <p style={{ color: '#888', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                                        Voted strategy by <strong style={{ color: 'var(--secondary)' }}>{players[round.coop_winning_strategy_id]?.name}</strong>:
                                    </p>
                                    <p style={{
                                        color: '#fff',
                                        padding: '0.75rem 1rem',
                                        background: 'rgba(0, 0, 0, 0.4)',
                                        borderRadius: '8px',
                                        borderLeft: '3px solid var(--secondary)',
                                        fontStyle: 'italic',
                                        lineHeight: '1.4'
                                    }}>
                                        "{players[round.coop_winning_strategy_id]?.strategy || 'No strategy submitted'}"
                                    </p>
                                </div>
                            )}

                            {/* Show judgement reason */}
                            {round.coop_team_reason && (
                                <p style={{
                                    color: '#ccc',
                                    marginBottom: '1rem',
                                    fontStyle: 'italic',
                                    padding: '0.75rem 1rem',
                                    background: 'rgba(0, 0, 0, 0.3)',
                                    borderRadius: '8px',
                                    borderLeft: `3px solid ${round.coop_team_survived ? 'var(--success)' : 'var(--danger)'}`
                                }}>
                                    "{round.coop_team_reason}"
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

                            {/* Team result image - only show single image if team survived */}
                            {round.coop_team_survived && round.scenario_image_url && (
                                <div style={{ marginTop: '1.5rem', borderRadius: '8px', overflow: 'hidden' }}>
                                    <img src={round.scenario_image_url} alt="Team Result" style={{ width: '100%', maxWidth: '500px', height: 'auto', display: 'block', margin: '0 auto' }} />
                                </div>
                            )}
                        </motion.div>

                        {/* When team failed: Show all player cards with their strategies */}
                        {!round.coop_team_survived && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                            >
                                {(() => {
                                    const lobbyPlayers = sortedPlayers.filter(p => p.in_lobby !== false);
                                    const playerCount = lobbyPlayers.length;
                                    const isOdd = playerCount % 2 === 1;
                                    const pairedPlayers = isOdd ? lobbyPlayers.slice(0, -1) : lobbyPlayers;
                                    const lastPlayer = isOdd ? lobbyPlayers[lobbyPlayers.length - 1] : null;

                                    const renderCoopFailCard = (player, index) => {
                                        const strategyImage = round.strategy_images?.[player.id];
                                        return (
                                            <motion.div
                                                key={player.id}
                                                className="card"
                                                style={{
                                                    padding: '0',
                                                    overflow: 'hidden',
                                                    border: '2px solid var(--danger)',
                                                }}
                                                initial={{ opacity: 0, scale: 0.9 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                                transition={{ delay: 0.3 + index * 0.05 }}
                                            >
                                                {/* Strategy image */}
                                                {strategyImage ? (
                                                    <div style={{ position: 'relative' }}>
                                                        <img
                                                            src={strategyImage}
                                                            alt="Strategy"
                                                            style={{ width: '100%', height: 'auto', display: 'block' }}
                                                        />
                                                        <div style={{
                                                            position: 'absolute',
                                                            top: '0.5rem',
                                                            right: '0.5rem',
                                                            background: 'var(--danger)',
                                                            borderRadius: '50%',
                                                            padding: '0.4rem',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            justifyContent: 'center'
                                                        }}>
                                                            <Skull color="#000" size={16} />
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
                                                        <Skull color="var(--danger)" size={32} />
                                                    </div>
                                                )}

                                                {/* Info section */}
                                                <div style={{ padding: '1rem' }}>
                                                    <div style={{
                                                        display: 'flex',
                                                        justifyContent: 'space-between',
                                                        alignItems: 'center',
                                                        marginBottom: '0.5rem'
                                                    }}>
                                                        <span style={{
                                                            fontWeight: 'bold',
                                                            fontSize: '1.1rem',
                                                            color: 'var(--danger)'
                                                        }}>
                                                            {player.name}
                                                        </span>
                                                        <span style={{
                                                            color: 'var(--danger)',
                                                            fontWeight: 'bold',
                                                            fontSize: '1rem'
                                                        }}>
                                                            TERMINATED
                                                        </span>
                                                    </div>

                                                    {/* Player's strategy */}
                                                    {player.strategy && (
                                                        <div style={{
                                                            fontSize: '0.85rem',
                                                            color: '#ccc',
                                                            lineHeight: '1.3',
                                                            fontStyle: 'italic'
                                                        }}>
                                                            "{player.strategy}"
                                                        </div>
                                                    )}
                                                </div>
                                            </motion.div>
                                        );
                                    };

                                    return (
                                        <>
                                            <div style={{
                                                display: 'grid',
                                                gridTemplateColumns: 'repeat(2, 1fr)',
                                                gap: '1rem',
                                            }}>
                                                {pairedPlayers.map((player, index) => renderCoopFailCard(player, index))}
                                            </div>

                                            {lastPlayer && (
                                                <div style={{
                                                    display: 'flex',
                                                    justifyContent: 'center',
                                                    marginTop: '1rem'
                                                }}>
                                                    <div style={{ width: 'calc(50% - 0.5rem)' }}>
                                                        {renderCoopFailCard(lastPlayer, lobbyPlayers.length - 1)}
                                                    </div>
                                                </div>
                                            )}
                                        </>
                                    );
                                })()}
                            </motion.div>
                        )}

                        {/* Vote Points Breakdown - only show when team survived */}
                        {round.coop_team_survived && Object.keys(round.coop_vote_points || {}).length > 0 && (
                            <motion.div
                                className="card"
                                style={{
                                    padding: '1.5rem',
                                    marginTop: '2rem',
                                    maxWidth: '500px',
                                    marginLeft: 'auto',
                                    marginRight: 'auto'
                                }}
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
                    </div>

                    {/* Right side: Leaderboard (1/4 width) */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        style={{ flex: '1', minWidth: '220px', maxWidth: '280px' }}
                    >
                        <h2 style={{ textAlign: 'center', marginBottom: '1rem', color: 'var(--primary)', fontSize: '1.1rem' }}>
                            <Trophy size={20} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />
                            SURVIVOMETER
                        </h2>
                        <div className="card" style={{ width: '100%', padding: '0.75rem' }}>
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
                                            padding: '0.5rem 0.75rem',
                                            borderBottom: index < sortedPlayers.length - 1 ? '1px solid #333' : 'none',
                                            background: index === 0 ? 'rgba(255, 215, 0, 0.1)' : 'transparent'
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <span style={{
                                                color: rankStyle.color,
                                                fontWeight: 'bold',
                                                fontSize: '0.9rem',
                                                minWidth: '32px'
                                            }}>
                                                {rankStyle.icon}
                                            </span>
                                            {player.character_image_url && (
                                                <img
                                                    src={player.character_image_url}
                                                    alt=""
                                                    style={{
                                                        width: '24px',
                                                        height: '24px',
                                                        borderRadius: '50%',
                                                        objectFit: 'cover'
                                                    }}
                                                />
                                            )}
                                            <span style={{ color: '#fff', fontSize: '0.9rem' }}>{player.name}</span>
                                        </div>
                                        <span style={{
                                            color: 'var(--primary)',
                                            fontWeight: 'bold',
                                            fontSize: '0.9rem'
                                        }}>
                                            {player.score.toLocaleString()}
                                        </span>
                                    </motion.div>
                                );
                            })}
                        </div>
                    </motion.div>
                </div>
            )}

            {/* Ranked Round: Side-by-side layout with cards on left, leaderboard on right */}
            {isRankedRound && (
                <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
                    {/* Left side: Player cards (3/4 width) */}
                    <div style={{ flex: '3' }}>
                        {/* Card grid - max 2 columns, odd players have last card centered */}
                        {(() => {
                            const playerCount = rankedPlayers.length;
                            const isOdd = playerCount % 2 === 1;
                            const pairedPlayers = isOdd ? rankedPlayers.slice(0, -1) : rankedPlayers;
                            const lastPlayer = isOdd ? rankedPlayers[rankedPlayers.length - 1] : null;

                            const renderCard = (player, index) => {
                                const points = round.ranked_points?.[player.id] || 0;
                                const commentary = round.ranked_commentary?.[player.id] || '';
                                const rankStyle = getRankStyle(index);
                                const isRankOneSurvivor = player.is_alive;
                                const statusColor = isRankOneSurvivor ? 'var(--success)' : 'var(--danger)';

                                return (
                                    <motion.div
                                        key={player.id}
                                        className="card"
                                        style={{
                                            padding: '0',
                                            overflow: 'hidden',
                                            border: `2px solid ${statusColor}`,
                                        }}
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        transition={{ delay: index * 0.1 }}
                                    >
                                        {/* Result Image */}
                                        {player.result_image_url ? (
                                            <div style={{ position: 'relative' }}>
                                                <img
                                                    src={player.result_image_url}
                                                    alt="Result"
                                                    style={{ width: '100%', height: 'auto', display: 'block' }}
                                                />
                                                {/* Survival status icon */}
                                                <div style={{
                                                    position: 'absolute',
                                                    top: '0.5rem',
                                                    right: '0.5rem',
                                                    background: statusColor,
                                                    borderRadius: '50%',
                                                    padding: '0.4rem',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center'
                                                }}>
                                                    {isRankOneSurvivor ? <Heart color="#000" size={16} /> : <Skull color="#000" size={16} />}
                                                </div>
                                                {/* Rank badge */}
                                                <div style={{
                                                    position: 'absolute',
                                                    top: '0.5rem',
                                                    left: '0.5rem',
                                                    background: rankStyle.color,
                                                    borderRadius: '8px',
                                                    padding: '0.4rem 0.8rem',
                                                    fontWeight: 'bold',
                                                    color: '#000',
                                                    fontSize: '0.9rem'
                                                }}>
                                                    {rankStyle.icon}
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

                                        {/* Info section */}
                                        <div style={{ padding: '1rem' }}>
                                            <div style={{
                                                display: 'flex',
                                                justifyContent: 'space-between',
                                                alignItems: 'center',
                                                marginBottom: '0.5rem'
                                            }}>
                                                <span style={{
                                                    fontWeight: 'bold',
                                                    fontSize: '1.1rem',
                                                    color: statusColor
                                                }}>
                                                    {player.name}
                                                </span>
                                                <span style={{
                                                    color: rankStyle.color,
                                                    fontWeight: 'bold',
                                                    fontSize: '1rem'
                                                }}>
                                                    +{points}
                                                </span>
                                            </div>

                                            {/* Player's strategy */}
                                            {player.strategy && (
                                                <div style={{
                                                    fontSize: '0.85rem',
                                                    color: '#ccc',
                                                    lineHeight: '1.4',
                                                    marginBottom: '0.75rem',
                                                    padding: '0.5rem 0.75rem',
                                                    background: 'rgba(0, 0, 0, 0.3)',
                                                    borderRadius: '6px',
                                                    borderLeft: '3px solid #666'
                                                }}>
                                                    <span style={{ color: '#888', fontWeight: 'bold', display: 'block', marginBottom: '0.25rem', fontSize: '0.75rem' }}>
                                                        STRATEGY:
                                                    </span>
                                                    "{player.strategy}"
                                                </div>
                                            )}

                                            {/* Status and Commentary */}
                                            <div style={{
                                                fontSize: '0.85rem',
                                                color: statusColor,
                                                lineHeight: '1.3',
                                                fontStyle: 'italic'
                                            }}>
                                                <span style={{ fontWeight: 'bold', fontStyle: 'normal' }}>
                                                    {isRankOneSurvivor ? 'SURVIVED: ' : 'TERMINATED: '}
                                                </span>
                                                {commentary}
                                            </div>
                                        </div>
                                    </motion.div>
                                );
                            };

                            return (
                                <>
                                    {/* 2-column grid for paired players */}
                                    <div style={{
                                        display: 'grid',
                                        gridTemplateColumns: 'repeat(2, 1fr)',
                                        gap: '1rem',
                                    }}>
                                        {pairedPlayers.map((player, index) => renderCard(player, index))}
                                    </div>

                                    {/* Centered last card for odd player counts */}
                                    {lastPlayer && (
                                        <div style={{
                                            display: 'flex',
                                            justifyContent: 'center',
                                            marginTop: '1rem'
                                        }}>
                                            <div style={{ width: 'calc(50% - 0.5rem)' }}>
                                                {renderCard(lastPlayer, rankedPlayers.length - 1)}
                                            </div>
                                        </div>
                                    )}
                                </>
                            );
                        })()}
                    </div>

                    {/* Right side: Leaderboard (1/4 width) */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        style={{ flex: '1', minWidth: '220px', maxWidth: '280px' }}
                    >
                        <h2 style={{ textAlign: 'center', marginBottom: '1rem', color: 'var(--primary)', fontSize: '1.1rem' }}>
                            <Trophy size={20} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />
                            SURVIVOMETER
                        </h2>
                        <div className="card" style={{ width: '100%', padding: '0.75rem' }}>
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
                                            padding: '0.5rem 0.75rem',
                                            borderBottom: index < sortedPlayers.length - 1 ? '1px solid #333' : 'none',
                                            background: index === 0 ? 'rgba(255, 215, 0, 0.1)' : 'transparent'
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <span style={{
                                                color: rankStyle.color,
                                                fontWeight: 'bold',
                                                fontSize: '0.9rem',
                                                minWidth: '32px'
                                            }}>
                                                {rankStyle.icon}
                                            </span>
                                            {player.character_image_url && (
                                                <img
                                                    src={player.character_image_url}
                                                    alt=""
                                                    style={{
                                                        width: '24px',
                                                        height: '24px',
                                                        borderRadius: '50%',
                                                        objectFit: 'cover'
                                                    }}
                                                />
                                            )}
                                            <span style={{ color: '#fff', fontSize: '0.9rem' }}>{player.name}</span>
                                        </div>
                                        <span style={{
                                            color: 'var(--primary)',
                                            fontWeight: 'bold',
                                            fontSize: '0.9rem'
                                        }}>
                                            {player.score.toLocaleString()}
                                        </span>
                                    </motion.div>
                                );
                            })}
                        </div>
                    </motion.div>
                </div>
            )}

            {/* Non-cooperative/Non-ranked: Side-by-side layout with cards on left, leaderboard on right */}
            {!isCooperativeRound && !isRankedRound && (
                <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
                    {/* Left side: Player cards (3/4 width) */}
                    <div style={{ flex: '3' }}>
                        {/* Card grid - max 2 columns, odd players have last card centered */}
                        {(() => {
                            const playerCount = sortedPlayers.length;
                            const isOdd = playerCount % 2 === 1;
                            const pairedPlayers = isOdd ? sortedPlayers.slice(0, -1) : sortedPlayers;
                            const lastPlayer = isOdd ? sortedPlayers[sortedPlayers.length - 1] : null;

                            const renderCard = (player, index) => (
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

                                        {/* Player's strategy */}
                                        {player.strategy && (
                                            <div style={{
                                                fontSize: '0.85rem',
                                                color: '#ccc',
                                                lineHeight: '1.4',
                                                marginBottom: '0.75rem',
                                                padding: '0.5rem 0.75rem',
                                                background: 'rgba(0, 0, 0, 0.3)',
                                                borderRadius: '6px',
                                                borderLeft: '3px solid #666'
                                            }}>
                                                <span style={{ color: '#888', fontWeight: 'bold', display: 'block', marginBottom: '0.25rem', fontSize: '0.75rem' }}>
                                                    STRATEGY:
                                                </span>
                                                "{player.strategy}"
                                            </div>
                                        )}

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
                            );

                            return (
                                <>
                                    {/* 2-column grid for paired players */}
                                    <div style={{
                                        display: 'grid',
                                        gridTemplateColumns: 'repeat(2, 1fr)',
                                        gap: '1rem',
                                    }}>
                                        {pairedPlayers.map((player, index) => renderCard(player, index))}
                                    </div>

                                    {/* Centered last card for odd player counts */}
                                    {lastPlayer && (
                                        <div style={{
                                            display: 'flex',
                                            justifyContent: 'center',
                                            marginTop: '1rem'
                                        }}>
                                            <div style={{ width: 'calc(50% - 0.5rem)' }}>
                                                {renderCard(lastPlayer, sortedPlayers.length - 1)}
                                            </div>
                                        </div>
                                    )}
                                </>
                            );
                        })()}
                    </div>

                    {/* Right side: Leaderboard (1/4 width) */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        style={{ flex: '1', minWidth: '220px', maxWidth: '280px' }}
                    >
                        <h2 style={{ textAlign: 'center', marginBottom: '1rem', color: 'var(--primary)', fontSize: '1.1rem' }}>
                            <Trophy size={20} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />
                            SURVIVOMETER
                        </h2>
                        <div className="card" style={{ width: '100%', padding: '0.75rem' }}>
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
                                            padding: '0.5rem 0.75rem',
                                            borderBottom: index < sortedPlayers.length - 1 ? '1px solid #333' : 'none',
                                            background: index === 0 ? 'rgba(255, 215, 0, 0.1)' : 'transparent'
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <span style={{
                                                color: rankStyle.color,
                                                fontWeight: 'bold',
                                                fontSize: '0.9rem',
                                                minWidth: '32px'
                                            }}>
                                                {rankStyle.icon}
                                            </span>
                                            {player.character_image_url && (
                                                <img
                                                    src={player.character_image_url}
                                                    alt=""
                                                    style={{
                                                        width: '24px',
                                                        height: '24px',
                                                        borderRadius: '50%',
                                                        objectFit: 'cover'
                                                    }}
                                                />
                                            )}
                                            <span style={{ color: '#fff', fontSize: '0.9rem' }}>{player.name}</span>
                                        </div>
                                        <span style={{
                                            color: 'var(--primary)',
                                            fontWeight: 'bold',
                                            fontSize: '0.9rem'
                                        }}>
                                            {player.score.toLocaleString()}
                                        </span>
                                    </motion.div>
                                );
                            })}
                        </div>
                    </motion.div>
                </div>
            )}
        </div>
    );
}
