import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api';

export function Lobby({ onJoin, onAdmin, setPlayerId }) {
    const [name, setName] = useState('');
    const [code, setCode] = useState('');
    const [mode, setMode] = useState('menu'); // 'menu' or 'join'
    const [error, setError] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [isJoining, setIsJoining] = useState(false);

    const handleCreate = useCallback(async () => {
        if (!name.trim()) {
            setError("Please enter your name");
            return;
        }
        setIsCreating(true);
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
            setIsCreating(false);
        }
    }, [name, onAdmin, onJoin, setPlayerId]);

    // Keyboard shortcut: Cmd/Ctrl + Enter to create game
    useEffect(() => {
        const handleKeyDown = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && mode === 'menu' && !isCreating) {
                e.preventDefault();
                handleCreate();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [mode, isCreating, handleCreate]);

    const handleJoin = async () => {
        if (!name.trim()) {
            setError("Please enter your name");
            return;
        }
        if (!code) {
            setError("Enter game code");
            return;
        }
        setIsJoining(true);
        setError('');
        try {
            const data = await api.joinGame(code, name);
            if (data.error) throw new Error(data.error);

            onAdmin(data.is_admin);
            onJoin(code, data.player_id, name);
            setPlayerId(data.player_id);
        } catch (e) {
            setError('Failed to join game. ' + e.message);
            setIsJoining(false);
        }
    };

    return (
        <div className="card lobby-card">
            <h1 className="game-title">DEATH BY AI</h1>
            {error && <div className="error-banner">{error}</div>}

            <div className="input-group" style={{ marginBottom: '2.5rem' }}>
                <label style={{ marginBottom: '0.5rem', display: 'block' }}>CODENAME</label>
                <input
                    type="text"
                    placeholder="Enter your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    maxLength={12}
                    data-testid="name-input"
                />
            </div>

            <div className="lobby-actions" style={{ gap: '1.5rem', display: 'flex', flexDirection: 'column' }}>
                {mode === 'menu' && (
                    <>
                        <button
                            className="primary"
                            onClick={handleCreate}
                            disabled={isCreating}
                            data-testid="create-game-btn"
                        >
                            {isCreating ? <span className="spinner"></span> : null}
                            {isCreating ? "CREATING..." : "NEW GAME"}
                            {!isCreating && <span style={{ opacity: 0.6, fontSize: '0.75rem', marginLeft: '0.5rem' }}>(⌘↵)</span>}
                        </button>
                        <div className="divider" style={{ margin: '0.5rem 0' }}>OR</div>
                        <button className="secondary" onClick={() => setMode('join')} data-testid="join-mode-btn">
                            JOIN GAME
                        </button>
                    </>
                )}

                {mode === 'join' && (
                    <>
                        <div className="input-group">
                            <label>ACCESS CODE</label>
                            <input
                                type="text"
                                placeholder="ABCD"
                                value={code}
                                onChange={(e) => setCode(e.target.value.toUpperCase())}
                                maxLength={4}
                                data-testid="code-input"
                            />
                        </div>
                        <button
                            className="primary"
                            onClick={handleJoin}
                            disabled={isJoining}
                            data-testid="join-game-btn"
                        >
                            {isJoining ? <span className="spinner"></span> : null}
                            {isJoining ? "JOINING..." : "ENTER"}
                        </button>
                        <button className="text-btn" onClick={() => setMode('menu')}>
                            Back
                        </button>
                    </>
                )}
            </div>
        </div>
    );
}
