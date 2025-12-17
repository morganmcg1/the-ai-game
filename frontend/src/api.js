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

    joinGame: async (code, name) => {
        const res = await fetch(`${getUrl("join_game")}?code=${code}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name }),
        });
        // Actually, to be safe with Modal web endpoints, passing params in URL is safest for simple arguments.
        // Let's fix the call below.
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
    }
};
