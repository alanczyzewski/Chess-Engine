import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import tensorflow as tf
import numpy as np
import chess
from .data_extraction import fen_to_one_hot, pgn_results, evaluation_perspective
from .model_training import get_model
from dataclasses import dataclass
from typing import List, Any, Callable
model = get_model()
model.load_weights('chess_engine_web_app/TP/tempw3')





@dataclass
class Tree:
    board: chess.Board
    height: int
    next: List['Tree'] = None
    depth: int = 0
    estimator: Any = None
    tree_value_func: Callable = None
    _value: float = None
    _index: int = None
    _tree_value: float = None
    move: str = None

    def push_board_obtain_index(self, l: List):
        self._index = len(l)
        l.append(self.board)
        if self.next is not None:
            for n in self.next:
                n.push_board_obtain_index(l)


    def get_value(self):
        assert self._index is not None
        if self._value is None:
            self._value = self.estimator.values[self._index]

        if self.depth%2==0:
            return self._value
        else:
            return -self._value

    @staticmethod
    def generic_tree_value_func(tree : 'Tree'):
        if tree.next is None:
            return tree.get_value()
        if tree.depth%2==0:
            val= max(tree.next, key=lambda x: x.get_tree_value()).get_tree_value()
        else:
            val = min(tree.next, key=lambda x: x.get_tree_value()).get_tree_value()
        inner_val = tree.get_value()
        return val + inner_val


    def get_tree_value(self):
        if self._tree_value is None:
            self._tree_value = self.tree_value_func(self)
        return self._tree_value
    def get_best_child(self):
        assert self.next is not None
        best_child = max(self.next, key=lambda x: x.get_tree_value())
        return best_child

    def generate_all_next(self):
        next_moves = []
        for move in self.board.legal_moves:
            move = str(move)
            b = self.board.copy()
            b.push_uci(move)
            next_moves.append(Tree(board=b, next=None, depth=self.depth+1, height=self.height-1, estimator=self.estimator, tree_value_func=self.tree_value_func, move=move))
        self.next = next_moves

    def __post_init__(self):
        if self.height > 0:
            self.generate_all_next()


@dataclass
class Estimator:
    _estimator: Any
    boards: List = None
    values: np.ndarray = None

    def obtain_boards_from_tree(self, tree: Tree):
        if self.boards is None:
            self.boards = []
        tree.push_board_obtain_index(self.boards)

    def batch_evaluate(self):
        assert self.boards is not None
        inputts = []
        for board in self.boards:
            position, colour, _, _, _, _ = board.fen().split(' ')
            if board.can_claim_draw():
                return 0
            if board.result() != '*':
                return pgn_results[board.result()] * evaluation_perspective[colour]
            one_hot = fen_to_one_hot(position, colour)
            inputt = np.where(np.sum(one_hot, axis=-1) != 0, np.argmax(one_hot, axis=-1) + 1, 0).astype(int)
            inputts.append(inputt)
        self.values = self._estimator.predict(np.array(inputts)[:, 0])


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

    def batch_evaluate(self, boards):
        inputts = []
        for board in boards:
            position, colour, _, _, _, _ = board.fen().split(' ')
            if board.can_claim_draw():
                return 0
            if board.result() != '*':
                return pgn_results[board.result()] * evaluation_perspective[colour]
            one_hot = fen_to_one_hot(position, colour)
            inputt = np.where(np.sum(one_hot, axis=-1) != 0, np.argmax(one_hot, axis=-1) + 1, 0).astype(int)
            inputts.append(inputt)
        return self.model.predict(np.array(inputts)[:, 0])


    def evaluate(self, board=None):
        if board is None:
            board = self.board
        position, colour, _, _, _, _ = board.fen().split(' ')
        if board.can_claim_draw():
            return 0
        if board.result() != '*':
            return pgn_results[board.result()] * evaluation_perspective[colour]
        one_hot = fen_to_one_hot(position, colour)
        inputt = np.where(np.sum(one_hot, axis=-1) != 0, np.argmax(one_hot, axis=-1) + 1, 0).astype(int)
        evaluation = self.model.predict(inputt)
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

    def server_response(self, fen, move, player_colour):
        self.board = chess.Board(fen)
        if move != "NaN":
            self.board.push_uci(move)
        new_move = self.decide_move()[0]
        self.board.push_uci(new_move)
        return new_move, self.board.fen()

    def shallow_best(self):
        best_evaluation = np.inf
        best_move = None
        for move in self.board.legal_moves:
            move = str(move)
            b = self.board.copy()
            b.push_uci(move)
            evaluation = self.evaluate(b)
            print(move, evaluation)
            if evaluation < best_evaluation:
                best_evaluation = evaluation
                best_move = move
        return best_move


    def min_max_tree(self):
        est = Estimator(self.model)
        tree = Tree(self.board, 2, estimator=est, tree_value_func=Tree.generic_tree_value_func)
        est.obtain_boards_from_tree(tree)
        print("eval now")
        est.batch_evaluate()
        best_move = tree.get_best_child().move
        return best_move

    def min_max(self):
        worst_response = -np.inf
        best_move = None
        for move in self.board.legal_moves:
            move = str(move)
            b = self.board.copy()
            b.push_uci(move)
            best_evaluation = np.inf
            best_response = None
            boards = []
            for response in b.legal_moves:
                response = str(response)
                bb = b.copy()
                bb.push_uci(response)
                # evaluation = self.evaluate(bb)
                boards.append(bb)

                # if evaluation < best_evaluation:
                #     best_evaluation = evaluation
                #     best_move = move
            # baseline_eval = self.batch_evaluate([b])
            evals = self.batch_evaluate([b]+boards)#, black=True)
            baseline_eval = evals[0]
            evals = evals[1:]
            evals -= baseline_eval
            best_evaluation = np.min(evals)
            if best_evaluation > worst_response:
                worst_response = best_evaluation
                best_move = move
        return best_move

    def generalized_min_max(self, depth):
        pass

    def recurrent_position_tracker(self, depth, board=None, prune=None):
        if board is None:
            board = self.board
        position_stride = []
        position_stride.append('in')
        for move in board.legal_moves:
            b = board.copy()
            move = str(move)
            b.push_uci(move)
            position_stride.append(move)
            if depth >= 2:
                position_stride += self.recurrent_position_tracker(depth-1, b)
            position_stride.append('out')


# agent = game_runner(model, 'min_max_tree', False, True)
# while True:
#     agent.standard_flow(input())
#     agent.standard_flow(('engine will decide this move'))