from components import initialise_board, print_board, legal_move
import random

vectors = [(-1, -1), (-1, 0), (-1, 1),
           (0, -1),          (0, 1),
           (1, -1), (1, 0), (1, 1)]

def cli_coords_input():
    while True:
        try:
            my_row = int(input("Please, provide the number for row:").strip()) - 1
            my_column = int(input("Please, provide the number for column:").strip()) - 1
            if 0 <= my_row < 8 and 0 <= my_column < 8:
                return my_row, my_column
            else:
                print("Coordinates must be between 1 and 8")
        except ValueError:
            print("Wrong format must be (row, column), check again")

def get_legal_moves(turn_player, board):
    moves = []
    for r in range(8):
        for c in range(8):
            if legal_move(turn_player.strip(), (r, c), board):
                moves.append((r, c))
    return moves

def ai_turn(board):
    moves = get_legal_moves('Light', board)
    if moves:
        return random.choice(moves)
    return None

def simple_game_loop():
    board = initialise_board()
    turn_player = 'Dark '
    move_counter = 60

    print("Hello player! Welcome to game Othello! You will be playing with AI, which is Light. Good luck!")

    while move_counter > 0:
        print_board(board)
        print(f"Turn of {turn_player.strip()}")

        legal_moves = get_legal_moves(turn_player, board)
        if not legal_moves:
            print(f"{turn_player.strip()} has no legal moves, switching turn.")
            turn_player = 'Light' if turn_player == 'Dark ' else 'Dark '
            continue

        if turn_player == 'Dark ':
            while True:
                move = cli_coords_input()
                if move in legal_moves:  # Use precomputed legal_moves
                    break
                print("The move is not legal, please provide a different coordinate")
        else:
            move = ai_turn(board)
            print(f"Now AI turn: {move}")

        r, c = move
        board[r][c] = turn_player
        enemy = 'Light' if turn_player == 'Dark ' else 'Dark '

        for change_r, change_c in vectors:
            new_r = r + change_r
            new_c = c + change_c
            outflanked_pieces = []

            while 0 <= new_r < 8 and 0 <= new_c < 8:
                square = board[new_r][new_c].strip()
                if square == enemy.strip():
                    outflanked_pieces.append((new_r, new_c))
                elif square == turn_player.strip():
                    for enemy_r, enemy_c in outflanked_pieces:
                        board[enemy_r][enemy_c] = turn_player
                    break
                else:
                    break
                new_r += change_r
                new_c += change_c

        move_counter -= 1
        if turn_player == 'Dark ':
            turn_player = 'Light'
        else:
            turn_player = 'Dark '

    print("GAME OVER")
    print_board(board)

    amount_of_light = 0
    amount_of_dark= 0

    for r in board:
        amount_of_light += r.count('Light')
        amount_of_dark += r.count('Dark ')

    print(f"Light:{amount_of_light} and Dark:{amount_of_dark}")

    if amount_of_light > amount_of_dark:
        print("Congratulations, light wins")
    elif amount_of_dark > amount_of_light:
        print("Congratulations, dark wins")
    else:
        print("Tie!")

if __name__ == "__main__":
    simple_game_loop()





