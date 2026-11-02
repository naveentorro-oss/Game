import os
import uuid

import chess
import streamlit as st
from supabase import create_client

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# ---------------------------
# Supabase setup
# ---------------------------
def get_supabase():
    url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

    if not url or not key:
        st.error("Missing Supabase credentials. Add SUPABASE_URL and SUPABASE_KEY to environment or .streamlit/secrets.toml")
        st.stop()

    return create_client(url, key)

supabase = get_supabase()

# ---------------------------
# Helpers
# ---------------------------
def get_game(room_id):
    response = supabase.table("games").select("*").eq("id", room_id).limit(1).execute()
    if not response.data:
        return None
    return response.data[0]

def create_game(player_name):
    room_id = uuid.uuid4().hex[:8].upper()
    initial_fen = chess.Board().fen()
    payload = {
        "id": room_id,
        "white_player": player_name,
        "black_player": None,
        "fen": initial_fen,
        "turn": "w",
        "status": "waiting",
        "winner": None,
    }
    supabase.table("games").insert(payload).execute()
    return room_id

def join_game(room_id, player_name):
    room = get_game(room_id)
    if room is None:
        raise ValueError("Room not found")

    if room["status"] == "finished":
        raise ValueError("This game is already finished.")

    if room["white_player"] == player_name:
        return room_id

    if room["black_player"] is not None and room["black_player"] != player_name:
        raise ValueError("Room is already full.")

    if room["black_player"] is None:
        supabase.table("games").update({
            "black_player": player_name,
            "status": "active"
        }).eq("id", room_id).execute()

    return room_id

def get_player_color(room, player_name):
    if room["white_player"] == player_name:
        return "w"
    if room["black_player"] == player_name:
        return "b"
    return None

def determine_winner(room, board):
    if not board.is_game_over():
        return None

    outcome = board.outcome()
    if outcome is None:
        return "draw"

    if outcome.winner == chess.WHITE:
        return room["white_player"]
    elif outcome.winner == chess.BLACK:
        return room["black_player"]
    else:
        return "draw"

def update_game_state(room_id, board, status="active", winner=None):
    fen = board.fen()
    turn = "w" if board.turn == chess.WHITE else "b"
    payload = {
        "fen": fen,
        "turn": turn,
        "status": status,
        "winner": winner
    }
    supabase.table("games").update(payload).eq("id", room_id).execute()

# ---------------------------
# UI setup
# ---------------------------
st.set_page_config(page_title="Online Chess", layout="centered")
st.title("Online Chess Multiplayer ♟️")

# Auto refresh every 2 seconds
if st_autorefresh is not None:
    st_autorefresh(interval=2000, key="game_refresh")

# Session state defaults
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "room_id" not in st.session_state:
    st.session_state.room_id = ""
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None

UNICODE_PIECES = {
    "R": "♜", "N": "♞", "B": "♝", "Q": "♛", "K": "♚", "P": "♟",
    "r": "♖", "n": "♘", "b": "♗", "q": "♕", "k": "♔", "p": "♙",
}

# ---------------------------
# Room creation / join
# ---------------------------
st.sidebar.header("Player Setup")
player_name = st.sidebar.text_input("Your name", value=st.session_state.player_name)

if player_name:
    st.session_state.player_name = player_name

if not st.session_state.room_id:
    room_id_input = st.sidebar.text_input("Room ID to join", placeholder="ABC12345")
    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.sidebar.button("Create Room"):
            if not player_name:
                st.warning("Enter your name first.")
            else:
                room_id = create_game(player_name)
                st.session_state.room_id = room_id
                st.success(f"Room created! Share this code: {room_id}")
                st.rerun()

    with col2:
        if st.sidebar.button("Join Room"):
            if not player_name:
                st.warning("Enter your name first.")
            else:
                try:
                    room_id = join_game(room_id_input.strip().upper(), player_name)
                    st.session_state.room_id = room_id
                    st.success(f"Joined room: {room_id}")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

# If currently in a room
if st.session_state.room_id:
    room = get_game(st.session_state.room_id)

    if room is None:
        st.warning("This room no longer exists.")
        st.session_state.room_id = ""
        st.session_state.selected_square = None
        st.stop()

    st.subheader(f"Room: {room['id']}")

    white = room["white_player"]
    black = room["black_player"]
    st.write(f"White: {white}")
    st.write(f"Black: {black}")

    if black is None:
        st.info("Waiting for second player to join...")
        st.stop()

    # Current player's turn/check
    player_color = get_player_color(room, st.session_state.player_name)
    if player_color is None:
        st.warning("You are not a player in this room.")
        st.stop()

    board = chess.Board(room["fen"])

    # Board status
    if room["status"] == "finished":
        if room["winner"] == "draw":
            st.warning("This game ended in a draw.")
        else:
            st.success(f"Winner: {room['winner']}")
        st.subheader("Final position")
    else:
        turn_name = "White" if room["turn"] == "w" else "Black"
        st.info(f"It is {turn_name}'s turn.")

    if room["turn"] != player_color:
        st.caption("Waiting for the other player to move...")

    # ---------------------------
    # Move handling
    # ---------------------------
    def handle_square_click(square_index):
        room = get_game(st.session_state.room_id)
        if room is None:
            return

        if room["status"] == "finished":
            return

        current_player = st.session_state.player_name
        player_color = get_player_color(room, current_player)
        if player_color is None:
            return

        if room["turn"] != player_color:
            return

        board = chess.Board(room["fen"])
        selected = st.session_state.selected_square

        if selected is None:
            piece = board.piece_at(square_index)
            if piece is not None and piece.color == (chess.WHITE if player_color == "w" else chess.BLACK):
                st.session_state.selected_square = square_index
            return

        # legal move creation
        move = chess.Move(selected, square_index)

        piece = board.piece_at(selected)
        if piece and piece.piece_type == chess.PAWN:
            target_rank = chess.square_rank(square_index)
            if target_rank in [0, 7]:
                move.promotion = chess.QUEEN

        if move in board.legal_moves:
            board.push(move)

            winner = determine_winner(room, board)
            if board.is_game_over():
                status = "finished"
                winner_value = winner if winner is not None else "draw"
            else:
                status = "active"
                winner_value = None

            update_game_state(st.session_state.room_id, board, status=status, winner=winner_value)
            st.session_state.selected_square = None
        else:
            if board.piece_at(square_index) is not None:
                piece_on_target = board.piece_at(square_index)
                if piece_on_target.color == (chess.WHITE if player_color == "w" else chess.BLACK):
                    st.session_state.selected_square = square_index
                else:
                    st.session_state.selected_square = None
            else:
                st.session_state.selected_square = None

    # ---------------------------
    # Render board
    # ---------------------------
    board = chess.Board(room["fen"])
    for row in range(7, -1, -1):
        cols = st.columns(8)
        for col in range(8):
            square_idx = chess.square(col, row)
            piece = board.piece_at(square_idx)
            label = UNICODE_PIECES.get(piece.symbol(), " ") if piece else " "
            is_selected = st.session_state.selected_square == square_idx
            btn_type = "primary" if is_selected else "secondary"

            with cols[col]:
                st.button(
                    label,
                    key=f"sq_{st.session_state.room_id}_{square_idx}",
                    type=btn_type,
                    use_container_width=True,
                    on_click=handle_square_click,
                    args=(square_idx,),
                    disabled=(room["status"] == "finished" or room["turn"] != player_color)
                )

    # Sidebar controls
    st.sidebar.markdown("---")
    if st.sidebar.button("Reset Room"):
        new_board = chess.Board()
        update_game_state(
            st.session_state.room_id,
            new_board,
            status="active",
            winner=None
        )
        st.session_state.selected_square = None
        st.rerun()

    if st.sidebar.button("Leave Room"):
        st.session_state.room_id = ""
        st.session_state.selected_square = None
        st.rerun()

    # Status panel
    st.markdown("---")
    if room["status"] == "finished":
        if room["winner"] == "draw":
            st.warning("Game ended in a draw.")
        else:
            st.success(f"Winner: {room['winner']}")
    else:
        current_turn = "White" if room["turn"] == "w" else "Black"
        st.info(f"Current turn: {current_turn}")

        if st.session_state.selected_square is not None:
            selected_name = chess.square_name(st.session_state.selected_square).upper()
            st.success(f"Selected: {selected_name} — choose a destination square.")