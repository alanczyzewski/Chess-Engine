from django.db import models

from .TP import model_prediction, model_training

class Game(models.Model):
    player_color = models.CharField(max_length=5)
    fen = models.CharField(max_length=100, default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')


    def get_move(self, user_move):

        model = model_training.get_model()
        model.load_weights('chess_engine_web_app/TP/tempw3')

        if self.player_color == 'white':
            is_white = False
        else:
            is_white = True

        runner = model_prediction.game_runner(model, 'min_max_tree', is_white, not is_white)
        move, fen = runner.server_response(self.fen, user_move, self.player_color)

        self.fen = fen
        self.save()

        return move

    def reset_state(self):
        self.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.save()

    def __str__(self):
        return str(self.pk) + '. ' + str(self.player_color) + ' ' + str(self.fen)
    