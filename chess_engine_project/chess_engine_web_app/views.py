from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from .models import Game

def index(request):
    return render(request, 'chess_engine_web_app/index.html')

def update_game_attributes(request):
    if request.method == 'GET':
        request.session['color'] = request.GET['color']
        request.session['time'] = request.GET['time']

        try:
            game = Game.objects.get(pk=request.session['game_pk'])
        except:
            game = Game()

        game.player_color = request.GET['color']
        game.time = request.GET['time']
        game.save()
        request.session['game_pk'] = game.pk

        print('game_pk: ', request.session['game_pk'])
        request.session.modified = True
        return HttpResponse("Session has been saved")
    else:
        return HttpResponse("Request method is not a GET")

def game(request):
    game_pk = request.session.get('game_pk', None)

    # if any([not color, not time]):
    if game_pk is None:
        return render(request, 'chess_engine_web_app/index.html')

    try:
        game = Game.objects.get(pk=game_pk)
    except:
        return render(request, 'chess_engine_web_app/index.html')

    game.reset_state()

    return render(request, 'chess_engine_web_app/game.html')

def get_next_move(request):
    if request.method == 'GET':
        move = request.GET.get('move', '')

        game_pk = request.session.get('game_pk', None)

        try:
            game = Game.objects.get(pk=game_pk)
        except:
            print('not exists')
            game = Game()

        botMove = game.get_move(move)

        return HttpResponse(botMove)

    else:
        return HttpResponse("Request method is not a GET")