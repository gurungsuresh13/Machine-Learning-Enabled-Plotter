import game
from camera import get_matrix_from_frame
import gcode
import os
import cv2

def choose_difficulty():
    """Choose difficulty level with corresponding depth limits."""
    print("Choose difficulty: 1 (Easy), 2 (Normal), 3 (Hard)")
    while True:
        try:
            choice = int(input("Enter your choice (1/2/3): "))
            if choice == 1:
                return 1  # Easy: Depth 1
            elif choice == 2:
                return 3  # Normal: Depth 3
            elif choice == 3:
                return 9  # Hard: Full depth
            else:
                print("Invalid input. Please choose 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")
[p]
def capture_board(cap):
    """Continuously capture the board until detection succeeds or the user quits."""
    print(" Position the board in front of the camera.")
    print(" Press 'c' to capture the board.")
    print(" Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print(" Failed to capture frame. Try again.")
            continue

        cv2.imshow("Live Feed - Capture Board", frame)
        key = cv2.waitKey(1)

        if key == ord('c'):
            print(" Detecting board...")
            board = get_matrix_from_frame(frame)
            if board is None:
                print(" No board detected. Please re-position the board and try again.")
                continue  # Go back and ask for re-capture
            print(" Board detected successfully!")
            return board  

        elif key == ord('q'):
            print("👋 Exiting game.")
            cap.release()
            cv2.destroyAllWindows()
            exit()

def main():
    print("Welcome to Tic-Tac-Toe!")
    cap = cv2.VideoCapture(0)  # Change index for your webcam

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Type 'n' for a New Game or 'c' to Continue from a mid-game state.")
    choice = ""
    while choice not in ["n", "c", "q"]:
        choice = input("Enter your choice (n/c/q): ").strip().lower()
        if choice not in ["n", "c", "q"]:
            print("Invalid input. Please type 'n', 'c', or 'q'.")

    if choice == "q":
        print("Exiting the game. Goodbye!")
        cap.release()
        return

    # Select difficulty
    difficulty = choose_difficulty()

    if choice == "n":
        print("Starting a New Game!")
        board = [["_"] * 3 for _ in range(3)]
        
        # Ask the player to choose their side
        player = ""
        while player not in ["x", "o"]:
            player = input("Choose your side (X or O): ").strip().lower()
        
        # Determine AI's side
        AI = "o" if player == "x" else "x"
        human = player

        # The player who chooses X should always start first
        current_turn = "x"

        # Draw the board **only for a new game**
        gcode.send_gcode_file("board.gcode")

    elif choice == "c":
        print("Continuing from a mid-game state.")
        board = capture_board(cap)  
        
        # Ask the player to choose their side
        player = ""
        while player not in ["x", "o"]:
            player = input("Choose your side (X or O): ").strip().lower()
        
        # Determine AI's side
        AI = "o" if player == "x" else "x"
        human = player

        # Count existing Xs and Os to determine the current turn
        x_count = sum(row.count("x") for row in board)
        o_count = sum(row.count("o") for row in board)

        # Determine whose turn it is:
        if x_count == o_count:
            current_turn = "x"
        elif x_count > o_count:
            current_turn = "o"
        else:
            current_turn = "x"

    # Main game loop
    while True:
        game.print_board(board)
        winner = game.get_winner(board)
        if winner:
            print(" Player wins!" if winner == player else " AI wins!")
            break
        if not game.is_moves_left(board):
            print(" It's a draw!")
            break

        if current_turn == player:
            print(" Capture your move by positioning the board and pressing 'c'.")
            board = capture_board(cap)  
            current_turn = AI
        else:
            best_move = game.find_best_move(board, AI, human, difficulty)
            if best_move:
                game.make_move(board, AI, best_move[0], best_move[1])
                position = best_move[0] * 3 + best_move[1] + 1  # Convert row/col to cell number
                
                # Send the correct G-code file for AI's move
                ai_gcode_file = f"draw_{AI.lower()}_{position}.gcode"
                print(f" AI moves at Cell {position}, executing {ai_gcode_file}...")
                gcode.send_gcode_file(ai_gcode_file)  # Send the correct G-code file

                #  Wait for CNC to complete execution before continuing
                input(" CNC is done! Press Enter to continue...")

                # Ask the user to make their move
                print(" Waiting for the player's move...")
                board = capture_board(cap)  # Wait for player input (via camera)
                current_turn = player  

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
