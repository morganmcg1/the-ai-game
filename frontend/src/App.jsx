import React, { useState, useEffect, useRef } from 'react';
import { Lobby } from './components/Lobby';
import { ScenarioView } from './components/ScenarioView';
import { InputView } from './components/InputView';
import { ResultsView } from './components/ResultsView';
import { TrapView } from './components/TrapView';
import { VotingView } from './components/VotingView';
import { CoopVotingView } from './components/CoopVotingView';
import { Copy, Check } from 'lucide-react';
import { api } from './api';

const GameHeader = ({ currentRound, maxRounds, score, playerName }) => {
  const progress = (currentRound / maxRounds) * 100;

  return (
    <div className="game-header">
      <div className="health-bar-container">
        <span className="health-bar-label">ROUND {currentRound}/{maxRounds}</span>
        <div className="health-bar-frame">
          <div className="health-bar-fill" style={{ width: `${progress}%` }}></div>
        </div>
      </div>

      <div className="score-container">
        <span className="score-label">{playerName || 'PLAYER'}</span>
        <div className="score-value">{score.toLocaleString()}</div>
      </div>
    </div>
  );
};

function App() {
  const [gameState, setGameState] = useState(null);
  const [playerId, setPlayerId] = useState(null);
  const [gameCode, setGameCode] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  // Ref to track locally submitted strategy to prevent polling from overwriting it (race condition)
  const pendingStrategyRef = useRef(null);

  // Polling logic
  useEffect(() => {
    if (!gameCode) return;

    const interval = setInterval(async () => {
      try {
        const state = await api.getGameState(gameCode, playerId);
        if (state && !state.error) {
          setGameState(prevState => {
            // Check if we have a pending strategy that the server hasn't reflected yet
            if (pendingStrategyRef.current &&
              pendingStrategyRef.current.roundIdx === state.current_round_idx &&
              playerId &&
              state.players[playerId] &&
              !state.players[playerId].strategy) {

              console.log("Polling: Injecting pending strategy locally");
              // Inject our local strategy into the server state for UI consistency
              const newState = { ...state };
              newState.players[playerId] = {
                ...state.players[playerId],
                strategy: pendingStrategyRef.current.strategy
              };
              return newState;
            }

            // If server has confirmed the strategy, clear our pending ref
            if (playerId && state.players[playerId] && state.players[playerId].strategy) {
              // Determine if it matches what we sent to be safe, or just clear it
              if (pendingStrategyRef.current) console.log("Polling: Server confirmed strategy, clearing pending ref");
              pendingStrategyRef.current = null;
            }

            return state;
          });
        }
      } catch (e) {
        console.error("Polling error", e);
      }
    }, 2000); // 2 second poll

    return () => clearInterval(interval);
  }, [gameCode, playerId]);

  const handleJoin = (code, pid, name) => {
    setGameCode(code);
    setPlayerId(pid);
  };

  const startGame = async () => {
    if (gameCode) {
      await api.startGame(gameCode);
    }
  };

  const submitStrategy = async (strategy) => {
    console.log("Submit Strategy called with:", strategy);
    if (gameCode && playerId) {
      if (gameState) {
        pendingStrategyRef.current = {
          roundIdx: gameState.current_round_idx,
          strategy: strategy
        };
        console.log("Pending Strategy Ref set:", pendingStrategyRef.current);
      }

      // Optimistic update to prevent flicker before poll
      setGameState(prev => {
        if (!prev) return prev;
        const newPlayers = { ...prev.players };
        if (newPlayers[playerId]) {
          newPlayers[playerId] = { ...newPlayers[playerId], strategy: strategy };
        }
        return { ...prev, players: newPlayers };
      });

      try {
        const res = await api.submitStrategy(gameCode, playerId, strategy);
        console.log("API Submit Strategy Result:", res);
        if (res && (res.error || res.detail)) {
          alert("Error submitting strategy: " + (res.error || res.detail));
        } else if (!res) {
          console.error("API returned null response");
          alert("Error: Server returned empty response.");
        }
      } catch (e) {
        console.error("API Submit Exception:", e);
        alert("Failed to submit: " + e.message);
      }
    }
  };

  const submitTrap = async (trapText) => {
    if (gameCode && playerId) {
      await api.submitTrap(gameCode, playerId, trapText);
    }
  };

  const voteTrap = async (targetId) => {
    if (gameCode && playerId) {
      await api.voteTrap(gameCode, playerId, targetId);
    }
  };

  const voteCoop = async (targetId) => {
    if (gameCode && playerId) {
      await api.voteCoop(gameCode, playerId, targetId);
    }
  };

  const nextRound = async () => {
    if (gameCode) {
      await api.nextRound(gameCode);
    }
  };

  // Render Logic
  if (!gameState) {
    return <Lobby onJoin={handleJoin} onAdmin={setIsAdmin} setPlayerId={setPlayerId} />;
  }

  const currentRound = gameState.rounds[gameState.current_round_idx];
  const player = gameState.players[playerId];

  if (gameState.status === 'lobby') {
    const hostPlayer = Object.values(gameState.players).find(p => p.is_admin);
    const hostName = hostPlayer?.name || 'host';

    const copyCode = async () => {
      try {
        await navigator.clipboard.writeText(gameCode);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (e) {
        console.error('Failed to copy:', e);
      }
    };

    return (
      <div className="card" style={{ textAlign: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
          <h2 style={{ margin: 0 }}>LOBBY: {gameCode}</h2>
          <button
            onClick={copyCode}
            style={{
              background: 'transparent',
              border: '1px solid var(--secondary)',
              borderRadius: '6px',
              padding: '6px 8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              color: copied ? 'var(--success)' : 'var(--secondary)'
            }}
            title="Copy game code"
          >
            {copied ? <Check size={16} /> : <Copy size={16} />}
          </button>
        </div>
        <p style={{ color: 'var(--secondary)', fontSize: '0.9rem', marginTop: '0.5rem', opacity: 0.8 }}>waiting for players to join...</p>
        <div style={{ margin: '2rem 0', display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          {Object.values(gameState.players).map(p => (
            <div key={p.id} style={{ padding: '8px 16px', borderRadius: '20px', background: 'var(--surface)', border: '1px solid var(--primary)' }}>
              {p.name} {p.is_admin ? '(HOST)' : ''}
            </div>
          ))}
        </div>

        {isAdmin ? (
          <button
            className="primary"
            onClick={async () => {
              setLoading(true);
              try {
                const res = await api.startGame(gameCode);
                console.log("Start Game Response:", res);
                if (res.error || res.detail) {
                  alert("Error starting game: " + (res.error || res.detail));
                  setLoading(false);
                }
              }
              catch (e) {
                console.error(e);
                alert("Exception starting game: " + e.message);
                setLoading(false);
              }
            }}
            disabled={loading}
          >
            {loading ? <span className="spinner"></span> : null}
            {loading ? "STARTING..." : "START GAME"}
          </button>
        ) : (
          <p style={{ color: 'var(--secondary)', opacity: 0.8 }}>Waiting for {hostName} to start the game...</p>
        )}
      </div>
    );
  }

  // Game finished - show final results
  if (gameState.status === 'finished') {
    const sortedPlayers = Object.values(gameState.players).sort((a, b) => b.score - a.score);
    const winner = sortedPlayers[0];

    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2rem', padding: '2rem' }}>
        <h1 className="glitch-text" style={{ fontSize: '3rem', textAlign: 'center' }}>GAME OVER</h1>

        <div className="card" style={{ textAlign: 'center', padding: '2rem', border: '2px solid #FFD700' }}>
          <h2 style={{ color: '#FFD700', marginBottom: '1rem' }}>WINNER</h2>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--primary)' }}>{winner?.name}</div>
          <div style={{ fontSize: '1.5rem', color: '#FFD700', marginTop: '0.5rem' }}>{winner?.score.toLocaleString()} PTS</div>
        </div>

        <div className="card" style={{ width: '100%', maxWidth: '500px', padding: '1.5rem' }}>
          <h3 style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'var(--primary)' }}>FINAL STANDINGS</h3>
          {sortedPlayers.map((p, index) => {
            const rankColors = ['#FFD700', '#C0C0C0', '#CD7F32'];
            const rankLabels = ['1st', '2nd', '3rd'];
            return (
              <div
                key={p.id}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.75rem 1rem',
                  borderBottom: index < sortedPlayers.length - 1 ? '1px solid #333' : 'none',
                  background: index === 0 ? 'rgba(255, 215, 0, 0.1)' : 'transparent'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span style={{ color: rankColors[index] || '#888', fontWeight: 'bold', minWidth: '40px' }}>
                    {rankLabels[index] || `${index + 1}th`}
                  </span>
                  <span style={{ color: '#fff' }}>{p.name}</span>
                </div>
                <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>
                  {p.score.toLocaleString()} PTS
                </span>
              </div>
            );
          })}
        </div>

        <button className="primary" onClick={() => window.location.reload()}>
          PLAY AGAIN
        </button>
      </div>
    );
  }

  // Game Loop
  if (gameState.status === 'playing' && currentRound) {
    // If dead, show ResultsView but maybe specialized spectator mode?
    // For MVP transparency, results view is good or Spectator Scenario View.
    const isDead = player && !player.is_alive;

    // Header
    const header = (
      <GameHeader
        currentRound={currentRound.number}
        maxRounds={gameState.max_rounds}
        score={player ? player.score : 0}
        playerName={player ? player.name : 'PLAYER'}
      />
    );

    if (currentRound.status === 'scenario') {
      // Transitioning... (Backend might skip this state fast)
      return (
        <>
          {header}
          <ScenarioView round={currentRound} isSpectating={isDead} />
        </>
      );
    }

    if (currentRound.status === 'strategy') {
      // If submitted, show waiting.
      const myStrategy = player?.strategy;
      if (myStrategy || isDead) {
        return (
          <div style={{ textAlign: 'center' }}>
            {header}
            <ScenarioView round={currentRound} isSpectating={true} />
            <div style={{ marginTop: '2rem', color: 'var(--secondary)' }}>
              {isDead ? "YOU ARE DEAD. WITNESS THE CARNAGE." : "STRATEGY UPLOADED. AWAITING JUDGEMENT."}
            </div>
          </div>
        );
      }
      return (
        <>
          {header}
          <ScenarioView round={currentRound} isSpectating={false} />
          <InputView round={currentRound} playerId={playerId} onSubmit={submitStrategy} />
        </>
      );
    }

    if (currentRound.status === 'judgement') {
      return (
        <div className="card" style={{ textAlign: 'center' }}>
          {header}
          <h2 className="glitch-text">JUDGING...</h2>
          <p>The AI is deciding your fate.</p>
          <span className="loader"></span>
        </div>
      );
    }

    if (currentRound.status === 'trap_creation') {
      return (
        <>
          {header}
          <TrapView round={currentRound} playerId={playerId} onSubmit={submitTrap} />
        </>
      );
    }

    if (currentRound.status === 'trap_voting') {
      return (
        <>
          {header}
          <VotingView round={currentRound} playerId={playerId} onVote={voteTrap} />
        </>
      );
    }

    if (currentRound.status === 'coop_voting') {
      return (
        <>
          {header}
          <CoopVotingView
            round={currentRound}
            playerId={playerId}
            onVote={voteCoop}
            players={gameState.players}
          />
        </>
      );
    }

    if (currentRound.status === 'coop_judgement') {
      return (
        <div className="card" style={{ textAlign: 'center' }}>
          {header}
          <h2 className="glitch-text">TEAM JUDGEMENT...</h2>
          <p style={{ color: 'var(--secondary)' }}>The AI is judging your collective fate.</p>
          <span className="loader"></span>
        </div>
      );
    }

    if (currentRound.status === 'results') {
      const isFinalRound = currentRound.number >= gameState.max_rounds;
      return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2rem' }}>
          {header}
          <ResultsView round={currentRound} players={gameState.players} />
          {isAdmin && (
            <button className="primary" onClick={nextRound}>
              {isFinalRound ? 'END GAME' : 'NEXT ROUND'}
            </button>
          )}
        </div>
      );
    }
  }

  return <div>Unknown State</div>;
}

export default App;
