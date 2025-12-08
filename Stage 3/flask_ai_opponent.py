import json
import random
import logging

from flask import Flask, render_template, request, redirect, url_for, flash

from config import SAVE_FILE, DARK, LIGHT, NONE, SECRET_KEY

logging.basicConfig(
    filename="othello_game.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialise Flask.
app = Flask(__name__)
app.secret_key = SECRET_KEY

def initialise_board():
    """ The initialisation of the board 8x8 and putting on it in initial places our pieces."""

    board = []

    for i in range(8):
        row = []
        for i in range(8):
            row.append(NONE)
        board.append(row)

    # Set the squares and piece colours as defined by the game rules for the starting positions.
    board[3][3] = LIGHT
    board[3][4] = DARK
    board[4][3] = DARK
    board[4][4] = LIGHT
    return board

# Initialise the board and log that this has taken place.
# Set the maximum number of moves and which player will move next.
# A game always starts with the DARK piece being moved first.
board = initialise_board()
logger.info("Initialise board with four pieces in the initial positions")
turn_player = DARK
move_counter = 60

# The position of all squares around any given square given as a vector relative to any given square.
vectors = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1), (1, 0), (1, 1)]

def normalise_board(board):
    """Verify board squares have consistent constants."""

    # Ensure the array 'board' contains only expected values.
    for r in range(8):
        for c in range(8):
            cell = board[r][c].strip()
            if cell == "Dark":
                board[r][c] = DARK
            elif cell == "Light":
                board[r][c] = LIGHT
            else:
                board[r][c] = NONE

def in_range(r, c):
    """Check on the board if the coordinates exist"""

    return 0 <= r < 8 and 0 <= c < 8

def move_is_legal(player, position, board):
    """
    Work out if a proposed move is legal using the proposed position,
    the current board state and the player suggesting the move.
    """

    row_0, column_0 = position
    if not in_range(row_0, column_0) or board[row_0][column_0] != NONE:
        return False

    # Make enemy reflect the opponents colour.
    enemy = LIGHT if player == DARK else DARK

    # Using 'vectors' scan the board to find an enemy piece.
    for change_r, change_c in vectors:
        r, c = row_0 + change_r, column_0 + change_c
        found_enemy = False

        while in_range(r, c) and board[r][c] == enemy:
            found_enemy = True
            r += change_r
            c += change_c

        if found_enemy and in_range(r, c) and board[r][c] == player:
            return True

    # If an enemy piece could not be found after scanning all squares
    # using the vectors defined in 'vector', then return false as the
    # move cannot be legal.
    return False

def moves_are_legal(player, board):
    """
    Create a list of all legal moves available for the current player given the current board state
    """

    moves = []

    for r in range(8):
        for c in range(8):
            if move_is_legal(player, (r, c), board):
                moves.append((r, c))
    return moves

def make_move(player, position, board):
    """
    Perform a move that has been found to be legal.
    This includes changing the colour of pieces that the game rules define
    should be flipped when a move is legal.
    """

    row_0, column_0 = position
    enemy = LIGHT if player == DARK else DARK
    board[row_0][column_0] = player
    for change_r, change_c in vectors:
        r, c = row_0 + change_r, column_0 + change_c
        flips = []
        while in_range(r, c) and board[r][c] == enemy:
            flips.append((r, c))
            r += change_r
            c += change_c
        if flips and in_range(r, c) and board[r][c] == player:
            for flip_r, flip_c in flips:
                board[flip_r][flip_c] = player


def count_pieces(board):
    """Count the number of dark and light pieces on the board."""

    amount_of_light = 0
    amount_of_dark = 0
    for row in board:
        amount_of_light += row.count(LIGHT)
        amount_of_dark += row.count(DARK)
    return amount_of_light, amount_of_dark


def ai_turn(board):
    """Collect all possible legal moves that the automated opponent could make."""

    moves = moves_are_legal(LIGHT, board)

    # From the list of legal moves, pick one at random
    # Note: The AI could be improved by counting the number
    #       of flipped pieces for each possible move, and selecting to
    #       make the best move i.e. the one that flips the most pieces.
    #       Different levels of automated opponent could also be created
    #       like this by always selecting the best move, worst move or
    #       somewhere in the middle.
    if moves:
        return random.choice(moves)
    return None


@app.route("/")
def idx():
    """
    Get the current count of dark and light pieces from the board and render the main page.
    """

    global board, turn_player, move_counter

    # Make sure that the board uses consistent constants.
    normalise_board(board)

    # Calculate totals of every single  piece type for score display and game over checks.
    amount_of_light, amount_of_dark = count_pieces(board)
    game_over = False
    congratulation_message = ""

    while True:
        # For both players get all legal moves.
        dark_moves = moves_are_legal(DARK, board)
        light_moves = moves_are_legal(LIGHT, board)

        if move_counter <= 0 or (not dark_moves and not light_moves):
            game_over = True

            # Check if the game has finished
            if amount_of_light > amount_of_dark:
                congratulation_message = "Congratulations, light wins"
            elif amount_of_dark > amount_of_light:
                congratulation_message = "Congratulations, dark wins"
            else:
                congratulation_message = "Tie!"
                logger.info(f"You finished the game, the results are: Winner: {congratulation_message}, Light: {amount_of_light}, Dark: {amount_of_dark}")
            break

        # Human turn.
        if turn_player == DARK:
            if dark_moves:
                break
            flash("Dark hasn't got legal moves, AI turn")
            turn_player = LIGHT

        # AI turn.
        elif turn_player == LIGHT:
            if light_moves:
                r, c = ai_turn(board)
                make_move(LIGHT, (r, c), board)
                logger.info(f"AI opponent places the light piece at ({r}, {c})")
                normalise_board(board)
                move_counter -= 1
                flash(f"AI move to ({r+1}, {c+1})")
                turn_player = DARK
            else:
                flash("AI has no legal moves, human turn")
                turn_player = DARK

    # Display welcome message on the screen when the board is still empty.
    hello_message = ""
    if move_counter == 60:
        empty_board = True
        for row in board:
            for cell in row:
                if cell != 'None ':
                    empty_board = False
                    break
        if empty_board:
            hello_message = "Hello player! Welcome to game Othello!"

    # Legal moves to display on the webpage.
    legal_moves = moves_are_legal(DARK, board) if turn_player == DARK else []

    return render_template(
        "index.html",
        board=board,
        turn_player=turn_player,
        move_counter=move_counter,
        game_over=game_over,
        congratulation_message=congratulation_message,
        hello_message=hello_message,
        amount_of_light=amount_of_light,
        amount_of_dark=amount_of_dark,
        legal_moves=legal_moves
    )


@app.route("/game", methods=["POST"])
def game():
    """
    From the webpage, handle the player's submitted move
    sent by POST and update the game state.
    """

    global board, turn_player, move_counter

    if move_counter <= 0:
        return redirect(url_for("idx"))

    r = int(request.form["row"])
    c = int(request.form["column"])

    legal = moves_are_legal(DARK, board)

    # If no legal moves for player then skip to the AI opponent.
    if not legal:
        flash("Dark has no legal moves, AI plays")
        turn_player = LIGHT
        return redirect(url_for("idx"))

    # Check if selected move is legal
    if (r, c) not in legal:
        logger.warning(f"Illegal move attempted at cell: ({r}, {c})")
        flash("The move is illegal, provide a different coordinate")
        return redirect(url_for("idx"))

    # Apply human move
    make_move(DARK, (r, c), board)
    logger.info(f"Human player places the dark piece at ({r}, {c})")
    normalise_board(board)
    move_counter -= 1
    turn_player = LIGHT
    logger.info(f"Now it is a {turn_player.strip()}'s turn")

    return redirect(url_for("idx"))


@app.route("/save_game")
def save_game():
    """
    Save the current game state.
    """

    global board, turn_player, move_counter

    with open(SAVE_FILE, "w", encoding="utf-8") as save:
        json.dump({"board": board, "turn_player": turn_player, "move_counter": move_counter}, save)
        logger.info("Saved successfully to finished_product.json")
    flash("You saved this game successfully!")
    return redirect(url_for("idx"))


@app.route("/load_game")
def load_game():
    """
    Load the previously saved game state.
    """

    global board, turn_player, move_counter

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as load:
            data = json.load(load)
            board = data["board"]
            turn_player = data["turn_player"]
            move_counter = data["move_counter"]
            normalise_board(board)
        logger.info("Loaded successfully from finished_product.json")
        flash("You loaded this game successfully!")
    except FileNotFoundError:
        flash("Unfortunately, we didn't find saved game")
    return redirect(url_for("idx"))

if __name__ == "__main__":
    print("Open this URL: http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)

