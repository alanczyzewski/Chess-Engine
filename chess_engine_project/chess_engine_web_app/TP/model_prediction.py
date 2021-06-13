import numpy as np
import chess
from .data_extraction import fen_to_one_hot, pgn_results, evaluation_perspective
from .model_training import get_model
from tensorflow import keras
model = get_model()
model.load_weights('chess_engine_web_app/TP/model.weights')


class game_runner():
    def __init__(self, model, prediction_method, play_white, play_black, starting_fen=None):
        self.model = model
        self.prediction_method = eval('self.'+prediction_method)
        self.board = chess.Board()
        self.to_move = 'w'
        self.play_white = play_white
        self.play_black = play_black
        self.san = None
        self.starting_fen = starting_fen
        self.evaluation_counter = 0

    def server_response(self, fen, move, player_colour):
        self.board = chess.Board(fen)
        print(move)
        if move != "NaN":
            self.board.push_uci(move)
        if player_colour == 'white':
            self.to_move = 'b'
            self.play_black = True
            self.play_white = False
        else:
            self.to_move = 'w'
            self.play_black = False
            self.play_white = True
        new_move = self.decide_move()[0]
        self.board.push_uci(new_move)
        return new_move, self.board.fen()

    def start_game(self):
        if self.starting_fen is None:
            self.board = chess.Board()
        else:
            self.board = chess.Board(self.starting_fen)

    def get_move(self, san):
        pass
        #self.board.push_uci(san)

    def decide_move(self, method=None):
        if method is None:
            move = self.prediction_method()
        else:
            move = method()
        evaluations_count = self.evaluation_counter
        self.evaluation_counter = 0
        return move, evaluations_count

    def evaluate(self, board=None):
        if board is None:
            board = self.board
        position, colour, _, _, _, _ = board.fen().split(' ')
        if board.can_claim_draw():
            return 0
        if board.result() != '*':
            return pgn_results[board.result()] * evaluation_perspective[colour]
        one_hot = fen_to_one_hot(position, colour)
        input = np.where(np.sum(one_hot, axis=-1) != 0, np.argmax(one_hot, axis=-1) + 1, 0).astype(int)
        evaluation = self.model.predict(input)
        self.evaluation_counter += 1
        #print(evaluation)
        return evaluation

    def standard_flow(self, san=None):
        if self.to_move == 'w':
            if self.play_white:
                move = self.decide_move()[0]
            else:
                move = san
        if self.to_move == 'b':
            if self.play_black:
                move = self.decide_move()[0]
            else:
                move = san
        self.board.push_uci(move)
        print(move, self.board.fen())
        if self.to_move == 'w':
            self.to_move = 'b'
        else:
            self.to_move = 'w'

    # prediction methods

    def shallow_best(self):
        best_evaluation = -np.inf
        best_move = None
        for move in self.board.legal_moves:
            move = str(move)
            b = self.board.copy()
            b.push_uci(move)
            evaluation = self.evaluate(b)
            print(move, evaluation)
            if evaluation > best_evaluation:
                best_evaluation = evaluation
                best_move = move
        return best_move


    def min_max(self):
        worst_response = np.inf
        best_move = None
        for move in self.board.legal_moves:
            move = str(move)
            b = self.board.copy()
            b.push_uci(move)
            best_evaluation = -np.inf
            best_response = None
            for response in b.legal_moves:
                response = str(response)
                bb = b.copy()
                bb.push_uci(response)
                evaluation = self.evaluate(bb)
                if evaluation > best_evaluation:
                    best_evaluation = evaluation
                    best_move = move
                if best_evaluation < worst_response:
                    worst_response = best_evaluation
                    best_move = move
        return best_move



    def beam_search(self, depth, width):
        pass
        '''
        possible_outcomes = [self.board]
        evaluations = []
        first_moves = None
        new_evaluations = []
        new_first_moves = []
        new_outcomes = []
        for i in range(depth):
            for n, b in enumerate(possible_outcomes):
                for move in b.legal_moves:
                    bb = b.copy()
                    bb.push_uci(move)
                    new_evaluations.append(self.evaluate(bb))
                    if first_moves is None:
                        new_first_moves.append(move)
                    else:
                        new_first_moves.append(first_moves[n])
                    new_outcomes.append(bb)
            evaluations = np.array(new_evaluations)
            if evaluations.size > width:
                if i%2 ==0:

                else:
            beam = np.argpartition(evaluations)
            possible_outcomes = np.array(new_outcomes)
            first_moves = np.array(new_first_moves)
            '''

# agent = game_runner(model, 'shallow_best', False, True)
# while True:
#     agent.standard_flow(input())
#     agent.standard_flow(('engine will decide this move'))