import pygame
import chess
import random
import sys
import pickle

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 700, 700
SQUARE_SIZE = WIDTH // 8
FPS = 1 # 1 frame per second for each move

# Colors
LIGHT_SQUARE = (247, 253, 206)
DARK_SQUARE = (118, 150, 86)
TEXT_COLOR = (0, 0, 0)

# Load images based on your naming convention
PIECES = {
    'bpawn': pygame.transform.scale(pygame.image.load('assets/bpawn.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'brook': pygame.transform.scale(pygame.image.load('assets/brook.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'bknight': pygame.transform.scale(pygame.image.load('assets/bknight.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'bbishop': pygame.transform.scale(pygame.image.load('assets/bbishop.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'bqueen': pygame.transform.scale(pygame.image.load('assets/bqueen.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'bking': pygame.transform.scale(pygame.image.load('assets/bking.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'wpawn': pygame.transform.scale(pygame.image.load('assets/wpawn.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'wrook': pygame.transform.scale(pygame.image.load('assets/wrook.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'wknight': pygame.transform.scale(pygame.image.load('assets/wknight.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'wbishop': pygame.transform.scale(pygame.image.load('assets/wbishop.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'wqueen': pygame.transform.scale(pygame.image.load('assets/wqueen.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'wking': pygame.transform.scale(pygame.image.load('assets/wking.png'), (SQUARE_SIZE, SQUARE_SIZE)),
}

# Piece values
piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,  # King is never counted for score
}

# Q-learning parameters
q_table = {}
alpha = 0.1  # Learning rate
gamma = 0.9  # Discount factor

# Create a window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Draw the chessboard
def draw_board(board, scores):
    for row in range(8):
        for col in range(8):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            # Draw pieces
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                piece_name = ''
                if piece.piece_type == chess.PAWN:
                    piece_name = 'bpawn' if piece.color == chess.BLACK else 'wpawn'
                elif piece.piece_type == chess.ROOK:
                    piece_name = 'brook' if piece.color == chess.BLACK else 'wrook'
                elif piece.piece_type == chess.KNIGHT:
                    piece_name = 'bknight' if piece.color == chess.BLACK else 'wknight'
                elif piece.piece_type == chess.BISHOP:
                    piece_name = 'bbishop' if piece.color == chess.BLACK else 'wbishop'
                elif piece.piece_type == chess.QUEEN:
                    piece_name = 'bqueen' if piece.color == chess.BLACK else 'wqueen'
                elif piece.piece_type == chess.KING:
                    piece_name = 'bking' if piece.color == chess.BLACK else 'wking'

                # Draw the piece on the board
                screen.blit(PIECES[piece_name], (col * SQUARE_SIZE, row * SQUARE_SIZE))

    # Draw scores
    font = pygame.font.SysFont('Arial', 32)
    score_text = f"Player 1: {scores[0]}  Player 2: {scores[1]}"
    score_surface = font.render(score_text, True, TEXT_COLOR)
    screen.blit(score_surface, (200, 300))  # Draw scores at top-left corner

# Save Q-table to a file
def save_q_table():
    with open('q_table.pkl', 'wb') as f:
        pickle.dump(q_table, f)

# Load Q-table from a file
def load_q_table():
    global q_table
    try:
        with open('q_table.pkl', 'rb') as f:
            q_table = pickle.load(f)
    except FileNotFoundError:
        q_table = {}

# Get state for the Q-table
def get_state(board):
    return board.fen()

# Heuristic to initialize Q-values
def initial_value_based_on_heuristic(move):
    # Assign an initial value based on the type of move; for now, we use 0
    return 0

# Initialize Q-values for a state
def initialize_q_values(state, board):
    if state not in q_table:
        q_table[state] = {}
        for move in board.legal_moves:
            q_table[state][move.uci()] = initial_value_based_on_heuristic(move)  # Initialize move values

# Choose move based on Q-table
def choose_move(board):
    state = get_state(board)
    initialize_q_values(state, board)  # Ensure the state is initialized
    legal_moves = list(board.legal_moves)
    print(f"Legal moves for state {state}: {[move.uci() for move in legal_moves]}")  # Debugging line
    if random.random() < 0.2:  # Increased exploration chance
        return random.choice(legal_moves)
    else:  # Exploitation
        return max(legal_moves, key=lambda move: q_table[state][move.uci()])

# Update Q-table
def update_q_table(old_state, move, reward, new_state, board):
    initialize_q_values(old_state, board)  # Ensure the old state is initialized
    initialize_q_values(new_state, board)  # Ensure the new state is initialized
    # Check if the move exists in the Q-table for the old state
    if move.uci() not in q_table[old_state]:
        print(f"Initializing move {move.uci()} for state {old_state}.")
        q_table[old_state][move.uci()] = 0  # Initialize move if not present
    # Update Q-value
    q_table[old_state][move.uci()] += alpha * (reward + gamma * max(q_table[new_state].values()) - q_table[old_state][move.uci()])

# Get reward based on the board and move
def get_reward(board, move):
    # Give a small positive reward for improving position (e.g., controlling the center)
    if move.to_square in [chess.E4, chess.D4, chess.E5, chess.D5]:
        return 0.1
    # Check if capturing a piece
    captured_piece = board.piece_at(move.to_square)
    return piece_values.get(captured_piece.piece_type, 0) if captured_piece else 0

# Main game loop
# Main game loop
def play_game():
    load_q_table()  # Load the Q-table
    board = chess.Board()
    scores = [0, 0]  # Scores for Player 1 and Player 2
    clock = pygame.time.Clock()

    while not board.is_game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                save_q_table()  # Save the Q-table on exit
                sys.exit()

        draw_board(board, scores)
        pygame.display.flip()  # Update the display

        # Player 1's move
        move1 = choose_move(board)
        captured_piece1 = board.piece_at(move1.to_square)
        reward1 = piece_values.get(captured_piece1.piece_type, 0) if captured_piece1 else 0
        if captured_piece1:  # If a piece was captured
            scores[0] += piece_values[captured_piece1.piece_type]  # Update Player 1's score
        board.push(move1)
        print(f"Player 1 moves: {move1}, Captured: {captured_piece1}, Score: {scores[0]}")

        # Update Q-table
        update_q_table(get_state(board), move1, reward1, get_state(board), board)

        draw_board(board, scores)
        pygame.display.flip()  # Update the display
        pygame.time.delay(500)  # Reduced wait time to 0.5 seconds

        # Check for game over after Player 1's move
        if board.is_game_over():
            if board.is_checkmate():
                print(f"Checkmate! Result: {'1-0' if board.turn == chess.BLACK else '0-1'}")
            elif board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repetition():
                print("The game is a draw!")
            break

        # Player 2's move
        move2 = choose_move(board)
        captured_piece2 = board.piece_at(move2.to_square)
        reward2 = piece_values.get(captured_piece2.piece_type, 0) if captured_piece2 else 0
        if captured_piece2:  # If a piece was captured
            scores[1] += piece_values[captured_piece2.piece_type]  # Update Player 2's score
        board.push(move2)
        print(f"Player 2 moves: {move2}, Captured: {captured_piece2}, Score: {scores[1]}")

        # Update Q-table
        update_q_table(get_state(board), move2, reward2, get_state(board), board)

        draw_board(board, scores)
        pygame.display.flip()  # Update the display
        pygame.time.delay(500)  # Reduced wait time to 0.5 seconds

        if board.is_game_over():
            if board.is_checkmate():
                print(f"Checkmate! Result: {'1-0' if board.turn == chess.BLACK else '0-1'}")
            elif board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repetition():
                print("The game is a draw!")
            break

        clock.tick(FPS)  # Maintain the frame rate

    print("Game over!")
    print("Result:", board.result())
    save_q_table()  # Save the Q-table at the end of the game

# Start the game
play_game()
pygame.quit()