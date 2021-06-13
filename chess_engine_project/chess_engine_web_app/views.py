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

        # print('color: ' + request.session['color'])
        # print('time: ' + request.session['time'])
        print('game_pk: ', request.session['game_pk'])
        request.session.modified = True
        return HttpResponse("Session has been saved")
    else:
        return HttpResponse("Request method is not a GET")

def game(request):
    # color = request.session.get('color', '')
    # time = request.session.get('time', '')

    game_pk = request.session.get('game_pk', None)


    # if any([not color, not time]):
    if game_pk is None:
        return render(request, 'chess_engine_web_app/index.html')

    try:
        game = Game.objects.get(pk=game_pk)
    except:
        return render(request, 'chess_engine_web_app/index.html')

    game.reset_state()

    # print(request.session.get('color', None))
    # print(request.session.get('time', None))
    print(request.session.get('game_pk', None))

    return render(request, 'chess_engine_web_app/game.html')

def get_next_move(request):
    if request.method == 'GET':
        move = request.GET.get('move', '')

        # TODO send move to engine

        game_pk = request.session.get('game_pk', None)
        print(game_pk)
        print(request.session.get('time', ''))
        print(request.session.get('color', ''))
        print(request.session.get('game_pk', None))

        try:
            game = Game.objects.get(pk=game_pk)
        except:
            print('not exists')
            game = Game()

        print(game)

        botMove = game.get_move(move)

        return HttpResponse(botMove)

        # return HttpResponse('e7e5')

    else:
        return HttpResponse("Request method is not a GET")


# def start_game(request):
#     if request.method == 'GET':
#         color = request.GET.get('color', '')
#         time = request.GET.get('time', '')
#         request.session['color'] = color
#         request.session['time'] = time
#         print('color: ' + color)
#         print('time: ' + time)
#         # response = HttpResponse(status=302)
#         # response['Location'] = '/startGame'
#         # return response
#         return render(request, 'chess_engine_web_app/game.html')

        
#     elif request.method == 'POST':
#         print(request.POST)
#         print(request.POST.get('select-time', ''))

#         return render(request, 'chess_engine_web_app/game.html')
#     else:
#         return HttpResponse("Request method is not a GET")
