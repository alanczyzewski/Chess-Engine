from django.db import models

class Game(models.Model):
    player_color = models.CharField(max_length=5)
    time = models.CharField(max_length=5)
    # moves = models.CharField(max_length=100)
    move_number = models.IntegerField(default=0)

    def get_move(self, user_move):
        self.move_number += 1
        self.save()

        # white win
        
        if self.player_color == 'white':
            if self.move_number == 1:
                return 'e7e5'
            elif self.move_number == 2:
                return 'd7d6'
            elif self.move_number == 3:
                return 'c7c5'
            elif self.move_number == 4:
                return 'a7a5'
            elif self.move_number == 5:
                return 'b7b5'
            elif self.move_number == 6:
                return 'h7h5'
            
        else:
            if self.move_number == 1:
                return 'e2e4'
            elif self.move_number == 2:
                return 'f1c4'
            elif self.move_number == 3:
                return 'd1f3'
            elif self.move_number == 4:
                return 'f3f7'
        
        # # black win

        # if self.player_color == 'white':
        #     if self.move_number == 1:
        #         return 'e7e5'
        #     elif self.move_number == 2:
        #         return 'd8h4'
        # else:
        #     if self.move_number == 1:
        #         return 'f2f3'
        #     elif self.move_number == 2:
        #         return 'g2g4'

    def reset_state(self):
        self.move_number = 0
        self.save()

    def __str__(self):
        return str(self.pk) + '. ' + str(self.player_color) + ' ' + str(self.time)
    
