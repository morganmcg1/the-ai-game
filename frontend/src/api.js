// Relative paths for unified FastAPI deployment
const getUrl = (funcName) => `/api/${funcName}`;

// Custom error class for API errors
export class ApiError extends Error {
    constructor(message, status, detail) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.detail = detail;
    }
}

// Helper function to handle fetch responses with proper error checking
async function fetchJson(url, options = {}) {
    const res = await fetch(url, options);
    
    // Try to parse response as JSON
    let data;
    const contentType = res.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
        try {
            data = await res.json();
        } catch (e) {
            // JSON parse failed
            if (!res.ok) {
                throw new ApiError(`HTTP ${res.status}: ${res.statusText}`, res.status, res.statusText);
            }
            throw new ApiError('Invalid JSON response from server', res.status, 'parse_error');
        }
    } else {
        // Non-JSON response
        const text = await res.text();
        if (!res.ok) {
            throw new ApiError(`HTTP ${res.status}: ${text || res.statusText}`, res.status, text || res.statusText);
        }
        // Return text as-is for non-JSON successful responses (rare)
        return { text };
    }
    
    // Check for HTTP errors
    if (!res.ok) {
        const detail = data?.detail || data?.message || res.statusText;
        throw new ApiError(`HTTP ${res.status}: ${detail}`, res.status, detail);
    }
    
    return data;
}

export const api = {
    createGame: async () => {
        return fetchJson(getUrl("create_game"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
        });
    },

    joinGame: async (code, name, characterDescription = null, characterImageUrl = null) => {
        const body = { name };
        if (characterDescription) {
            body.character_description = characterDescription;
        }
        if (characterImageUrl) {
            body.character_image_url = characterImageUrl;
        }
        return fetchJson(`${getUrl("join_game")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
    },

    startGame: async (code) => {
        return fetchJson(`${getUrl("start_game")}?code=${code}`, { method: "POST" });
    },

    getGameState: async (code, playerId = null) => {
        // GET request, code as query param
        let url = `${getUrl("get_game_state")}?code=${code}`;
        if (playerId) {
            url += `&player_id=${playerId}`;
        }
        return fetchJson(url);
    },

    submitStrategy: async (code, playerId, strategy) => {
        return fetchJson(`${getUrl("submit_strategy")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId, strategy }),
        });
    },

    submitTrap: async (code, playerId, trapText) => {
        return fetchJson(`${getUrl("submit_trap")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId, trap_text: trapText }),
        });
    },

    voteTrap: async (code, voterId, targetId) => {
        return fetchJson(`${getUrl("vote_trap")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ voter_id: voterId, target_id: targetId }),
        });
    },

    voteCoop: async (code, voterId, targetId) => {
        return fetchJson(`${getUrl("vote_coop")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ voter_id: voterId, target_id: targetId }),
        });
    },

    nextRound: async (code) => {
        return fetchJson(`${getUrl("next_round")}?code=${code}`, { method: "POST" });
    },

    retryPlayerVideos: async (code) => {
        return fetchJson(`${getUrl("retry_player_videos")}?code=${code}`, { method: "POST" });
    },

    regenerateCharacterImage: async (code, playerId) => {
        return fetchJson(`${getUrl("regenerate_character_image")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId }),
        });
    },

    enterLobby: async (code, playerId) => {
        return fetchJson(`${getUrl("enter_lobby")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId }),
        });
    },

    // Sacrifice round APIs
    volunteerSacrifice: async (code, playerId) => {
        return fetchJson(`${getUrl("volunteer_sacrifice")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId }),
        });
    },

    advanceSacrificeVolunteer: async (code, playerId) => {
        return fetchJson(`${getUrl("advance_sacrifice_volunteer")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId }),
        });
    },

    voteSacrifice: async (code, voterId, targetId) => {
        return fetchJson(`${getUrl("vote_sacrifice")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ voter_id: voterId, target_id: targetId }),
        });
    },

    submitSacrificeSpeech: async (code, playerId, speech) => {
        return fetchJson(`${getUrl("submit_sacrifice_speech")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId, speech }),
        });
    },

    // Last Stand revival APIs
    voteRevival: async (code, voterId, targetId) => {
        return fetchJson(`${getUrl("vote_revival")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ voter_id: voterId, target_id: targetId }),
        });
    },

    advanceRevival: async (code, playerId) => {
        return fetchJson(`${getUrl("advance_revival")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId }),
        });
    },

    generateRandomCharacters: async () => {
        return fetchJson(getUrl("generate_random_characters"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({}),
        });
    },

    // Debug API - skip to specific game state
    debugSkipToState: async (code, playerId, options) => {
        return fetchJson(`${getUrl("debug_skip_to_state")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                player_id: playerId,
                ...options,
            }),
        });
    },

    // Get game configuration
    getConfig: async () => {
        return fetchJson(getUrl("config"));
    }
};
