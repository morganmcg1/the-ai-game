import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw } from 'lucide-react';
import { api } from '../api';

// 5 character description fields
const CHARACTER_FIELDS = [
    {
        id: 'look',
        label: 'PHYSICAL VIBE',
        placeholder: '"wild purple hair, leather jacket, mysterious scar"'
    },
    {
        id: 'weapon',
        label: 'SIGNATURE WEAPON',
        placeholder: '"rusty machete", "flaming guitar", "pocket sand"'
    },
    {
        id: 'talent',
        label: 'HIDDEN TALENT',
        placeholder: '"can talk to animals", "expert lockpicker", "never sleeps"'
    },
    {
        id: 'flaw',
        label: 'FATAL FLAW',
        placeholder: '"trusts everyone", "allergic to running", "speaks too loud"'
    },
    {
        id: 'catchphrase',
        label: 'CATCHPHRASE',
        placeholder: '"I\'ve seen worse", "Hold my beer", "Not again..."'
    }
];

export function Lobby({ onJoin, onAdmin, setPlayerId }) {
    const [name, setName] = useState('');
    const [code, setCode] = useState('');
    const [mode, setMode] = useState('menu'); // 'menu', 'join', 'character', or 'preview'
    const [error, setError] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [isJoining, setIsJoining] = useState(false);
    const [pendingAction, setPendingAction] = useState(null); // 'create' or 'join'

    // Character fields state
    const [characterFields, setCharacterFields] = useState({
        look: '',
        weapon: '',
        talent: '',
        flaw: '',
        catchphrase: ''
    });

    // Preview state - stored after joining but before going to lobby
    const [previewData, setPreviewData] = useState(null); // { gameCode, playerId, isAdmin, characterImageUrl }
    const [isRegenerating, setIsRegenerating] = useState(false);

    // Combine character fields into a single prompt
    const buildCharacterPrompt = () => {
        const parts = [];
        if (characterFields.look) parts.push(characterFields.look);
        if (characterFields.weapon) parts.push(`wielding ${characterFields.weapon}`);
        if (characterFields.talent) parts.push(`known for ${characterFields.talent}`);
        if (characterFields.flaw) parts.push(`weakness: ${characterFields.flaw}`);
        if (characterFields.catchphrase) parts.push(`says "${characterFields.catchphrase}"`);
        return parts.join(', ');
    };

    const handleCharacterFieldChange = (fieldId, value) => {
        setCharacterFields(prev => ({ ...prev, [fieldId]: value }));
    };

    // Proceed to character creation
    const proceedToCharacter = (action) => {
        if (!name.trim()) {
            setError("Please enter your codename");
            return;
        }
        if (action === 'join' && !code) {
            setError("Enter game code");
            return;
        }
        setError('');
        setPendingAction(action);
        setMode('character');
    };

    // Poll for character image when in preview mode
    useEffect(() => {
        if (mode !== 'preview' || !previewData?.gameCode || !previewData?.playerId) return;

        const pollForImage = async () => {
            try {
                const state = await api.getGameState(previewData.gameCode, previewData.playerId);
                if (state && state.players && state.players[previewData.playerId]) {
                    const player = state.players[previewData.playerId];
                    if (player.character_image_url) {
                        setPreviewData(prev => ({
                            ...prev,
                            characterImageUrl: player.character_image_url
                        }));
                    }
                }
            } catch (e) {
                console.error("Poll error:", e);
            }
        };

        // Poll immediately and then every 2 seconds
        pollForImage();
        const interval = setInterval(pollForImage, 2000);
        return () => clearInterval(interval);
    }, [mode, previewData?.gameCode, previewData?.playerId]);

    const handleCreate = useCallback(async () => {
        const characterPrompt = buildCharacterPrompt();
        setIsCreating(true);
        setError('');
        try {
            const data = await api.createGame();
            if (data.code) {
                const joinData = await api.joinGame(data.code, name || "Admin", characterPrompt || null);
                if (joinData.error) throw new Error(joinData.error);

                // If no character description, skip preview and go straight to lobby
                if (!characterPrompt) {
                    onAdmin(true);
                    onJoin(data.code, joinData.player_id, name || "Admin");
                    setPlayerId(joinData.player_id);
                } else {
                    // Go to preview mode
                    setPreviewData({
                        gameCode: data.code,
                        playerId: joinData.player_id,
                        isAdmin: true,
                        characterImageUrl: null
                    });
                    setMode('preview');
                    setIsCreating(false);
                }
            }
        } catch (e) {
            setError('Failed to create game. ' + e.message);
            setIsCreating(false);
            setMode('menu');
        }
    }, [name, characterFields, onAdmin, onJoin, setPlayerId]);

    const handleJoin = useCallback(async () => {
        const characterPrompt = buildCharacterPrompt();
        setIsJoining(true);
        setError('');
        try {
            const joinData = await api.joinGame(code, name, characterPrompt || null);
            if (joinData.error) throw new Error(joinData.error);

            // If no character description, skip preview and go straight to lobby
            if (!characterPrompt) {
                onAdmin(joinData.is_admin);
                onJoin(code, joinData.player_id, name);
                setPlayerId(joinData.player_id);
            } else {
                // Go to preview mode
                setPreviewData({
                    gameCode: code,
                    playerId: joinData.player_id,
                    isAdmin: joinData.is_admin,
                    characterImageUrl: null
                });
                setMode('preview');
                setIsJoining(false);
            }
        } catch (e) {
            setError('Failed to join game. ' + e.message);
            setIsJoining(false);
            setMode('join');
        }
    }, [name, code, characterFields, onAdmin, onJoin, setPlayerId]);

    // Handle final submission from character screen
    const handleCharacterSubmit = () => {
        if (pendingAction === 'create') {
            handleCreate();
        } else {
            handleJoin();
        }
    };

    // Handle regenerate in preview mode
    const handleRegenerate = async () => {
        if (!previewData?.gameCode || !previewData?.playerId) return;
        setIsRegenerating(true);
        setPreviewData(prev => ({ ...prev, characterImageUrl: null }));
        try {
            await api.regenerateCharacterImage(previewData.gameCode, previewData.playerId);
        } catch (e) {
            console.error("Regenerate error:", e);
        }
        setIsRegenerating(false);
    };

    // Proceed from preview to actual lobby
    const handleContinueToLobby = async () => {
        if (!previewData) return;
        // Notify backend that player has entered the lobby
        await api.enterLobby(previewData.gameCode, previewData.playerId);
        onAdmin(previewData.isAdmin);
        onJoin(previewData.gameCode, previewData.playerId, name);
        setPlayerId(previewData.playerId);
    };

    // Keyboard shortcut: Cmd/Ctrl + Enter
    useEffect(() => {
        const handleKeyDown = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                e.preventDefault();
                if (mode === 'menu' && !isCreating) {
                    proceedToCharacter('create');
                } else if (mode === 'character' && !isCreating && !isJoining) {
                    handleCharacterSubmit();
                } else if (mode === 'preview' && previewData?.characterImageUrl) {
                    handleContinueToLobby();
                }
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [mode, isCreating, isJoining, handleCreate, handleJoin, pendingAction, name, code, previewData]);

    return (
        <div className="card lobby-card">
            <h1 className="game-title">DEATH BY AI</h1>

            {/* Simulation intro tagline */}
            <p style={{
                fontFamily: 'monospace',
                color: '#0f0',
                fontSize: '0.8rem',
                marginTop: '-1rem',
                marginBottom: '1.5rem',
                opacity: 0.8,
                textAlign: 'center'
            }}>
                &gt; CORRUPTED SIMULATION DETECTED // SURVIVE TO ESCAPE
            </p>

            {error && <div className="error-banner">{error}</div>}

            {/* Name Input - Always visible in menu and join modes */}
            {(mode === 'menu' || mode === 'join') && (
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
            )}

            <div className="lobby-actions" style={{ gap: '1.5rem', display: 'flex', flexDirection: 'column' }}>
                {mode === 'menu' && (
                    <>
                        <button
                            className="primary"
                            onClick={() => proceedToCharacter('create')}
                            disabled={isCreating}
                            data-testid="create-game-btn"
                        >
                            NEW GAME
                            <span style={{ opacity: 0.6, fontSize: '0.75rem', marginLeft: '0.5rem' }}>(⌘↵)</span>
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
                            onClick={() => proceedToCharacter('join')}
                            data-testid="join-game-btn"
                        >
                            NEXT
                        </button>
                        <button className="text-btn" onClick={() => setMode('menu')}>
                            Back
                        </button>
                    </>
                )}

                {mode === 'character' && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <div style={{
                            textAlign: 'center',
                            marginBottom: '1.5rem',
                            padding: '1rem',
                            background: 'rgba(255,255,255,0.05)',
                            borderRadius: '8px'
                        }}>
                            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>
                                {name.toUpperCase()}
                            </div>
                            <div style={{ opacity: 0.7, fontSize: '0.9rem' }}>
                                Describe your character for an AI-generated avatar
                            </div>
                        </div>

                        {CHARACTER_FIELDS.map((field, idx) => (
                            <motion.div
                                key={field.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.08 }}
                                className="input-group"
                                style={{ marginBottom: '1rem' }}
                            >
                                <label style={{ marginBottom: '0.4rem', display: 'block' }}>
                                    {field.label}
                                </label>
                                <input
                                    type="text"
                                    placeholder={field.placeholder}
                                    value={characterFields[field.id]}
                                    onChange={(e) => handleCharacterFieldChange(field.id, e.target.value)}
                                    maxLength={60}
                                    style={{ fontSize: '0.9rem' }}
                                />
                            </motion.div>
                        ))}

                        <div style={{
                            marginTop: '1.5rem',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '1rem'
                        }}>
                            <button
                                className="primary"
                                onClick={handleCharacterSubmit}
                                disabled={isCreating || isJoining}
                                data-testid="character-submit-btn"
                            >
                                {(isCreating || isJoining) ? <span className="spinner"></span> : null}
                                {isCreating ? "CREATING..." : isJoining ? "JOINING..." : "GENERATE CHARACTER"}
                                {!(isCreating || isJoining) && (
                                    <span style={{ opacity: 0.6, fontSize: '0.75rem', marginLeft: '0.5rem' }}>(⌘↵)</span>
                                )}
                            </button>
                            <button
                                className="text-btn"
                                onClick={() => {
                                    setMode(pendingAction === 'create' ? 'menu' : 'join');
                                    setPendingAction(null);
                                }}
                                disabled={isCreating || isJoining}
                            >
                                Back
                            </button>
                            <div style={{
                                opacity: 0.5,
                                fontSize: '0.75rem',
                                textAlign: 'center'
                            }}>
                                All fields are optional - leave blank for a random character!
                            </div>
                        </div>
                    </motion.div>
                )}

                {mode === 'preview' && previewData && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.3 }}
                        style={{ textAlign: 'center' }}
                    >
                        <div style={{
                            marginBottom: '1.5rem',
                            padding: '1rem',
                            background: 'rgba(0,255,0,0.05)',
                            borderRadius: '8px',
                            border: '1px solid rgba(0,255,0,0.2)'
                        }}>
                            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: '#0f0' }}>
                                {name.toUpperCase()}
                            </div>
                            <div style={{ opacity: 0.7, fontSize: '0.9rem', fontFamily: 'monospace' }}>
                                &gt; USER AVATAR RENDERING...
                            </div>
                        </div>

                        {/* Character Image Preview */}
                        <div style={{
                            width: '200px',
                            height: '200px',
                            borderRadius: '12px',
                            overflow: 'hidden',
                            margin: '0 auto 1.5rem',
                            background: '#1a1a1a',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: '2px solid var(--primary)'
                        }}>
                            {previewData.characterImageUrl ? (
                                <motion.img
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    src={previewData.characterImageUrl}
                                    alt="Your character"
                                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                />
                            ) : (
                                <div style={{ textAlign: 'center' }}>
                                    <span className="spinner" style={{ width: '40px', height: '40px' }}></span>
                                    <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '1rem', fontFamily: 'monospace' }}>
                                        Generating avatar...
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Game code display */}
                        <div style={{
                            marginBottom: '1.5rem',
                            padding: '0.75rem',
                            background: 'rgba(255,255,255,0.05)',
                            borderRadius: '8px'
                        }}>
                            <div style={{ fontSize: '0.8rem', opacity: 0.6, marginBottom: '0.25rem' }}>GAME CODE</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', letterSpacing: '0.2em' }}>
                                {previewData.gameCode}
                            </div>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {/* Regenerate button */}
                            <button
                                onClick={handleRegenerate}
                                disabled={!previewData.characterImageUrl || isRegenerating}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '0.5rem',
                                    background: 'transparent',
                                    border: '1px solid var(--secondary)',
                                    borderRadius: '8px',
                                    padding: '0.75rem 1rem',
                                    color: 'var(--secondary)',
                                    cursor: previewData.characterImageUrl && !isRegenerating ? 'pointer' : 'not-allowed',
                                    opacity: previewData.characterImageUrl && !isRegenerating ? 1 : 0.5,
                                    fontSize: '0.9rem'
                                }}
                            >
                                <RefreshCw size={16} className={isRegenerating ? 'spinning' : ''} />
                                {isRegenerating ? 'REGENERATING...' : 'TRY NEW LOOK'}
                            </button>

                            {/* Continue button */}
                            <button
                                className="primary"
                                onClick={handleContinueToLobby}
                                disabled={!previewData.characterImageUrl}
                                style={{
                                    opacity: previewData.characterImageUrl ? 1 : 0.5
                                }}
                            >
                                {previewData.characterImageUrl ? 'ENTER LOBBY' : 'WAITING FOR AVATAR...'}
                                {previewData.characterImageUrl && (
                                    <span style={{ opacity: 0.6, fontSize: '0.75rem', marginLeft: '0.5rem' }}>(⌘↵)</span>
                                )}
                            </button>

                            <div style={{
                                opacity: 0.5,
                                fontSize: '0.75rem',
                                fontFamily: 'monospace'
                            }}>
                                Don't like it? Regenerate for a different art style!
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
