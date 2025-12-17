// Relative paths for unified FastAPI deployment
const getUrl = (funcName) => `/api/${funcName}`;

export const api = {
    createGame: async () => {
        const res = await fetch(getUrl("create_game"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
        });
        return res.json();
    },

    joinGame: async (code, name, characterDescription = null, characterImageUrl = null) => {
        const body = { name };
        if (characterDescription) {
            body.character_description = characterDescription;
        }
        if (characterImageUrl) {
            body.character_image_url = characterImageUrl;
        }
        const res = await fetch(`${getUrl("join_game")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        return res.json();
    },

    startGame: async (code) => {
        const res = await fetch(`${getUrl("start_game")}?code=${code}`, { method: "POST" });
        return res.json();
    },

    getGameState: async (code, playerId = null) => {
        // GET request, code as query param
        let url = `${getUrl("get_game_state")}?code=${code}`;
        if (playerId) {
            url += `&player_id=${playerId}`;
        }
        const res = await fetch(url);
        return res.json();
    },

    submitStrategy: async (code, playerId, strategy) => {
        const res = await fetch(`${getUrl("submit_strategy")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId, strategy }),
        });
        return res.json();
    },

    submitTrap: async (code, playerId, trapText) => {
        const res = await fetch(`${getUrl("submit_trap")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId, trap_text: trapText }),
        });
        return res.json();
    },

    voteTrap: async (code, voterId, targetId) => {
        const res = await fetch(`${getUrl("vote_trap")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ voter_id: voterId, target_id: targetId }),
        });
        return res.json();
    },

    voteCoop: async (code, voterId, targetId) => {
        const res = await fetch(`${getUrl("vote_coop")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ voter_id: voterId, target_id: targetId }),
        });
        return res.json();
    },

    nextRound: async (code) => {
        const res = await fetch(`${getUrl("next_round")}?code=${code}`, { method: "POST" });
        return res.json();
    },

    retryPlayerVideos: async (code) => {
        const res = await fetch(`${getUrl("retry_player_videos")}?code=${code}`, { method: "POST" });
        return res.json();
    },

    regenerateCharacterImage: async (code, playerId) => {
        const res = await fetch(`${getUrl("regenerate_character_image")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId }),
        });
        return res.json();
    },

    enterLobby: async (code, playerId) => {
        const res = await fetch(`${getUrl("enter_lobby")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId }),
        });
        return res.json();
    },

    // Sacrifice round APIs
    volunteerSacrifice: async (code, playerId) => {
        const res = await fetch(`${getUrl("volunteer_sacrifice")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId }),
        });
        return res.json();
    },

    advanceSacrificeVolunteer: async (code, playerId) => {
        const res = await fetch(`${getUrl("advance_sacrifice_volunteer")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId }),
        });
        return res.json();
    },

    voteSacrifice: async (code, voterId, targetId) => {
        const res = await fetch(`${getUrl("vote_sacrifice")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ voter_id: voterId, target_id: targetId }),
        });
        return res.json();
    },

    submitSacrificeSpeech: async (code, playerId, speech) => {
        const res = await fetch(`${getUrl("submit_sacrifice_speech")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId, speech }),
        });
        return res.json();
    },

    // Last Stand revival APIs
    voteRevival: async (code, voterId, targetId) => {
        const res = await fetch(`${getUrl("vote_revival")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ voter_id: voterId, target_id: targetId }),
        });
        return res.json();
    },

    advanceRevival: async (code, playerId) => {
        const res = await fetch(`${getUrl("advance_revival")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId }),
        });
        return res.json();
    },

    generateRandomCharacters: async () => {
        const res = await fetch(getUrl("generate_random_characters"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({}),
        });
        return res.json();
    },

    // Debug API - skip to specific game state
    debugSkipToState: async (code, playerId, options) => {
        const res = await fetch(`${getUrl("debug_skip_to_state")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                player_id: playerId,
                ...options,
            }),
        });
        return res.json();
    },

    // Get game configuration
    getConfig: async () => {
        const res = await fetch(getUrl("config"));
        return res.json();
    }
};
