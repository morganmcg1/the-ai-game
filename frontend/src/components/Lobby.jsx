import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Shuffle, Copy, Check } from 'lucide-react';
import { api } from '../api';

// Game code display component with copy button
function GameCodeDisplay({ code }) {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    return (
        <div style={{
            marginBottom: '1.5rem',
            padding: '0.75rem',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '8px'
        }}>
            <div style={{ fontSize: '0.8rem', opacity: 0.6, marginBottom: '0.25rem' }}>GAME CODE</div>
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem'
            }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', letterSpacing: '0.2em' }}>
                    {code}
                </div>
                <button
                    onClick={handleCopy}
                    style={{
                        background: copied ? 'var(--success)' : 'rgba(255,255,255,0.1)',
                        border: 'none',
                        borderRadius: '6px',
                        padding: '0.5rem',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all 0.2s ease'
                    }}
                    title="Copy game code"
                >
                    {copied ? (
                        <Check size={18} color="#000" />
                    ) : (
                        <Copy size={18} color="#fff" />
                    )}
                </button>
            </div>
        </div>
    );
}

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
    const [mode, setMode] = useState('menu'); // 'menu', 'join', 'character', 'random_select', or 'preview'
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

    // Random character selection state
    const [randomCharacters, setRandomCharacters] = useState([]); // Array of { traits, prompt, url }
    const [isLoadingRandom, setIsLoadingRandom] = useState(false);
    const [selectedRandomIdx, setSelectedRandomIdx] = useState(null);

    // Preview state - stored after joining but before going to lobby
    // traits: { look, weapon, talent, flaw, catchphrase }
    const [previewData, setPreviewData] = useState(null); // { gameCode, playerId, isAdmin, characterImageUrl, traits }
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

    // Generate 8 random characters
    const handleGenerateRandom = async () => {
        setIsLoadingRandom(true);
        setRandomCharacters([]);
        setSelectedRandomIdx(null);
        setMode('random_select');
        setError('');

        try {
            const result = await api.generateRandomCharacters();
            if (result.characters && result.characters.length > 0) {
                setRandomCharacters(result.characters);
            } else {
                setError("Failed to generate random characters. Try again!");
                setMode('character');
            }
        } catch (e) {
            console.error("Random generation error:", e);
            setError("Failed to generate random characters. Try again!");
            setMode('character');
        }
        setIsLoadingRandom(false);
    };

    // Handle selecting a random character and joining
    const handleSelectRandomCharacter = async (idx) => {
        const selected = randomCharacters[idx];
        if (!selected) return;

        setSelectedRandomIdx(idx);
        setIsCreating(pendingAction === 'create');
        setIsJoining(pendingAction === 'join');
        setError('');

        try {
            if (pendingAction === 'create') {
                const data = await api.createGame();
                if (data.code) {
                    // Join with the selected character's prompt AND the pre-generated image URL
                    const joinData = await api.joinGame(data.code, name || "Admin", selected.prompt, selected.url);
                    if (joinData.error) throw new Error(joinData.error);

                    // Go directly to preview with the already-generated image and traits
                    setPreviewData({
                        gameCode: data.code,
                        playerId: joinData.player_id,
                        isAdmin: true,
                        characterImageUrl: selected.url,
                        traits: selected.traits // Include the random traits
                    });
                    setMode('preview');
                }
            } else {
                // Join existing game with pre-generated image
                const joinData = await api.joinGame(code, name, selected.prompt, selected.url);
                if (joinData.error) throw new Error(joinData.error);

                setPreviewData({
                    gameCode: code,
                    playerId: joinData.player_id,
                    isAdmin: joinData.is_admin,
                    characterImageUrl: selected.url,
                    traits: selected.traits // Include the random traits
                });
                setMode('preview');
            }
        } catch (e) {
            setError('Failed to join game. ' + e.message);
            setMode('random_select');
        }
        setIsCreating(false);
        setIsJoining(false);
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
                    // Go to preview mode with custom traits
                    setPreviewData({
                        gameCode: data.code,
                        playerId: joinData.player_id,
                        isAdmin: true,
                        characterImageUrl: null,
                        traits: { ...characterFields } // Include custom traits
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
                // Go to preview mode with custom traits
                setPreviewData({
                    gameCode: code,
                    playerId: joinData.player_id,
                    isAdmin: joinData.is_admin,
                    characterImageUrl: null,
                    traits: { ...characterFields } // Include custom traits
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
            <h1 className="game-title">SurvAIve</h1>

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

                            <div className="divider" style={{ margin: '0.25rem 0' }}>OR</div>

                            <button
                                onClick={handleGenerateRandom}
                                disabled={isCreating || isJoining || isLoadingRandom}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '0.5rem',
                                    background: 'linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%)',
                                    border: 'none',
                                    borderRadius: '8px',
                                    padding: '0.75rem 1rem',
                                    color: '#000',
                                    fontWeight: 'bold',
                                    cursor: 'pointer',
                                    fontSize: '0.9rem'
                                }}
                            >
                                <Shuffle size={18} />
                                RANDOM CHARACTER
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
                                Fill fields for custom character, or hit RANDOM for 8 surprises!
                            </div>
                        </div>
                    </motion.div>
                )}

                {mode === 'random_select' && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <div style={{
                            textAlign: 'center',
                            marginBottom: '1rem',
                            padding: '0.75rem',
                            background: 'rgba(255,255,255,0.05)',
                            borderRadius: '8px'
                        }}>
                            <div style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>
                                {name.toUpperCase()}
                            </div>
                            <div style={{ opacity: 0.7, fontSize: '0.85rem' }}>
                                {isLoadingRandom ? 'Generating 8 random characters...' : 'Pick your character!'}
                            </div>
                        </div>

                        {isLoadingRandom ? (
                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(4, 1fr)',
                                gap: '0.5rem',
                                marginBottom: '1rem'
                            }}>
                                {[...Array(8)].map((_, idx) => (
                                    <div
                                        key={idx}
                                        style={{
                                            aspectRatio: '1',
                                            borderRadius: '8px',
                                            background: '#1a1a1a',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            border: '2px solid #333'
                                        }}
                                    >
                                        <span className="spinner" style={{ width: '24px', height: '24px' }}></span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(4, 1fr)',
                                gap: '0.5rem',
                                marginBottom: '1rem'
                            }}>
                                {randomCharacters.map((char, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, scale: 0.8 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        transition={{ delay: idx * 0.05 }}
                                        onClick={() => !isCreating && !isJoining && handleSelectRandomCharacter(idx)}
                                        style={{
                                            aspectRatio: '1',
                                            borderRadius: '8px',
                                            overflow: 'hidden',
                                            cursor: (isCreating || isJoining) ? 'wait' : 'pointer',
                                            border: selectedRandomIdx === idx ? '3px solid var(--primary)' : '2px solid #333',
                                            transition: 'all 0.2s ease',
                                            transform: selectedRandomIdx === idx ? 'scale(1.05)' : 'scale(1)',
                                            position: 'relative'
                                        }}
                                    >
                                        <img
                                            src={char.url}
                                            alt={`Random character ${idx + 1}`}
                                            style={{
                                                width: '100%',
                                                height: '100%',
                                                objectFit: 'cover'
                                            }}
                                        />
                                        {selectedRandomIdx === idx && (
                                            <div style={{
                                                position: 'absolute',
                                                inset: 0,
                                                background: 'rgba(0, 255, 0, 0.2)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center'
                                            }}>
                                                <span className="spinner" style={{ width: '32px', height: '32px' }}></span>
                                            </div>
                                        )}
                                    </motion.div>
                                ))}
                            </div>
                        )}

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            <button
                                onClick={handleGenerateRandom}
                                disabled={isLoadingRandom || isCreating || isJoining}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '0.5rem',
                                    background: 'transparent',
                                    border: '1px solid var(--secondary)',
                                    borderRadius: '8px',
                                    padding: '0.6rem 1rem',
                                    color: 'var(--secondary)',
                                    cursor: (isLoadingRandom || isCreating || isJoining) ? 'not-allowed' : 'pointer',
                                    opacity: (isLoadingRandom || isCreating || isJoining) ? 0.5 : 1,
                                    fontSize: '0.85rem'
                                }}
                            >
                                <RefreshCw size={14} className={isLoadingRandom ? 'spinning' : ''} />
                                {isLoadingRandom ? 'GENERATING...' : 'REGENERATE ALL'}
                            </button>
                            <button
                                className="text-btn"
                                onClick={() => {
                                    setMode('character');
                                    setRandomCharacters([]);
                                    setSelectedRandomIdx(null);
                                }}
                                disabled={isCreating || isJoining}
                            >
                                Back to custom
                            </button>
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
                            margin: '0 auto 1rem',
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

                        {/* Character Traits Display */}
                        {previewData.traits && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                                style={{
                                    marginBottom: '1rem',
                                    padding: '0.75rem',
                                    background: 'rgba(255,255,255,0.03)',
                                    borderRadius: '8px',
                                    textAlign: 'left',
                                    fontSize: '0.75rem'
                                }}
                            >
                                {previewData.traits.look && (
                                    <div style={{ marginBottom: '0.4rem' }}>
                                        <span style={{ color: '#888', marginRight: '0.5rem' }}>VIBE:</span>
                                        <span style={{ color: '#fff' }}>{previewData.traits.look}</span>
                                    </div>
                                )}
                                {previewData.traits.weapon && (
                                    <div style={{ marginBottom: '0.4rem' }}>
                                        <span style={{ color: '#888', marginRight: '0.5rem' }}>WEAPON:</span>
                                        <span style={{ color: '#ff6b6b' }}>{previewData.traits.weapon}</span>
                                    </div>
                                )}
                                {previewData.traits.talent && (
                                    <div style={{ marginBottom: '0.4rem' }}>
                                        <span style={{ color: '#888', marginRight: '0.5rem' }}>TALENT:</span>
                                        <span style={{ color: '#48dbfb' }}>{previewData.traits.talent}</span>
                                    </div>
                                )}
                                {previewData.traits.flaw && (
                                    <div style={{ marginBottom: '0.4rem' }}>
                                        <span style={{ color: '#888', marginRight: '0.5rem' }}>FLAW:</span>
                                        <span style={{ color: '#feca57' }}>{previewData.traits.flaw}</span>
                                    </div>
                                )}
                                {previewData.traits.catchphrase && (
                                    <div>
                                        <span style={{ color: '#888', marginRight: '0.5rem' }}>SAYS:</span>
                                        <span style={{ color: '#0f0', fontStyle: 'italic' }}>"{previewData.traits.catchphrase}"</span>
                                    </div>
                                )}
                            </motion.div>
                        )}

                        {/* Regenerate button - moved above game code */}
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
                                fontSize: '0.9rem',
                                marginBottom: '1rem',
                                width: '100%'
                            }}
                        >
                            <RefreshCw size={16} className={isRegenerating ? 'spinning' : ''} />
                            {isRegenerating ? 'REGENERATING...' : 'TRY NEW LOOK'}
                        </button>

                        {/* Game code display with copy button */}
                        <GameCodeDisplay code={previewData.gameCode} />

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
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
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
