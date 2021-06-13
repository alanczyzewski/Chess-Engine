import numpy as np
import chess
import os
import pickle

one_hot_array = np.zeros((13, 13), dtype='i1')
np.fill_diagonal(one_hot_array, 1)

piece_encodings = dict()
for i, c in enumerate('PNBRQK-kqrbnp'):
    piece_encodings[c] = one_hot_array[i]

def fen_to_one_hot(fen, colour):
    one_hot = np.zeros((8, 8, 13), dtype='i1')
    for rank, content in enumerate(fen.split('/')):
        file=0
        for c in content:
            if c.isalpha():
                one_hot[rank, file, :] = piece_encodings[c]
                file += 1
            else:
                file += int(c)
    if colour == 'w':
        return one_hot[np.newaxis, :, :, :]
    else:
        return one_hot[np.newaxis, ::-1, :, ::-1]

def extract_data(filenames, path):
    data = []
    if type(filenames) == str:
        filenames = [filenames]
    for filename in filenames:
        data += extract_games(filename, path)
    return data

def extract_games(filename, path):
    games = []
    f = open(path+'\\'+filename, 'r')
    game_pgn = None
    for line in f.readlines():
        if game_pgn is not None:
            game_pgn += ' ' + line.strip()
        if line[:2] == '1.':
            game_pgn = line.strip()
        if line == '\n' and game_pgn is not None:
            games.append(game_pgn)
            game_pgn = None
    return games

pgn_results = {'1-0': 1,
               '1/2-1/2': 0,
               '0-1': -1,
               '*': 'no official result'}

evaluation_perspective = {'w': 1,
                          'b': -1}

def get_positions(pgn):
    board = chess.Board()
    split_pgn = pgn.split(' ')
    try:
        result = pgn_results[split_pgn[-2]]
    except:
        return []
    if result == 'no official result':
        return []
    moves = split_pgn[:-3]
    try:
        moves[::2] = [move.split('.')[1] for move in moves[::2]]
    except:
        return []
    positions = []
    for move in moves:
        if move:
            board.push_san(move)
            positions.append(board.fen())
    labels = np.linspace(0, result, len(positions))
    return [pair for pair in zip(positions, labels)]



if __name__ == '__main__':
    path = 'pgn'
    print(os.listdir(path))
    game_data = extract_data(os.listdir(path), path)
    position_embeddings = []
    labels = []

    for game in game_data:
        for position in get_positions(game):
            fen_data = position[0].split(' ')
            position_embeddings.append(fen_to_one_hot(fen_data[0], fen_data[1]))
            labels.append(position[1]*evaluation_perspective[fen_data[1]])
    with open('data.pickle', 'wb') as d:
        pickle.dump(np.concatenate(position_embeddings), d)
    with open('labels.pickle', 'wb') as l:
        pickle.dump(np.array(labels), l)