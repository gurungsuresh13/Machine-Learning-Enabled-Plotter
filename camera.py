import cv2
import numpy as np
from inference_sdk import InferenceHTTPClient

# Initialize Roboflow API client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="xxxxxxxxxxxxxxxx"  # Enter API key from Roboflow
)

# Model IDs
BOARD_MODEL_ID = "tictactoe-uyxgd-ak2el/1"
SYMBOL_MODEL_ID = "tictactoe-qsz5b/3"

def detect_board_with_roboflow(image_path):
    """Detect the Tic-Tac-Toe board using Roboflow."""
    try:
        result = CLIENT.infer(image_path, model_id=BOARD_MODEL_ID)
        predictions = result.get("predictions", [])
        print("Board Detection Raw Output:", predictions)

        board_box = None
        max_area = 0
        for pred in predictions:
            if pred["class"].lower() == "field":
                x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
                area = w * h
                if area > max_area:
                    max_area = area
                    board_box = (x, y, w, h)

        return board_box
    except Exception as e:
        print("Error during board detection:", e)
        return None

def warp_to_birds_eye_view(image, board_box):
    """Warp the detected board to match its real size instead of a fixed 300x300."""
    if board_box is None:
        return None

    x, y, w, h = board_box

    src_points = np.array([
        [x - w / 2, y - h / 2],
        [x + w / 2, y - h / 2],
        [x + w / 2, y + h / 2],
        [x - w / 2, y + h / 2]
    ], dtype=np.float32)

 
    width, height = int(w), int(h)
    
    dst_points = np.array([
        [0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]
    ], dtype=np.float32)

    transform_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    warped = cv2.warpPerspective(image, transform_matrix, (width, height))

    cv2.imwrite("warped_board.jpg", warped)
    print(f"✅ Saved warped board image as 'warped_board.jpg' ({width}x{height}) for debugging.")

    return warped

def detect_symbols_with_roboflow(image_path):
    try:
        result = CLIENT.infer(image_path, model_id=SYMBOL_MODEL_ID)
        predictions = result.get("predictions", [])
        print("🔍 Raw Symbol Predictions:", predictions)

        return predictions
    except Exception as e:
        print("Error during symbol detection:", e)
        return []

def get_matrix_from_frame(frame):
    """Capture the board matrix using Roboflow detection."""
    cv2.imwrite("current_frame.jpg", frame)
    board_box = detect_board_with_roboflow("current_frame.jpg")

    if board_box is None:
        print("❌ No valid board detected.")
        return None

    warped_image = warp_to_birds_eye_view(frame, board_box)

    if warped_image is None:
        print("❌ Error warping board.")
        return None

    cv2.imwrite("warped_board.jpg", warped_image)
    predictions = detect_symbols_with_roboflow("warped_board.jpg")

    board = map_symbols_to_board(predictions, warped_image.shape[1], warped_image.shape[0])
    
    return board

def map_symbols_to_board(predictions, board_width, board_height):
    """Map detected symbols to a 3x3 Tic-Tac-Toe grid."""
    board = [['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']]
    cell_width = board_width / 3
    cell_height = board_height / 3

    for pred in predictions:
        if "class" not in pred or "x" not in pred or "y" not in pred:
            continue

        raw_label = pred["class"].strip()
        label = raw_label.lower()  

        # Ensure correct class matching
        if raw_label == "O" or label == "o":
            label = "o"
        elif raw_label == "X" or label == "x":
            label = "x"
        else:
            continue  

        x, y = pred["x"], pred["y"]

        row = min(2, max(0, int(y / cell_height)))
        col = min(2, max(0, int(x / cell_width)))

        if board[row][col] == "_":
            board[row][col] = label

    return board
