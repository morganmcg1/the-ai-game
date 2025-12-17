import React, { useState } from 'react';
import { X, Bug, Play, SkipForward, Users } from 'lucide-react';

// Dummy placeholder image as data URI (dark gray box with question mark)
const DUMMY_CHARACTER_IMAGE = 'data:image/svg+xml;base64,' + btoa(`
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#1a1a1a"/>
  <text x="50" y="60" font-family="monospace" font-size="40" fill="#666" text-anchor="middle">?</text>
</svg>
`);

// Round types and their starting statuses
const ROUND_TYPES = [
  { type: 'survival', label: 'Survival', statuses: ['scenario', 'strategy', 'judgement', 'results'] },
  { type: 'blind_architect', label: 'Blind Architect', statuses: ['trap_creation', 'trap_voting', 'strategy', 'judgement', 'results'] },
  { type: 'cooperative', label: 'Cooperative', statuses: ['scenario', 'strategy', 'coop_voting', 'coop_judgement', 'results'] },
  { type: 'sacrifice', label: 'Sacrifice', statuses: ['sacrifice_volunteer', 'sacrifice_voting', 'sacrifice_submission', 'sacrifice_judgement', 'results'] },
  { type: 'last_stand', label: 'Last Stand', statuses: ['scenario', 'strategy', 'judgement', 'last_stand_revival', 'revival_judgement', 'results'] },
  { type: 'ranked', label: 'Ranked', statuses: ['scenario', 'strategy', 'ranked_judgement', 'results'] },
];

// Game states
const GAME_STATES = [
  { status: 'lobby', label: 'Lobby' },
  { status: 'playing', label: 'Playing' },
  { status: 'finished', label: 'Finished' },
];

export const DebugMenu = ({ isOpen, onClose, gameCode, playerId, onSkip }) => {
  const [selectedGameStatus, setSelectedGameStatus] = useState('playing');
  const [selectedRoundType, setSelectedRoundType] = useState('survival');
  const [selectedRoundStatus, setSelectedRoundStatus] = useState('scenario');
  const [roundNumber, setRoundNumber] = useState(1);
  const [numDummyPlayers, setNumDummyPlayers] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const currentRoundType = ROUND_TYPES.find(r => r.type === selectedRoundType);

  const handleSkip = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await onSkip({
        game_status: selectedGameStatus,
        round_type: selectedRoundType,
        round_status: selectedRoundStatus,
        round_number: roundNumber,
        num_dummy_players: numDummyPlayers,
        dummy_character_image: DUMMY_CHARACTER_IMAGE,
      });

      if (result.error) {
        setError(result.error);
      } else {
        onClose();
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.9)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 10000,
    }}>
      <div style={{
        background: '#111',
        border: '2px solid #f0f',
        borderRadius: '12px',
        padding: '2rem',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '90vh',
        overflowY: 'auto',
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Bug size={24} color="#f0f" />
            <h2 style={{ margin: 0, color: '#f0f', fontFamily: 'monospace' }}>DEBUG MENU</h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              padding: '4px',
            }}
          >
            <X size={24} color="#888" />
          </button>
        </div>

        {/* Game Code Display */}
        {gameCode && (
          <div style={{ marginBottom: '1rem', padding: '0.5rem', background: '#1a1a1a', borderRadius: '6px' }}>
            <span style={{ color: '#888', fontSize: '0.8rem' }}>Game: </span>
            <span style={{ color: '#0f0', fontFamily: 'monospace' }}>{gameCode}</span>
          </div>
        )}

        {/* Game Status */}
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: '#888', fontSize: '0.9rem' }}>
            Game Status
          </label>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {GAME_STATES.map(gs => (
              <button
                key={gs.status}
                onClick={() => setSelectedGameStatus(gs.status)}
                style={{
                  padding: '0.5rem 1rem',
                  background: selectedGameStatus === gs.status ? '#f0f' : '#222',
                  color: selectedGameStatus === gs.status ? '#000' : '#fff',
                  border: '1px solid #f0f',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontFamily: 'monospace',
                  fontSize: '0.85rem',
                }}
              >
                {gs.label}
              </button>
            ))}
          </div>
        </div>

        {/* Only show round options if game status is 'playing' */}
        {selectedGameStatus === 'playing' && (
          <>
            {/* Round Type */}
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#888', fontSize: '0.9rem' }}>
                Round Type
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {ROUND_TYPES.map(rt => (
                  <button
                    key={rt.type}
                    onClick={() => {
                      setSelectedRoundType(rt.type);
                      setSelectedRoundStatus(rt.statuses[0]);
                    }}
                    style={{
                      padding: '0.5rem 0.75rem',
                      background: selectedRoundType === rt.type ? '#0ff' : '#222',
                      color: selectedRoundType === rt.type ? '#000' : '#fff',
                      border: '1px solid #0ff',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontFamily: 'monospace',
                      fontSize: '0.8rem',
                    }}
                  >
                    {rt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Round Status */}
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#888', fontSize: '0.9rem' }}>
                Round Status
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {currentRoundType?.statuses.map(status => (
                  <button
                    key={status}
                    onClick={() => setSelectedRoundStatus(status)}
                    style={{
                      padding: '0.5rem 0.75rem',
                      background: selectedRoundStatus === status ? '#0f0' : '#222',
                      color: selectedRoundStatus === status ? '#000' : '#fff',
                      border: '1px solid #0f0',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontFamily: 'monospace',
                      fontSize: '0.8rem',
                    }}
                  >
                    {status.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            </div>

            {/* Round Number */}
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#888', fontSize: '0.9rem' }}>
                Round Number
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={roundNumber}
                onChange={(e) => setRoundNumber(parseInt(e.target.value) || 1)}
                style={{
                  padding: '0.5rem',
                  background: '#222',
                  color: '#fff',
                  border: '1px solid #444',
                  borderRadius: '6px',
                  width: '80px',
                  fontFamily: 'monospace',
                }}
              />
            </div>
          </>
        )}

        {/* Dummy Players */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: '#888', fontSize: '0.9rem' }}>
            <Users size={16} />
            Add Dummy Players
          </label>
          <input
            type="number"
            min="0"
            max="10"
            value={numDummyPlayers}
            onChange={(e) => setNumDummyPlayers(parseInt(e.target.value) || 0)}
            style={{
              padding: '0.5rem',
              background: '#222',
              color: '#fff',
              border: '1px solid #444',
              borderRadius: '6px',
              width: '80px',
              fontFamily: 'monospace',
            }}
          />
          <span style={{ marginLeft: '0.5rem', color: '#666', fontSize: '0.8rem' }}>
            (Uses placeholder avatars)
          </span>
        </div>

        {/* Error Display */}
        {error && (
          <div style={{
            marginBottom: '1rem',
            padding: '0.75rem',
            background: 'rgba(255,0,0,0.1)',
            border: '1px solid #f00',
            borderRadius: '6px',
            color: '#f88',
            fontSize: '0.85rem',
          }}>
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#333',
              color: '#fff',
              border: '1px solid #555',
              borderRadius: '6px',
              cursor: 'pointer',
              fontFamily: 'monospace',
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSkip}
            disabled={isLoading || !gameCode}
            style={{
              padding: '0.75rem 1.5rem',
              background: isLoading ? '#555' : '#f0f',
              color: '#000',
              border: 'none',
              borderRadius: '6px',
              cursor: isLoading || !gameCode ? 'not-allowed' : 'pointer',
              fontFamily: 'monospace',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            {isLoading ? (
              <>
                <span className="spinner" style={{ width: '16px', height: '16px' }}></span>
                Skipping...
              </>
            ) : (
              <>
                <SkipForward size={18} />
                Skip To State
              </>
            )}
          </button>
        </div>

        {/* Help Text */}
        <div style={{
          marginTop: '1.5rem',
          padding: '0.75rem',
          background: '#1a1a1a',
          borderRadius: '6px',
          fontSize: '0.8rem',
          color: '#666',
        }}>
          <p style={{ margin: '0 0 0.5rem 0' }}>
            <strong style={{ color: '#888' }}>Keyboard Shortcut:</strong> Ctrl+Shift+D (or Cmd+Shift+D on Mac)
          </p>
          <p style={{ margin: 0 }}>
            This menu sets up the game state with dummy data so you can test specific screens without playing through the whole game.
          </p>
        </div>
      </div>
    </div>
  );
};
