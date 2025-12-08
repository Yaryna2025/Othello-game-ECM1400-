from components import initialise_board, print_board, legal_move


def cli_coords_input():
    """
    Obtain from the player the row and column in which they want to place
    their next piece.
    """

    while True:
        try:
            my_row = int(input("Please, provide the row number:").strip())-1
            my_column = int(input("Please, provide the column number:").strip())-1
            if 0 <= my_row < 8 and 0 <= my_column < 8:
                return (my_row, my_column)
            else:
                print("Incorrect, coordinates must be between 1 and 8")
        except ValueError:
            print("Wrong format must be (row, column), check again")

def simple_game_loop():
    """
    The function sets up the game and welcomes the user.
    """

    print("Hello player! Welcome to the game Othello!")

    board = initialise_board()
    move_counter = 60
    turn_player = 'Dark '

    vectors = [(-1, -1), (-1, 0), (-1,1),
                (0, -1),          (0,1),
                (1, -1), (1, 0), (1,1)]

    # Below is the main game loop that continues until the maximum
    # number of moves has taken place or the board is full.
    while move_counter > 0:
        print_board(board)
        print(f"Turn of {turn_player}")

        move_is_legal = False
        for r in range(8):
            for c in range(8):
                if legal_move(turn_player.strip(), (r, c), board):
                    move_is_legal = True
                    break
            if move_is_legal:
                break

        if not move_is_legal:
            print("This player has no legal moves, switching to the other player")
            if turn_player =='Dark ':
                turn_player='Light'
            else:
                turn_player='Dark '
            continue

        while True:
            move=cli_coords_input()
            if legal_move(turn_player.strip(), move, board):
                break
            print("The move is not legal, please provide a different coordinate")

        r,c = move

        # Here is where we switch users after a legal move has been completed.
        if turn_player =='Light':
            board[r][c] = 'Light'
            enemy = 'Dark'
        else:
            board[r][c] = 'Dark '
            enemy = 'Light'

        # Below we flip the colour of outflanked pieces.
        for change_r, change_c in vectors:
            new_r = r + change_r
            new_c = c + change_c
            outflanked_pieces = []

            while 0 <= new_r < 8 and 0 <= new_c < 8:
                square = board[new_r][new_c].strip()

                if square == enemy:
                    outflanked_pieces.append((new_r, new_c))

                elif square == turn_player.strip():
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

        # Reduce the move counter that is checked in the main
        # game loop by one. The loop will exit when the maximum
        # number of moves have taken place.
        move_counter -=1

        if turn_player == 'Dark ':
            turn_player = 'Light'
        else:
            turn_player = 'Dark '

    print("GAME OVER")
    print_board(board)

    amount_of_light = 0
    amount_of_dark= 0

    # Calculate the final count of pieces for LIGHT and DARK.
    for r in board:
        amount_of_light += r.count('Light')
        amount_of_dark += r.count('Dark ')

    print(f"Light:{amount_of_light} and Dark:{amount_of_dark}")

    # Output a message to say who won the game.
    if amount_of_light > amount_of_dark:
        print("Congratulations, light wins")
    elif amount_of_dark > amount_of_light:
        print("Congratulations, dark wins")
    else:
        print("Tie!")

if __name__ == "__main__":
    simple_game_loop()
