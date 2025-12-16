import React, { useState, useEffect } from 'react';
import { Lobby } from './components/Lobby';
import { ScenarioView } from './components/ScenarioView';
import { InputView } from './components/InputView';
import { ResultsView } from './components/ResultsView';
import { TrapView } from './components/TrapView';
import { VotingView } from './components/VotingView';
import { api } from './api';

function App() {
  const [gameState, setGameState] = useState(null);
  const [playerId, setPlayerId] = useState(null);
  const [gameCode, setGameCode] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(false);

  // Polling logic
  useEffect(() => {
    if (!gameCode) return;

    const interval = setInterval(async () => {
      try {
        const state = await api.getGameState(gameCode);
        if (state && !state.error) {
          setGameState(state);
        }
      } catch (e) {
        console.error("Polling error", e);
      }
    }, 2000); // 2 second poll

    return () => clearInterval(interval);
  }, [gameCode]);

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
    if (gameCode && playerId) {
      await api.submitStrategy(gameCode, playerId, strategy);
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
    return (
      <div className="card" style={{ textAlign: 'center' }}>
        <h2>LOBBY: {gameCode}</h2>
        <div style={{ margin: '2rem 0', display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          {Object.values(gameState.players).map(p => (
            <div key={p.id} style={{ padding: '8px 16px', borderRadius: '20px', background: 'var(--surface)', border: '1px solid var(--primary)' }}>
              {p.name} {p.is_admin ? '(HOST)' : ''}
            </div>
          ))}
        </div>

        {isAdmin ? (
          <button className="primary" onClick={startGame}>START GAME</button>
        ) : (
          <p className="loader">Waiting for host to start...</p>
        )}
      </div>
    );
  }

  // Game Loop
  if (gameState.status === 'playing' && currentRound) {
    // If dead, show ResultsView but maybe specialized spectator mode?
    // For MVP transparency, results view is good or Spectator Scenario View.
    const isDead = player && !player.is_alive;

    if (currentRound.status === 'scenario') {
      // Transitioning... (Backend might skip this state fast)
      return <ScenarioView round={currentRound} isSpectating={isDead} />;
    }

    if (currentRound.status === 'strategy') {
      // If submitted, show waiting.
      const myStrategy = player?.strategy;
      if (myStrategy || isDead) {
        return (
          <div style={{ textAlign: 'center' }}>
            <ScenarioView round={currentRound} isSpectating={true} />
            <div style={{ marginTop: '2rem', color: 'var(--secondary)' }}>
              {isDead ? "YOU ARE DEAD. WITNESS THE CARNAGE." : "STRATEGY UPLOADED. AWAITING JUDGEMENT."}
            </div>
          </div>
        );
      }
      return (
        <>
          <ScenarioView round={currentRound} isSpectating={false} />
          <InputView round={currentRound} playerId={playerId} onSubmit={submitStrategy} />
        </>
      );
    }

    if (currentRound.status === 'judgement') {
      return (
        <div className="card" style={{ textAlign: 'center' }}>
          <h2 className="glitch-text">JUDGING...</h2>
          <p>The AI is deciding your fate.</p>
          <span className="loader"></span>
        </div>
      );
    }

    if (currentRound.status === 'trap_creation') {
      return <TrapView round={currentRound} playerId={playerId} onSubmit={submitTrap} />;
    }

    if (currentRound.status === 'trap_voting') {
      return <VotingView round={currentRound} playerId={playerId} onVote={voteTrap} />;
    }

    if (currentRound.status === 'results') {
      // Next round button for admin?
      // Logic for next round needs to be added to backend & frontend call if not auto.
      // For MVP we might stick on results. I should add a "Next Round" button for Admin.
      return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2rem' }}>
          <ResultsView round={currentRound} players={gameState.players} />
          {isAdmin && (
            <button className="primary" onClick={nextRound}>
              NEXT ROUND
            </button>
          )}
        </div>
      );
    }
  }

  return <div>Unknown State</div>;
}

export default App;
