import json
import random
from flask import Flask, render_template, request, redirect, url_for, flash
import logging
from config import SAVE_FILE, DARK, LIGHT, NONE, SECRET_KEY

logging.basicConfig(
    filename="othello_game.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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

    board[3][3] = LIGHT
    board[3][4] = DARK
    board[4][3] = DARK
    board[4][4] = LIGHT
    return board

board = initialise_board()
logger.info("Initialise board with four pieces in the initial positions")
turn_player = DARK
move_counter = 60


vectors = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1), (1, 0), (1, 1)]

def normalise_board(board):
    """Verify board squares have consistent constants."""
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
    row_0, column_0 = position
    if not in_range(row_0, column_0) or board[row_0][column_0] != NONE:
        return False

    enemy = LIGHT if player == DARK else DARK

    for change_r, change_c in vectors:
        r, c = row_0 + change_r, column_0 + change_c
        found_enemy = False

        while in_range(r, c) and board[r][c] == enemy:
            found_enemy = True
            r += change_r
            c += change_c

        if found_enemy and in_range(r, c) and board[r][c] == player:
            return True

    return False

def moves_are_legal(player, board):
    moves = []
    for r in range(8):
        for c in range(8):
            if move_is_legal(player, (r, c), board):
                moves.append((r, c))
    return moves

def make_move(player, position, board):
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
 amount_of_light = 0
 amount_of_dark = 0
 for row in board:
     amount_of_light += row.count(LIGHT)
     amount_of_dark += row.count(DARK)
 return amount_of_light, amount_of_dark

def ai_turn(board):
 moves = moves_are_legal(LIGHT, board)
 if moves:
     return random.choice(moves)
 return None

@app.route("/")
def idx():
    global board, turn_player, move_counter
    normalise_board(board)

    amount_of_light, amount_of_dark = count_pieces(board)
    game_over = False
    congratulation_message = ""

    while True:
        dark_moves = moves_are_legal(DARK, board)
        light_moves = moves_are_legal(LIGHT, board)

        if move_counter <= 0 or (not dark_moves and not light_moves):
            game_over = True
            if amount_of_light > amount_of_dark:
                congratulation_message = "Congratulations, light wins"
            elif amount_of_dark > amount_of_light:
                congratulation_message = "Congratulations, dark wins"
            else:
                congratulation_message = "Tie!"
                logger.info(f"You finished the game, the results are: Winner: {congratulation_message}, Light: {amount_of_light}, Dark: {amount_of_dark}")
            break

        if turn_player == DARK:
            if dark_moves:
                break
            flash("Dark hasn't got legal moves, AI turn")
            turn_player = LIGHT
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
    global board, turn_player, move_counter
    if move_counter <= 0:
        return redirect(url_for("idx"))
    r = int(request.form["row"])
    c = int(request.form["column"])
    legal = moves_are_legal(DARK, board)
    if not legal:
        flash("Dark has no legal moves, AI plays")
        turn_player = LIGHT
        return redirect(url_for("idx"))
    if (r, c) not in legal:
        logger.warning(f"Illegal move attempted at cell: ({r}, {c})")
        flash("The move is illegal, provide a different coordinate")
        return redirect(url_for("idx"))
    make_move(DARK, (r, c), board)
    logger.info(f"Human player places the dark piece at ({r}, {c})")
    normalise_board(board)
    move_counter -= 1
    turn_player = LIGHT
    logger.info(f"Now it is a {turn_player.strip()}'s turn")
    return redirect(url_for("idx"))

@app.route("/save_game")
def save_game():
    global board, turn_player, move_counter
    with open(SAVE_FILE, "w", encoding="utf-8") as save:
        json.dump({"board": board, "turn_player": turn_player, "move_counter": move_counter}, save)
        logger.info("Saved successfully to finished_product.json")
    flash("You saved this game successfully!")
    return redirect(url_for("idx"))

@app.route("/load_game")
def load_game():
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

