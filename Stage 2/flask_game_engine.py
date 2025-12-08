import json
from flask import Flask, render_template, request, redirect,  url_for, flash
from components import initialise_board, legal_move

# Initialise Flask.
app = Flask(__name__)
app.secret_key = "secret_key"

SAVE_FILE = "finished_product.json"

# Set up the board, the first player to move and the maximum number of
# moves within a single game.
board = initialise_board()
move_counter = 60
turn_player = 'Dark '

# 'vectors' holds the coordinates of the ring of squares that surround
# a specific square.
vectors = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1), (1, 0), (1, 1)]

def count_pieces(board):
    """
    Count the total number of Light and Dark pieces in 'board'
    """

    amount_of_light = 0
    amount_of_dark = 0
    for row in board:
        amount_of_light += row.count('Light')
        amount_of_dark += row.count('Dark ')
    return amount_of_light, amount_of_dark

    # Below the root of our web project is defined so that
    # 127.0.0.1 without more '/' elements will come to here
    # in the code.
@app.route("/")
def idx():
    """
    Get the current count of dark and light pieces from the board and render the main page.
    """

    global board, turn_player, move_counter

    amount_of_light, amount_of_dark = count_pieces(board)

    # Set the booleans for end of game and whether a suggested move is legal.
    game_over = False
    move_is_legal = False

    # If the users suggested move is legal then allow it and
    # break from the inner loop and then also outer loop.

    for r in range(8):
        for c in range(8):
            if legal_move(turn_player, (r, c), board):
                move_is_legal = True
                break
        if move_is_legal:
            break

    # End the game if the maximum number of moves have taken place
    # or the move made was illegal.

    if move_counter <= 0 or not move_is_legal:
        game_over = True

    # Look at the game state and set the message to be displayed to
    # the user announcing who won or whether it was a tie.

    congratulation_message = ""
    if game_over:
        if amount_of_light > amount_of_dark:
            congratulation_message = "Congratulations, light wins"
        elif amount_of_dark > amount_of_light:
            congratulation_message = "Congratulations, dark wins"
        else:
            congratulation_message = "Tie!"

    # If the board is empty then this is a new game.
    hello_message = ""
    if move_counter == 60:
        empty_board = True
        for row in board:
            for cell in row:
                if cell != '':
                    empty_board = False
                    break
        if empty_board:
            hello_message = "Hello player! Welcome to the game Othello!"

    # Return to the browser the data it needs to update the display.
    return render_template(
        "index.html",
        board=board,
        turn_player=turn_player,
        move_counter=move_counter,
        game_over=game_over,
        congratulation_message=congratulation_message,
        hello_message= hello_message,
        amount_of_light=amount_of_light,
        amount_of_dark=amount_of_dark
    )


@app.route("/game", methods=["POST"])
def game():
    """
    Handle a player's move and update the board.
    """

    global turn_player, board, move_counter

    # If no moves are left, redirect to main page.
    if move_counter <= 0:
        return redirect(url_for("idx"))

    # Get the row and column entered by the user.
    chosen_row = request.form["row"]
    chosen_column = request.form["column"]

    my_row = int(chosen_row)
    my_column = int(chosen_column)

    # Check if the current player has any legal moves.
    move_is_legal = False
    for r in range(8):
        for c in range(8):
            if legal_move(turn_player, (r, c), board):
                move_is_legal = True
                break
        if move_is_legal:
            break

    # Switch to the other player, if the player has no legal moves.
    if not move_is_legal:
        if turn_player == 'Dark ':
            turn_player = 'Light'
        else:
            turn_player = 'Dark '
        flash("This player has no legal moves, switching to the other player")
        return redirect(url_for("idx"))

    # If the selected move is legal, place the piece and flip outflanked pieces.
    if legal_move(turn_player, (my_row, my_column), board):

        if turn_player =='Light':
                    board[my_row][my_column] = 'Light'
                    enemy = 'Dark '
        else:
            board[my_row][my_column] = 'Dark '
            enemy = 'Light'

        for change_r, change_c in vectors:
            new_r = my_row + change_r
            new_c = my_column + change_c
            outflanked_pieces = []

            while 0 <= new_r < 8 and 0 <= new_c < 8:
                square = board[new_r][new_c]
                if square == enemy:
                    outflanked_pieces.append((new_r, new_c))
                elif square == turn_player:
                    for enemy_r, enemy_c in outflanked_pieces:
                        if turn_player == 'Light':
                            board[enemy_r][enemy_c] = 'Light'
                        else:
                            board[enemy_r][enemy_c] = 'Dark '
                    break
                else:
                    break
                new_r += change_r
                new_c += change_c
        # Make the remaining moves on one less and switch to the next player.
        move_counter -= 1
        if turn_player == 'Dark ':
            turn_player = 'Light'
        else:
            turn_player = 'Dark '
    # Redirect back to refresh the board, after the move is processed.
    return  redirect(url_for("idx"))


@app.route("/save_game")
def save_game():
    """
    Save the current game state.
    """

    global turn_player, board, move_counter
    with open(SAVE_FILE, "w", encoding="utf-8") as save:
        json.dump({"board": board, "turn_player": turn_player, "move_counter": move_counter}, save)
    flash("You saved this game successfully!")
    return  redirect(url_for("idx"))


@app.route("/load_game")
def load_game():
    """
    Load the previously saved game state.
    """

    global turn_player, board, move_counter
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as load:
            data=json.load(load)
            board = data["board"]
            turn_player = data["turn_player"]
            move_counter = data.get("move_counter", 60)
        flash("You loaded this game successfully!")
    except FileNotFoundError:
        flash("Unfortunately, we didn't find the saved game")
    return redirect(url_for("idx"))

if __name__ == "__main__":
    app.run(debug=True)
