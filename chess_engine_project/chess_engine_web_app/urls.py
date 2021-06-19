from django.urls import path
from . import views

app_name = 'chess_engine_web_app'

urlpatterns = [
    path('', views.index, name='home'),
    path('play', views.game, name='game'),
    path('update-game-attributes', views.update_game_attributes, name='update_game_attributes'),
    path('get-next-move', views.get_next_move, name='get_next_move')
]
