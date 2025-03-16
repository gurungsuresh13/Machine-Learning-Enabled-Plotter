import math

def print_board(board):
    """Print the current game board."""
    print("---------")
    for row in board:
        print("| " + " | ".join(row) + " |")
    print("---------")

def make_move(board, player, row, col):
    """Place the player's move on the board if valid."""
    if board[row][col] == "_":
        board[row][col] = player
        return True
    return False

def get_winner(board):
    """Check for a winner and return 'x' or 'o' if found, otherwise None."""
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != "_":
            return board[i][0]
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] != "_":
            return board[0][j]
    if board[0][0] == board[1][1] == board[2][2] != "_":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "_":
        return board[0][2]
    return None

def is_moves_left(board):
    """Check if there are empty cells left."""
    for row in board:
        if "_" in row:
            return True
    return False

def evaluate(board, AI, human):
    """Evaluate the board from the AI's perspective."""
    winner = get_winner(board)
    if winner == AI:
        return 10
    elif winner == human:
        return -10
    return 0

def minimax(board, depth, isMaximizing, AI, human, depth_limit):
    score = evaluate(board, AI, human)
    if score == 10 or score == -10 or not is_moves_left(board):
        return score
    if depth == depth_limit:
        return score

    if isMaximizing:
        best = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == "_":
                    board[i][j] = AI
                    val = minimax(board, depth + 1, False, AI, human, depth_limit)
                    board[i][j] = "_"
                    best = max(best, val)
        return best
    else:
        best = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == "_":
                    board[i][j] = human
                    val = minimax(board, depth + 1, True, AI, human, depth_limit)
                    board[i][j] = "_"
                    best = min(best, val)
        return best

def find_best_move(board, AI, human, depth_limit):
    """Find the best move for the AI using Minimax with a depth limit."""
    best_val = -math.inf
    best_move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == "_":
                board[i][j] = AI
                move_val = minimax(board, 0, False, AI, human, depth_limit)
                board[i][j] = "_"
                if move_val > best_val:
                    best_val = move_val
                    best_move = (i, j)
    return best_move
