def initialise_board(size=8):
    """
    This function will initialise the board and other key
    variables used throughout the code.
    """

    state_1='Light'
    state_2='Dark '
    state_3='None '

    # 'board' holds the current state of the game in progress.
    board = []

    # Below the board is constructed.
    for r in range(size):
        row = []
        for c in range(size):
            row.append(state_3)
        board.append(row)

    # Determine central positions.
    center_left_top = size//2-1
    center_right_bottom = size//2

    # Here I initialise the four pieces with their positions as
    # directed by the rules of Othello.
    board[center_left_top][center_left_top] = state_1
    board[center_left_top][center_right_bottom] = state_2
    board[center_right_bottom][center_left_top] = state_2
    board[center_right_bottom][center_right_bottom] = state_1

    return board


def print_board(board):
    """
    This function outputs the state of the 'board' variable
    that holds the current positions for each piece.
    """

    size = len(board)
    print(" ", end="")

    for c in range(size):
        print(f"{c+1:3}", end=" ")
    print()
    for r in range(size):
        print(f"{r+1}", end=" ")
        for c in range(size):
            square = board[r][c].strip()
            if square == "Light":
                print("[L]", end=" ")
            elif square == "Dark":
                print("[D]", end=" ")
            else:
                print("[*]", end=" ")
        print()


def legal_move(colour, coord, board):
    """
    This function checks whether the coordinates of a suggested move
    are legal based on the current board state and the colour of the
    piece to be played.
    """

    size = len(board)
    r,c=coord

    if colour =='Light':
        enemy='Dark'
    else:
        enemy='Light'

    if board[r][c].strip() != 'None':
        return False

    # 'vectors' defines the coordinates of all adjacent game squares.
    vectors = [(-1, -1), (-1, 0), (-1,1),
                (0, -1),          (0,1),
                (1, -1), (1, 0), (1,1)]

    # The loop below searches for the opponent's pieces to ensure the
    # suggested move is legal.
    for change_r, change_c in vectors:
        new_r = r + change_r
        new_c = c + change_c
        found_enemy = False

        while 0 <= new_r < size and 0 <= new_c < size:
            square = board[new_r][new_c].strip()
            if square == enemy:
                found_enemy = True
            elif square == colour:
                if found_enemy:
                    return True
                break
            else:
                break

            new_r += change_r
            new_c += change_c

    return False
