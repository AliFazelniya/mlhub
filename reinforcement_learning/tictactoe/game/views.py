"""REST API + page views for the Tic-Tac-Toe web app."""

import json

from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from game.ai_manager import compute_ai_move, resolve_engine
from game.engine.board import Board
from game.models import MatchHistory
from game.models_rl.registry import registry

MIN_SIZE = 3
MAX_SIZE = 10


def _clamp_size(value, default=5):
    try:
        size = int(value)
    except (TypeError, ValueError):
        return default
    return max(MIN_SIZE, min(MAX_SIZE, size))


def index(request):
    """Render the single-page game interface."""
    context = {
        "min_size": MIN_SIZE,
        "max_size": MAX_SIZE,
        "rl_sizes": registry.available_sizes,
    }
    return render(request, "game/index.html", context)


def _build_board(grid, board_size):
    board = Board(board_size)
    if isinstance(grid, list):
        for r in range(min(board_size, len(grid))):
            row = grid[r]
            if not isinstance(row, list):
                continue
            for c in range(min(board_size, len(row))):
                cell = row[c]
                if cell in ("X", "O"):
                    board.make_move(r, c, cell)
    return board


def _outcome(human_score, ai_score):
    if human_score > ai_score:
        return "WIN", "Victory!"
    if ai_score > human_score:
        return "LOSS", "Defeat!"
    return "TIE", "It's a Tie!"


@csrf_exempt
@require_http_methods(["POST"])
def api_move(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    board_size = _clamp_size(payload.get("board_size"), 5)
    human_mark = payload.get("human_mark")
    if human_mark not in ("X", "O"):
        return JsonResponse({"error": "human_mark must be 'X' or 'O'."}, status=400)
    ai_mark = "O" if human_mark == "X" else "X"

    requested_mode = payload.get("ai_mode", "rl")
    if requested_mode not in ("rl", "minimax"):
        requested_mode = "minimax"

    grid = payload.get("grid")
    human_move = payload.get("human_move")

    board = _build_board(grid, board_size)

    if human_move is not None:
        try:
            hr, hc = int(human_move[0]), int(human_move[1])
        except (TypeError, ValueError, IndexError):
            return JsonResponse({"error": "human_move must be [row, col]."}, status=400)
        if not board.make_move(hr, hc, human_mark):
            return JsonResponse({"error": "Illegal human move."}, status=400)

    ai_move = None
    if not board.is_full():
        move, engine_used = compute_ai_move(
            board, ai_mark, human_mark, requested_mode
        )
        if move is not None:
            board.make_move(move[0], move[1], ai_mark)
            ai_move = [move[0], move[1]]
        else:
            engine_used = resolve_engine(requested_mode, board_size)
    else:
        engine_used = resolve_engine(requested_mode, board_size)

    score_x, score_o = board.calculate_scores()
    human_score = score_x if human_mark == "X" else score_o
    ai_score = score_o if human_mark == "X" else score_x

    is_game_over = board.is_full()
    result_message = None
    winner = None
    result = None

    if is_game_over:
        result, result_message = _outcome(human_score, ai_score)
        if result == "WIN":
            winner = "human"
        elif result == "LOSS":
            winner = "ai"
        else:
            winner = "tie"
        MatchHistory.objects.create(
            board_size=board_size,
            human_mark=human_mark,
            ai_engine=engine_used,
            human_score=human_score,
            ai_score=ai_score,
            result=result,
        )

    return JsonResponse(
        {
            "grid": board.grid,
            "ai_move": ai_move,
            "score_x": score_x,
            "score_o": score_o,
            "human_score": human_score,
            "ai_score": ai_score,
            "is_game_over": is_game_over,
            "result_message": result_message,
            "winner": winner,
            "engine_used": engine_used,
        }
    )


@require_http_methods(["GET"])
def api_history(request):
    qs = MatchHistory.objects.all()
    total = qs.count()
    wins = qs.filter(result="WIN").count()
    losses = qs.filter(result="LOSS").count()
    ties = qs.filter(result="TIE").count()
    win_rate = round((wins / total) * 100, 1) if total else 0.0

    recent = list(qs.values()[:10])

    return JsonResponse(
        {
            "stats": {
                "total_games": total,
                "human_wins": wins,
                "ai_wins": losses,
                "ties": ties,
                "win_rate": win_rate,
            },
            "recent_matches": recent,
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def api_history_clear(request):
    deleted, _ = MatchHistory.objects.all().delete()
    return JsonResponse({"cleared": deleted})
