import chess
import streamlit as st

st.set_page_config(layout="centered")
st.title("Streamlit Graphical Chess ♟️")

# 1. Initialize the board and selection states
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None

# Sidebar Controls
if st.sidebar.button("Reset Game", type="primary"):
    st.session_state.board = chess.Board()
    st.session_state.selected_square = None
    st.rerun()

# 2. Map chess pieces to Unicode symbols for display
UNICODE_PIECES = {
    "R": "♜", "N": "♞", "B": "♝", "Q": "♛", "K": "♚", "P": "♟",
    "r": "♖", "n": "♘", "b": "♗", "q": "♕", "k": "♔", "p": "♙",
}

# 3. Handle Square Clicks
def handle_square_click(square_index):
    selected = st.session_state.selected_square
    
    if selected is None:
        # First click: Select a piece if one exists on that square
        if st.session_state.board.piece_at(square_index) is not None:
            st.session_state.selected_square = square_index
    else:
        # Second click: Attempt to move from the previously selected square to this one
        move = chess.Move(selected, square_index)
        
        # Check for pawn promotion (auto-promote to Queen for simplicity)
        piece = st.session_state.board.piece_at(selected)
        if piece and piece.piece_type == chess.PAWN:
            if chess.square_rank(square_index) in [0, 7]:
                move.promotion = chess.QUEEN
        
        # Execute move if valid
        if move in st.session_state.board.legal_moves:
            st.session_state.board.push(move)
            st.session_state.selected_square = None
        else:
            # If illegal move, clear selection or switch to new piece selection
            if st.session_state.board.piece_at(square_index) is not None:
                st.session_state.selected_square = square_index
            else:
                st.session_state.selected_square = None
    st.rerun()

# 4. Render the 8x8 Board
# Rows in chess are 0-7 starting from the bottom (Rank 1 to Rank 8)
for row in range(7, -1, -1):
    cols = st.columns(8)
    for col in range(8):
        square_idx = chess.square(col, row)
        piece = st.session_state.board.piece_at(square_idx)
        
        # Determine button label (Piece icon or blank space)
        label = UNICODE_PIECES[piece.symbol()] if piece else " "
        
        # Check if this square is currently selected
        is_selected = st.session_state.selected_square == square_idx
        btn_type = "primary" if is_selected else "secondary"
        
        # Render square button
        with cols[col]:
            st.button(
                label, 
                key=f"sq_{square_idx}", 
                type=btn_type, 
                use_container_width=True,
                on_click=handle_square_click,
                args=(square_idx,)
            )

# 5. Display Status
st.markdown("---")
if st.session_state.board.is_game_over():
    st.error(f"Game Over! Result: {st.session_state.board.outcome().result()}")
else:
    turn = "White" if st.session_state.board.turn == chess.WHITE else "Black"
    st.info(f"**Turn:** {turn} to move")
    
    if st.session_state.selected_square is not None:
        square_name = chess.square_name(st.session_state.selected_square)
        st.success(f"Selected Square: **{square_name.upper()}** (Click a target square to move)")