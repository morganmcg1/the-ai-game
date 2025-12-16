import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api';
import { Play, Users } from 'lucide-react';

export function Lobby({ onJoin, onAdmin, setPlayerId }) {
    const [name, setName] = useState('');
    const [code, setCode] = useState('');
    const [isJoinMode, setIsJoinMode] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleCreate = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await api.createGame();
            if (data.code) {
                // Admin automatically joins
                const joinData = await api.joinGame(data.code, name || "Admin");
                if (joinData.error) throw new Error(joinData.error);

                onAdmin(true);
                onJoin(data.code, joinData.player_id, name || "Admin");
                setPlayerId(joinData.player_id);
            }
        } catch (e) {
            setError('Failed to create game. ' + e.message);
        } finally {
            setLoading(false);
        }
    };

    const handleJoin = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await api.joinGame(code, name);
            if (data.error) throw new Error(data.error);

            onAdmin(data.is_admin);
            onJoin(code, data.player_id, name);
            setPlayerId(data.player_id);
        } catch (e) {
            setError('Failed to join game. ' + e.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <h1 className="glitch-text" style={{ fontSize: '3rem', textAlign: 'center', marginBottom: '1rem' }}>
                    DEATH BY AI
                </h1>
                <p style={{ textAlign: 'center', color: '#888', marginBottom: '2rem' }}>
                    Survive the algorithm.
                </p>

                {error && (
                    <div style={{ color: 'var(--danger)', background: 'rgba(255, 46, 46, 0.1)', padding: '10px', borderRadius: '8px', marginBottom: '1rem', textAlign: 'center' }}>
                        {error}
                    </div>
                )}

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <input
                        type="text"
                        placeholder="Enter your name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        data-testid="name-input"
                    />

                    {!isJoinMode ? (
                        <>
                            <button
                                className="primary"
                                onClick={handleCreate}
                                disabled={!name || loading}
                                data-testid="create-game-btn"
                            >
                                {loading ? 'Creating...' : 'CREATE NEW GAME'}
                            </button>
                            <button className="secondary" onClick={() => setIsJoinMode(true)} data-testid="join-mode-btn">
                                JOIN EXISTING GAME
                            </button>
                        </>
                    ) : (
                        <>
                            <input
                                type="text"
                                placeholder="Game Code (4 chars)"
                                value={code}
                                onChange={(e) => setCode(e.target.value.toUpperCase())}
                                maxLength={4}
                                data-testid="code-input"
                            />
                            <button
                                className="primary"
                                onClick={handleJoin}
                                disabled={!name || !code || loading}
                                data-testid="join-game-btn"
                            >
                                {loading ? 'Joining...' : 'JOIN GAME'}
                            </button>
                            <button className="secondary" onClick={() => setIsJoinMode(false)}>
                                BACK
                            </button>
                        </>
                    )}
                </div>
            </motion.div>
        </div>
    );
}
