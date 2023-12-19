"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    X_plays = 0
    O_plays = 0
    for row in [0, 1, 2]:
        for cell in [0, 1, 2]:
            if board[row][cell] == X:
                X_plays += 1
            elif board[row][cell] == O:
                O_plays += 1
    if O_plays < X_plays:
        return O
    return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = []
    for row in [0, 1, 2]:
        for cell in [0, 1, 2]:
            if board[row][cell] == EMPTY:
                possible_actions.append((row, cell))
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = copy.deepcopy(board)
    for row in [0, 1, 2]:
        for cell in [0, 1, 2]:
            if row == action[0] and cell == action[1]:
                if new_board[row][cell] == EMPTY:
                    new_board[row][cell] = player(board)
                else:
                    raise ValueError('Invalid board move')
    return new_board

def check_for_win(row_column_values):
    if row_column_values == [X, X, X]: return X
    if row_column_values == [O, O, O]: return O

def row_win(board):
    for row in [0, 1, 2]:
        cell_values = []
        for cell in [0, 1, 2]:
            if board[row][cell] == EMPTY: break
            cell_values.append(board[row][cell])
        win = check_for_win(cell_values)
        if win: return win

def column_win(board):
    for cell in [0, 1, 2]:
        cell_values = []
        for row in [0, 1, 2]:
            if board[row][cell] == EMPTY: break
            cell_values.append(board[row][cell])
        win = check_for_win(cell_values)
        if win: return win

def perpendicular_win(board):
    line_1 = [board[0][0], board[1][1], board[2][2]]
    line_2 = [board[0][2], board[1][1], board[2][0]]
    win = check_for_win(line_1)
    if win: return win
    win_2 = check_for_win(line_2)
    if win_2: return win_2

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    row_winner = row_win(board)
    if row_winner: return row_winner
    
    column_winner = column_win(board)
    if column_winner: return column_winner

    perpendicular_winner = perpendicular_win(board)
    if perpendicular_winner: return perpendicular_winner
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) or len(actions(board)) == 0: return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    has_winner = winner(board)
    if not has_winner: return 0
    elif has_winner == X: return 1
    else: return -1


def find_current_plays(board, player):
    cur_plays = []
    for row in [0, 1, 2]:
        for cell in [0, 1, 2]:
            if board[row][cell] == player:
                cur_plays.append((row, cell))
    return cur_plays

def get_minmax(board):
    cur_player = player(board)
    minmax = 0
    if cur_player == X: minmax = 1
    else: minmax = -1
    return minmax

def filter_plays(minmax, plays):
    best_plays = list(filter(lambda x: x[0][0] == minmax, plays))

    def get_moves(x):
        return x[0][1]

    if len(best_plays) > 0:
        best_plays.sort(key=get_moves)
        return best_plays
    else:
        # no winning options, go for draw
        draw_plays = list(filter(lambda x: x[0][0] == 0, plays))
        if len(draw_plays) > 0:
            draw_plays.sort(key=get_moves)
            return draw_plays
    # no good options, just return first play
    return [plays[0]]

# considering endgame finds the optimal plays within possible plays
def find_best_plays(board, minmax):
    scores = []
    av_act = actions(board)
    for action in av_act:
        resulting_board = result(board, action)
        score = simulate_optimal_plays(resulting_board, 0)
        if score is not None: scores.append((score, action))

    best_plays = list(filter(lambda x: minmax == x[0][0], scores))
    if len(best_plays) > 0:
        return best_plays
    else:
        # no winning options, go for draw
        draw_plays = list(filter(lambda x: x[0][0] == 0, scores))
        if len(draw_plays) > 0:
            return draw_plays
    # no good options, just return first play
    return scores

def simulate_optimal_plays(board, moves, max_moves=9999):
    if max_moves <= moves: return None
    
    if terminal(board):
        return (utility(board), moves)
    plays = find_best_plays(board, get_minmax(board))
    for p in plays:
        result_board = result(board, p[1])
        return simulate_optimal_plays(result_board, moves + 1, max_moves)


def find_minmax_endgames(board, minmax):
    # from current board state, find best plays for player
    best_plays = find_best_plays(board, minmax)
    plays = []
    max_moves = 9999
    
    for play in best_plays:
        result_board = result(board, play[1])
        moves_count = 1
        # plays is: ((result, num_moves), (play))
        optimal = simulate_optimal_plays(result_board, moves_count, max_moves)
        if optimal is not None:
            max_moves = optimal[1]
            plays.append((optimal, play[1]))
    
    filtered_plays = filter_plays(minmax, plays)
    return filtered_plays
    

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board): return None
    if board == initial_state(): return (0, 0)
    
    play = find_minmax_endgames(board, get_minmax(board))
    return play[0][1]