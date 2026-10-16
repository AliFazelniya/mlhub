/* AI Tic-Tac-Toe frontend — vanilla JS, SPA-style state machine. */
(function () {
  "use strict";

  const CFG = window.GAME_CONFIG || { minSize: 3, maxSize: 10, rlSizes: [3, 4, 5] };

  const state = {
    boardSize: 5,
    humanMark: "X",
    engine: "rl",
    grid: [],
    started: false,
    awaiting: false,
    lastAiMove: null,
    gameOver: false,
  };

  const aiMark = () => (state.humanMark === "X" ? "O" : "X");

  const $ = (id) => document.getElementById(id);

  function csrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute("content") : "";
  }

  function emptyGrid(size) {
    return Array.from({ length: size }, () => Array(size).fill(null));
  }

  function countEmpty(grid) {
    let n = 0;
    grid.forEach((row) => row.forEach((c) => { if (!c) n += 1; }));
    return n;
  }

  /* ----------------------------- setup UI ------------------------------ */
  function sizeSupportedByRL(size) {
    return Array.isArray(CFG.rlSizes) && CFG.rlSizes.indexOf(size) !== -1;
  }

  function updateSizeBadge() {
    const badge = $("size-badge");
    if (state.engine === "rl" && sizeSupportedByRL(state.boardSize)) {
      badge.textContent = "DQN + Minimax";
    } else {
      badge.textContent = "Minimax AI";
    }
  }

  function setNote(text) {
    $("engine-note").textContent = text || "";
  }

  function refreshEngineNote() {
    if (state.engine === "rl" && !sizeSupportedByRL(state.boardSize)) {
      setNote(
        "No trained DQN model for " + state.boardSize + "x" + state.boardSize +
        " — Minimax AI will be used automatically."
      );
    } else {
      setNote("");
    }
    updateSizeBadge();
  }

  $("size-minus").addEventListener("click", () => {
    if (state.boardSize > CFG.minSize) {
      state.boardSize -= 1;
      $("size-value").textContent = state.boardSize;
      refreshEngineNote();
    }
  });
  $("size-plus").addEventListener("click", () => {
    if (state.boardSize < CFG.maxSize) {
      state.boardSize += 1;
      $("size-value").textContent = state.boardSize;
      refreshEngineNote();
    }
  });

  document.querySelectorAll("#role-select .seg").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#role-select .seg").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.humanMark = btn.getAttribute("data-role");
    });
  });

  document.querySelectorAll("#engine-select .seg").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#engine-select .seg").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.engine = btn.getAttribute("data-engine");
      refreshEngineNote();
    });
  });

  /* ------------------------------ board ------------------------------- */
  function markSVG(mark) {
    if (mark === "X") {
      return '<div class="mark x"><svg viewBox="0 0 100 100">' +
        '<path d="M22 22 L78 78" fill="none"/>' +
        '<path d="M78 22 L22 78" fill="none"/></svg></div>';
    }
    if (mark === "O") {
      return '<div class="mark o"><svg viewBox="0 0 100 100">' +
        '<circle cx="50" cy="50" r="28"/></svg></div>';
    }
    return "";
  }

  function renderBoard() {
    const board = $("board");
    const size = state.boardSize;
    board.style.gridTemplateColumns = "repeat(" + size + ", 1fr)";
    board.innerHTML = "";

    for (let r = 0; r < size; r += 1) {
      for (let c = 0; c < size; c += 1) {
        const cell = document.createElement("div");
        cell.className = "cell";
        cell.dataset.row = r;
        cell.dataset.col = c;
        const val = state.grid[r] ? state.grid[r][c] : null;
        if (val) {
          cell.classList.add("taken");
          cell.innerHTML = markSVG(val);
        }
        if (state.lastAiMove && state.lastAiMove[0] === r && state.lastAiMove[1] === c) {
          cell.classList.add("last-ai");
        }
        if (state.awaiting || state.gameOver || !state.started) {
          cell.classList.add("locked");
        }
        cell.addEventListener("click", () => onCellClick(r, c));
        board.appendChild(cell);
      }
    }
  }

  /* ---------------------------- scoreboard ---------------------------- */
  function updateScores(scoreX, scoreO) {
    $("score-x").textContent = scoreX;
    $("score-o").textContent = scoreO;
    $("empty-cells").textContent = countEmpty(state.grid);
    $("label-x").textContent = state.humanMark === "X"
      ? "X (You)" : "X (AI)";
    $("label-o").textContent = state.humanMark === "O"
      ? "O (You)" : "O (AI)";
  }

  function setStatus(text) { $("status-text").textContent = text; }

  function setEngineChip(engine) {
    const chip = $("engine-used");
    if (!engine) { chip.hidden = true; return; }
    chip.hidden = false;
    chip.textContent = engine === "rl" ? "Engine: DQN" : "Engine: Minimax";
  }

  /* ------------------------------- API -------------------------------- */
  async function apiMove(humanMove, gridOverride) {
    const res = await fetch("/api/move/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken(),
      },
      body: JSON.stringify({
        grid: gridOverride || state.grid,
        board_size: state.boardSize,
        human_mark: state.humanMark,
        human_move: humanMove,
        ai_mode: state.engine,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || "Request failed");
    }
    return res.json();
  }

  function applyServerResponse(data) {
    state.grid = data.grid;
    state.lastAiMove = data.ai_move || null;
    updateScores(data.score_x, data.score_o);
    setEngineChip(data.engine_used);

    if (data.is_game_over) {
      state.gameOver = true;
      state.started = false;
      renderBoard();
      showModal(data.result_message, data.winner, data.human_score, data.ai_score);
      loadHistory();
    } else {
      renderBoard();
    }
  }

  async function onCellClick(r, c) {
    if (!state.started || state.awaiting || state.gameOver) return;
    if (state.grid[r][c]) return;

    // The server applies the human move itself from `human_move`, so it must
    // receive the board state BEFORE this move. Keep a clean pre-move snapshot
    // and send that (do not send the optimistically-updated grid, or the server
    // will reject the already-occupied cell as an "Illegal human move").
    const gridBeforeMove = state.grid.map((row) => row.slice());
    const humanMove = [r, c];

    // Optimistic human placement for immediate feedback
    state.grid[r][c] = state.humanMark;
    state.awaiting = true;
    state.lastAiMove = null;
    renderBoard();
    updateScores(scoreXGuess(), scoreOGuess());
    setStatus("AI is thinking…");

    try {
      const data = await apiMove(humanMove, gridBeforeMove);
      state.awaiting = false;
      applyServerResponse(data);
      if (!data.is_game_over) setStatus("Your turn.");
    } catch (e) {
      state.awaiting = false;
      // Roll back optimistic move
      state.grid[r][c] = null;
      renderBoard();
      setStatus("Error: " + e.message);
    }
  }

  // Local score guesses are only used for a brief optimistic flash; the
  // authoritative scores always come from the server response.
  let lastKnown = { x: 0, o: 0 };
  function scoreXGuess() { return lastKnown.x; }
  function scoreOGuess() { return lastKnown.o; }

  /* ------------------------------ modal ------------------------------- */
  function showModal(message, winner, humanScore, aiScore) {
    const modal = $("modal");
    const title = $("modal-title");
    title.textContent = message || "Game Over";
    title.className = winner === "human" ? "win" : (winner === "ai" ? "loss" : "tie");
    $("modal-scores").textContent =
      "Your score: " + humanScore + "  ·  AI score: " + aiScore;
    modal.hidden = false;
  }

  function hideModal() { $("modal").hidden = true; }

  $("play-again").addEventListener("click", () => {
    hideModal();
    startGame();
  });
  $("change-setup").addEventListener("click", () => {
    hideModal();
    state.started = false;
    state.gameOver = false;
    state.lastAiMove = null;
    setStatus("Choose your options and press Start Game.");
    setEngineChip(null);
    renderBoard();
  });

  /* ------------------------------- flow -------------------------------- */
  async function startGame() {
    state.grid = emptyGrid(state.boardSize);
    state.gameOver = false;
    state.lastAiMove = null;
    state.started = true;
    state.awaiting = false;
    lastKnown = { x: 0, o: 0 };

    hideModal();
    renderBoard();
    updateScores(0, 0);
    setEngineChip(null);

    if (state.humanMark === "O") {
      // AI (X) opens the game.
      state.awaiting = true;
      setStatus("AI is thinking…");
      renderBoard();
      try {
        const data = await apiMove(null);
        state.awaiting = false;
        applyServerResponse(data);
        if (!data.is_game_over) setStatus("Your turn.");
      } catch (e) {
        state.awaiting = false;
        setStatus("Error: " + e.message);
      }
    } else {
      setStatus("Your turn.");
    }
  }

  $("start-btn").addEventListener("click", startGame);

  /* ----------------------------- history ------------------------------ */
  async function loadHistory() {
    try {
      const res = await fetch("/api/history/");
      const data = await res.json();
      const s = data.stats || {};
      $("stat-total").textContent = s.total_games || 0;
      $("stat-wins").textContent = s.human_wins || 0;
      $("stat-losses").textContent = s.ai_wins || 0;
      $("stat-ties").textContent = s.ties || 0;
      $("stat-winrate").textContent = (s.win_rate || 0) + "%";

      const list = $("history-list");
      list.innerHTML = "";
      const recent = data.recent_matches || [];
      if (!recent.length) {
        const li = document.createElement("li");
        li.className = "empty";
        li.textContent = "No matches yet.";
        list.appendChild(li);
        return;
      }
      recent.forEach((m) => {
        const li = document.createElement("li");
        const meta = document.createElement("span");
        meta.className = "h-meta";
        meta.textContent =
          m.board_size + "x" + m.board_size + " · " + m.ai_engine +
          " · " + m.human_score + "-" + m.ai_score;
        const res = document.createElement("span");
        res.className = "h-result " + m.result;
        res.textContent = m.result;
        li.appendChild(meta);
        li.appendChild(res);
        list.appendChild(li);
      });
    } catch (e) {
      /* history panel is non-critical */
    }
  }

  $("clear-history").addEventListener("click", async () => {
    try {
      await fetch("/api/history/clear/", {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken() },
      });
      loadHistory();
    } catch (e) { /* ignore */ }
  });

  /* ------------------------------- init -------------------------------- */
  function init() {
    $("size-value").textContent = state.boardSize;
    refreshEngineNote();
    state.grid = emptyGrid(state.boardSize);
    renderBoard();
    updateScores(0, 0);
    loadHistory();
  }

  init();
})();
