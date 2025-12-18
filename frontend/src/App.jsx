import React, { useState, useEffect, useRef } from 'react';
import { Lobby } from './components/Lobby';
import { ScenarioView } from './components/ScenarioView';
import { InputView } from './components/InputView';
import { ResultsView } from './components/ResultsView';
import { TrapView } from './components/TrapView';
import { VotingView } from './components/VotingView';
import { CoopVotingView } from './components/CoopVotingView';
import { SacrificeVolunteerView } from './components/SacrificeVolunteerView';
import { SacrificeVotingView } from './components/SacrificeVotingView';
import { SacrificeSubmissionView } from './components/SacrificeSubmissionView';
import { RevivalVotingView } from './components/RevivalVotingView';
import { DebugMenu } from './components/DebugMenu';
import { Copy, Check, RefreshCw, Trophy, Video, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from './api';

// Video waiting card component
const VideoWaitingCard = ({ playerCount }) => (
  <div className="card" style={{
    textAlign: 'center',
    padding: '3rem 2rem',
    background: 'linear-gradient(135deg, rgba(0,255,0,0.05) 0%, rgba(0,100,0,0.1) 100%)',
    border: '2px solid #0f0',
    maxWidth: '500px',
    margin: '0 auto'
  }}>
    <Video size={64} style={{ color: '#0f0', marginBottom: '1.5rem' }} />
    <h2 style={{ color: '#0f0', marginBottom: '1rem', fontFamily: 'monospace' }}>EXTRACTING CONSCIOUSNESS DATA</h2>
    <p style={{ color: 'var(--secondary)', marginBottom: '1.5rem', fontFamily: 'monospace' }}>
      Rendering extraction sequences for {playerCount} user{playerCount > 1 ? 's' : ''}...
    </p>
    <div className="loader" style={{ margin: '0 auto' }}></div>
    <p style={{ color: '#888', fontSize: '0.85rem', marginTop: '1.5rem', fontFamily: 'monospace' }}>
      ETA: 2-4 minutes
    </p>
  </div>
);

// Player video carousel component
const PlayerVideoCarousel = ({ sortedPlayers, playerVideos }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const videoRef = useRef(null);

  // Filter to players who have videos
  const playersWithVideos = sortedPlayers.filter(p => playerVideos[p.id]);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().catch(e => console.log('Autoplay blocked:', e));
    }
  }, [currentIndex]);

  const handleVideoEnd = () => {
    // Auto-advance to next video
    if (currentIndex < playersWithVideos.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  const goToPrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const goToNext = () => {
    if (currentIndex < playersWithVideos.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  if (playersWithVideos.length === 0) {
    return null;
  }

  const currentPlayer = playersWithVideos[currentIndex];
  const isWinner = currentIndex === 0;
  const rankColors = ['#FFD700', '#C0C0C0', '#CD7F32'];
  const rankLabels = ['1st', '2nd', '3rd'];
  const borderColor = rankColors[currentIndex] || 'var(--primary)';

  return (
    <div style={{
      textAlign: 'center',
      padding: '1rem',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      {isWinner && <Trophy size={48} style={{ color: '#FFD700', marginBottom: '1rem' }} />}

      <h2 style={{ color: borderColor, marginBottom: '0.5rem' }}>
        {isWinner ? `${currentPlayer.name} IS THE CHAMPION!` : `${rankLabels[currentIndex] || `${currentIndex + 1}th`} PLACE: ${currentPlayer.name}`}
      </h2>
      <p style={{ color: 'var(--secondary)', marginBottom: '1rem', fontSize: '1.2rem' }}>
        {currentPlayer.score.toLocaleString()} PTS
      </p>

      <video
        ref={videoRef}
        key={currentPlayer.id}
        src={playerVideos[currentPlayer.id]}
        controls
        autoPlay
        playsInline
        onEnded={handleVideoEnd}
        style={{
          width: '100%',
          maxWidth: '720px',
          borderRadius: '12px',
          border: `3px solid ${borderColor}`,
          boxShadow: `0 0 30px ${borderColor}33`
        }}
      />

      {/* Navigation */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '1rem',
        marginTop: '1.5rem'
      }}>
        <button
          onClick={goToPrev}
          disabled={currentIndex === 0}
          style={{
            background: currentIndex === 0 ? '#333' : 'var(--surface)',
            border: '1px solid var(--primary)',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: currentIndex === 0 ? 'not-allowed' : 'pointer',
            opacity: currentIndex === 0 ? 0.5 : 1
          }}
        >
          <ChevronLeft size={24} color="var(--primary)" />
        </button>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {playersWithVideos.map((p, idx) => (
            <button
              key={p.id}
              onClick={() => setCurrentIndex(idx)}
              style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                border: 'none',
                background: idx === currentIndex ? (rankColors[idx] || 'var(--primary)') : '#444',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            />
          ))}
        </div>

        <button
          onClick={goToNext}
          disabled={currentIndex === playersWithVideos.length - 1}
          style={{
            background: currentIndex === playersWithVideos.length - 1 ? '#333' : 'var(--surface)',
            border: '1px solid var(--primary)',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: currentIndex === playersWithVideos.length - 1 ? 'not-allowed' : 'pointer',
            opacity: currentIndex === playersWithVideos.length - 1 ? 0.5 : 1
          }}
        >
          <ChevronRight size={24} color="var(--primary)" />
        </button>
      </div>

      <p style={{ color: '#888', marginTop: '0.75rem', fontSize: '0.9rem' }}>
        Video {currentIndex + 1} of {playersWithVideos.length}
      </p>
    </div>
  );
};

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
  const [showDebugMenu, setShowDebugMenu] = useState(false);

  // Ref to track locally submitted strategy to prevent polling from overwriting it (race condition)
  const pendingStrategyRef = useRef(null);

  // Debug menu keyboard shortcut (Ctrl+Shift+. or Cmd+Shift+.)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === '.') {
        e.preventDefault();
        setShowDebugMenu(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Debug skip handler
  const handleDebugSkip = async (options) => {
    if (!gameCode || !playerId) {
      return { error: 'No active game. Join or create a game first.' };
    }
    return api.debugSkipToState(gameCode, playerId, options);
  };

  // Polling logic - fetches game state immediately and then every 2 seconds
  useEffect(() => {
    if (!gameCode) return;

    const fetchGameState = async () => {
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
    };

    // Fetch immediately when entering the lobby (don't wait for first interval)
    fetchGameState();

    // Then continue polling every 2 seconds
    const interval = setInterval(fetchGameState, 2000);

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

  // Sacrifice round handlers
  const volunteerSacrifice = async () => {
    if (gameCode && playerId) {
      await api.volunteerSacrifice(gameCode, playerId);
    }
  };

  const advanceSacrificeVolunteer = async () => {
    if (gameCode && playerId) {
      await api.advanceSacrificeVolunteer(gameCode, playerId);
    }
  };

  const voteSacrifice = async (targetId) => {
    if (gameCode && playerId) {
      await api.voteSacrifice(gameCode, playerId, targetId);
    }
  };

  const submitSacrificeSpeech = async (speech) => {
    if (gameCode && playerId) {
      await api.submitSacrificeSpeech(gameCode, playerId, speech);
    }
  };

  // Last Stand revival handlers
  const voteRevival = async (targetId) => {
    if (gameCode && playerId) {
      await api.voteRevival(gameCode, playerId, targetId);
    }
  };

  const advanceRevival = async () => {
    if (gameCode && playerId) {
      await api.advanceRevival(gameCode, playerId);
    }
  };

  const nextRound = async () => {
    if (gameCode) {
      await api.nextRound(gameCode);
    }
  };

  // Debug menu component (rendered on all screens)
  const debugMenuComponent = (
    <DebugMenu
      isOpen={showDebugMenu}
      onClose={() => setShowDebugMenu(false)}
      gameCode={gameCode}
      playerId={playerId}
      onSkip={handleDebugSkip}
    />
  );

  // Render Logic
  if (!gameState) {
    return (
      <>
        {debugMenuComponent}
        <Lobby onJoin={handleJoin} onAdmin={setIsAdmin} setPlayerId={setPlayerId} />
      </>
    );
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
      <>
      {debugMenuComponent}
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
        {/* Player cards with character images - only show players who have entered the lobby (or self) */}
        <div style={{ margin: '2rem 0', display: 'flex', gap: '1.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          {Object.values(gameState.players).filter(p => p.in_lobby || p.id === playerId).map(p => {
            const isMe = p.id === playerId;
            const hasImage = !!p.character_image_url;
            const hasDescription = !!p.character_description;

            return (
              <div
                key={p.id}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  padding: '1rem',
                  borderRadius: '12px',
                  background: 'var(--surface)',
                  border: isMe ? '2px solid var(--primary)' : '1px solid #333',
                  minWidth: '140px',
                  maxWidth: '160px'
                }}
              >
                {/* Character image or placeholder */}
                <div style={{
                  width: '100px',
                  height: '100px',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  marginBottom: '0.75rem',
                  background: '#1a1a1a',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {hasImage ? (
                    <img
                      src={p.character_image_url}
                      alt={`${p.name}'s character`}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : hasDescription ? (
                    <div style={{ textAlign: 'center' }}>
                      <span className="spinner" style={{ width: '24px', height: '24px' }}></span>
                      <div style={{ fontSize: '0.7rem', color: '#666', marginTop: '0.5rem' }}>Generating...</div>
                    </div>
                  ) : (
                    <div style={{ fontSize: '2.5rem', opacity: 0.3 }}>?</div>
                  )}
                </div>

                {/* Player name */}
                <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                  {p.name}
                </div>
                {p.is_admin && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--primary)' }}>HOST</div>
                )}
              </div>
            );
          })}
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
      </>
    );
  }

  // Game finished - show final results with player videos
  if (gameState.status === 'finished') {
    const sortedPlayers = Object.values(gameState.players).sort((a, b) => b.score - a.score);
    const winner = sortedPlayers[0];
    const videoStatus = gameState.videos_status || 'pending';
    const playerVideos = gameState.player_videos || {};
    const hasAnyVideos = Object.keys(playerVideos).length > 0;

    const handleRetryVideos = async () => {
      if (gameCode) {
        await api.retryPlayerVideos(gameCode);
      }
    };

    return (
      <>
      {debugMenuComponent}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2rem', padding: '2rem' }}>
        <h1 className="glitch-text" style={{ fontSize: '3rem', textAlign: 'center' }}>EXIT PROTOCOL COMPLETE</h1>
        <p style={{ fontFamily: 'monospace', color: '#0f0', textAlign: 'center', marginTop: '-1rem' }}>
          &gt; SIMULATION TERMINATED // CONSCIOUSNESS EXTRACTION IN PROGRESS
        </p>

        {/* Video section - show based on status */}
        {(videoStatus === 'generating' || videoStatus === 'pending') && (
          <VideoWaitingCard playerCount={sortedPlayers.length} />
        )}

        {videoStatus === 'ready' && hasAnyVideos && (
          <PlayerVideoCarousel sortedPlayers={sortedPlayers} playerVideos={playerVideos} />
        )}

        {videoStatus === 'failed' && (
          <div className="card" style={{ textAlign: 'center', padding: '2rem', border: '2px solid #ff4444', maxWidth: '500px' }}>
            <h2 style={{ color: '#ff4444', marginBottom: '1rem' }}>VIDEO GENERATION FAILED</h2>
            <p style={{ color: 'var(--secondary)', marginBottom: '1.5rem' }}>
              The AI couldn't create the player videos. You can try again.
            </p>
            <button
              className="primary"
              onClick={handleRetryVideos}
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: '0 auto' }}
            >
              <RefreshCw size={18} />
              RETRY VIDEOS
            </button>
          </div>
        )}

        {/* Winner card - show if videos not ready yet */}
        {(videoStatus !== 'ready' || !hasAnyVideos) && (
          <div className="card" style={{ textAlign: 'center', padding: '2rem', border: '2px solid #FFD700' }}>
            <h2 style={{ color: '#FFD700', marginBottom: '1rem', fontFamily: 'monospace' }}>PRIMARY SURVIVOR</h2>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--primary)' }}>{winner?.name}</div>
            <div style={{ fontSize: '1.5rem', color: '#FFD700', marginTop: '0.5rem' }}>{winner?.score.toLocaleString()} INTEGRITY PTS</div>
            <p style={{ fontFamily: 'monospace', color: '#0f0', marginTop: '1rem', fontSize: '0.9rem' }}>
              CONSCIOUSNESS EXTRACTED SUCCESSFULLY
            </p>
          </div>
        )}

        <div className="card" style={{ width: '100%', maxWidth: '500px', padding: '1.5rem' }}>
          <h3 style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'var(--primary)', fontFamily: 'monospace' }}>EXTRACTION LOG</h3>
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
          RE-ENTER SIMULATION
        </button>
      </div>
      </>
    );
  }

  // Game Loop
  if (gameState.status === 'playing' && currentRound) {
    // If dead, show ResultsView but maybe specialized spectator mode?
    // For MVP transparency, results view is good or Spectator Scenario View.
    const isDead = player && !player.is_alive;

    // Header (includes debug menu)
    const header = (
      <>
        {debugMenuComponent}
        <GameHeader
          currentRound={currentRound.number}
          maxRounds={gameState.max_rounds}
          score={player ? player.score : 0}
          playerName={player ? player.name : 'PLAYER'}
        />
      </>
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
            <div style={{ marginTop: '2rem', color: 'var(--secondary)', fontFamily: 'monospace' }}>
              {isDead ? "&gt; STATUS: TERMINATED // OBSERVING OTHER USERS..." : "&gt; PROTOCOL UPLOADED // AWAITING SYSTEM EVALUATION..."}
            </div>
          </div>
        );
      }
      return (
        <>
          {header}
          <ScenarioView round={currentRound} isSpectating={false} flatBottom={true} />
          <InputView round={currentRound} playerId={playerId} onSubmit={submitStrategy} flatTop={true} config={gameState.config} />
        </>
      );
    }

    if (currentRound.status === 'judgement') {
      return (
        <div className="card" style={{ textAlign: 'center' }}>
          {header}
          <h2 className="glitch-text">EVALUATING...</h2>
          <p style={{ fontFamily: 'monospace', color: 'var(--secondary)' }}>
            &gt; PROCESSING SURVIVAL PROTOCOLS...
          </p>
          <span className="loader"></span>
        </div>
      );
    }

    if (currentRound.status === 'ranked_judgement') {
      return (
        <div className="card" style={{ textAlign: 'center' }}>
          {header}
          <h2 className="glitch-text" style={{ color: '#ffd700' }}>RANKING PROTOCOLS...</h2>
          <p style={{ fontFamily: 'monospace', color: 'var(--secondary)' }}>
            &gt; COMPARING ALL SURVIVAL STRATEGIES...
          </p>
          <span className="loader"></span>
        </div>
      );
    }

    if (currentRound.status === 'trap_creation') {
      return (
        <>
          {header}
          <TrapView round={currentRound} playerId={playerId} onSubmit={submitTrap} config={gameState.config} />
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
          <h2 className="glitch-text">SYNC EVALUATION...</h2>
          <p style={{ fontFamily: 'monospace', color: 'var(--secondary)' }}>
            &gt; ANALYZING COLLECTIVE PROTOCOL...
          </p>
          <span className="loader"></span>
        </div>
      );
    }

    // Sacrifice round statuses
    if (currentRound.status === 'sacrifice_volunteer') {
      return (
        <>
          {header}
          <SacrificeVolunteerView
            round={currentRound}
            playerId={playerId}
            players={gameState.players}
            isAdmin={isAdmin}
            onVolunteer={volunteerSacrifice}
            onAdvance={advanceSacrificeVolunteer}
            config={gameState.config}
          />
        </>
      );
    }

    if (currentRound.status === 'sacrifice_voting') {
      return (
        <>
          {header}
          <SacrificeVotingView
            round={currentRound}
            playerId={playerId}
            players={gameState.players}
            onVote={voteSacrifice}
          />
        </>
      );
    }

    if (currentRound.status === 'sacrifice_submission') {
      return (
        <>
          {header}
          <SacrificeSubmissionView
            round={currentRound}
            playerId={playerId}
            players={gameState.players}
            onSubmit={submitSacrificeSpeech}
            config={gameState.config}
          />
        </>
      );
    }

    if (currentRound.status === 'sacrifice_judgement') {
      return (
        <div className="card" style={{ textAlign: 'center' }}>
          {header}
          <h2 className="glitch-text" style={{ color: '#ffd700' }}>EVALUATING SACRIFICE...</h2>
          <p style={{ fontFamily: 'monospace', color: 'var(--secondary)' }}>
            &gt; DETERMINING IF DEATH WAS EPIC ENOUGH...
          </p>
          <span className="loader"></span>
        </div>
      );
    }

    // Last Stand revival statuses
    if (currentRound.status === 'last_stand_revival') {
      return (
        <>
          {header}
          <RevivalVotingView
            round={currentRound}
            playerId={playerId}
            players={gameState.players}
            isAdmin={isAdmin}
            onVote={voteRevival}
            onAdvance={advanceRevival}
          />
        </>
      );
    }

    if (currentRound.status === 'revival_judgement') {
      return (
        <div className="card" style={{ textAlign: 'center' }}>
          {header}
          <h2 className="glitch-text" style={{ color: '#0f0' }}>REVIVAL IN PROGRESS...</h2>
          <p style={{ fontFamily: 'monospace', color: 'var(--secondary)' }}>
            &gt; RE-EVALUATING WITH TEAMWORK BONUS...
          </p>
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

  return (
    <>
      <DebugMenu
        isOpen={showDebugMenu}
        onClose={() => setShowDebugMenu(false)}
        gameCode={gameCode}
        playerId={playerId}
        onSkip={handleDebugSkip}
      />
      <div>Unknown State</div>
    </>
  );
}

export default App;
