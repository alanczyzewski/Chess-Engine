from django.db import models

from .TP import model_prediction, model_training

class Game(models.Model):
    player_color = models.CharField(max_length=5)
    fen = models.CharField(max_length=100, default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    # chessboard = models.CharField(max_length=100)
    # time = models.CharField(max_length=5)
    # moves = models.CharField(max_length=100)
    # move_number = models.IntegerField(default=0)

    def get_move(self, user_move):
        # self.move_number += 1
        # self.save()

        model = model_training.get_model()
        model.load_weights('chess_engine_web_app/TP/model.weights')

        if self.player_color == 'white':
            is_white = False
        else:
            is_white = True

        runner = model_prediction.game_runner(model, 'shallow_best', is_white, not is_white)
        move, fen = runner.server_response(self.fen, user_move, self.player_color)

        self.fen = fen
        self.save()

        return move

    def reset_state(self):
        # self.move_number = 0
        self.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.save()

    def __str__(self):
        return str(self.pk) + '. ' + str(self.player_color) + ' ' + str(self.time)
    
