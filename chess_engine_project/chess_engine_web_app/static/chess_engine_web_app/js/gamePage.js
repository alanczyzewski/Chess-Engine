const PiecesColor = {
    WHITE: 'white',
    BLACK: 'black'
};

var playerPieces = null;
var timerBot = null;
var timerUser = null;

var board = null;
var $board = $("#board");
var game = null;
var squareToHighlight = null;
var squareClass = 'square-55d63';
var runOutOfTimeLoser = null;


jQuery(function(){
    playerPieces = ((session['color'] == 'white') ? PiecesColor.WHITE : PiecesColor.BLACK);

    var config = {
        pieceTheme: 'static/chess_engine_web_app/chessboardjs-1.0.0/img/chesspieces/wikipedia/{piece}.png',
        position: 'start',
        draggable: true,
        moveSpeed: 'slow',
        snapbackSpeed: 200,
        snapSpeed: 100,
        orientation: playerPieces,
        onDragStart: onDragStart,
        onDrop: onDrop,
        onMoveEnd: onMoveEnd,
        onSnapEnd: onSnapEnd
    };

    game = new Chess();
    board = Chessboard('board', config);

    setClocks();

    $('.' + playerPieces + '-piece').addClass('user-piece');
    if (playerPieces == PiecesColor.BLACK) {
        getNextMove();
    }
});

$('#btnCopy').click(function() {
    var copyDiv = document.getElementById("gamePgn");

    if (document.selection) {
        var range = document.body.createTextRange();
        range.moveToElementText(copyDiv);
        range.select().createTextRange();
        document.execCommand("copy");
    } else if (window.getSelection) {
        var range = document.createRange();
        range.selectNode(copyDiv);
        window.getSelection().addRange(range);
        document.execCommand("copy");
    }
});

function onDragStart (source, piece, position, orientation) {
    // do not pick up pieces if the game is over
    if (game.game_over() || runOutOfTimeLoser != null) {
        return false;
    }

    if (playerPieces === PiecesColor.WHITE && piece.search(/^b/) !== -1) return false;
    else if (playerPieces === PiecesColor.BLACK && piece.search(/^w/) !== -1) return false;
}

function onDrop (source, target) {
    // see if the move is legal
    var move = game.move({
      from: source,
      to: target,
      promotion: 'q' // NOTE: always promote to a queen for example simplicity
    });

    // illegal move
    if (move === null) return 'snapback';

    if (timerUser != null && timerBot != null) {
        timerUser.pause();
        if (!game.game_over()) {
            timerBot.resume();
        }
    }


    // highlight white's move
    removeHighlights('white');
    $board.find('.square-' + source).addClass('highlight-white');
    $board.find('.square-' + target).addClass('highlight-white');

    setTimeout(function() {
        getNextMove(source, target);
    }, 250);
}

function onMoveEnd () {
    $board.find('.square-' + squareToHighlight).addClass('highlight-black');
}

function onSnapEnd () {
    updateBoardAndPgn()
}

function updateBoardAndPgn() {
    board.position(game.fen());
    var pgn = game.pgn({ max_width: 5, newline_char: '<br/>' });

    if (game.in_checkmate()) {
        pgn += '<div class="text-center mt-2">';
        if (game.turn() == 'b') {
            pgn += ' 1 - 0';
        } else {
            pgn += ' 0 - 1';
        }
        pgn += "</div>";
    } else if (game.in_draw()) {
        pgn += '<div class="text-center mt-2">&half; - &half;</div>';
    } else if (runOutOfTimeLoser != null) {
        pgn += '<div class="text-center mt-2">';
        if (runOutOfTimeLoser == 'b') {
            pgn += '1 - 0';
        } else {
            pgn += '0 - 1';
        }
        pgn += "</div>";
    }

    $('#gamePgn').html(pgn);
    $("#gamePgn").scrollTop($("#gamePgn")[0].scrollHeight);
}


function removeHighlights (color) {
    $board.find('.' + squareClass).removeClass('highlight-' + color);
}

function setClocks() {
    if (session['time'] == 'null') {
        $('.clock-component').hide();
        return;
    }

    var timeTab = session['time'].split('|');
    var minutes = parseInt(timeTab[0]);
    var incrementSeconds = null;

    if (timeTab.length > 1) {
        incrementSeconds = timeTab[1];
    }
    $('.clock-value').html((minutes < 10 ? '0' : '') + minutes + ':00');

    var colorUser = ((playerPieces == PiecesColor.WHITE) ? 'w' : 'b')
    var colorBot = ((playerPieces == PiecesColor.WHITE) ? 'b' : 'w')

    timerBot = new Timer(colorBot, 'clock-bot', minutes, incrementSeconds);
    timerUser = new Timer(colorUser, 'clock-user', minutes, incrementSeconds);

    startClock(timerUser);
    startClock(timerBot);
}

function startClock(timer) {
    setTimeout(function() {
        updateClock(timer);
    }, timer.timeGap);
}

function updateClock(timer) {
    timer.update();
    if (timer.currentTime + timer.timeGap <= timer.endTime) {
        setTimeout(function() {
            updateClock(timer);
        }, timer.timeGap);
    }
}

function getNextMove(move_from, move_to) {
    var move = null;
    $.ajax(
    {
        type:"GET",
        url: "/get-next-move",
        data:{
            move: move_from + move_to
        },
        success: function( move )
        {
            if (!game.game_over() && runOutOfTimeLoser == null) {
                makeBotMove(move.substring(0,2), move.substring(2));
                if (timerUser != null && timerBot != null) {
                    timerBot.pause();
                    if (!game.game_over()) {
                        timerUser.resume();
                    }
                }
            }
        }
    });
}

function makeBotMove(source=null, target=null) {

    var possibleMoves = game.moves({
        verbose: true
    })
    console.log('turn:', game.turn())
    // game over
    if (possibleMoves.length === 0) {
        return;
    }

    var move = possibleMoves.find(move => move.from == source && move.to == target);

    game.move(move.san);

    // highlight black's move
    removeHighlights('black');
    $board.find('.square-' + move.from).addClass('highlight-black');
    squareToHighlight = move.to;

    // update the board to the new position
    updateBoardAndPgn()
}

function Timer(color, guiTimerId, minutes, incrementSeconds=null) {
    this.color = color;
    this.guiTimer = $('#' + guiTimerId);
    this.guiTimerValue = $('#' + guiTimerId + '-value');
    this.timeOut = minutes * 60 * 1000;
    this.incrementSeconds = incrementSeconds;
    this.timeGap = 1000;
    this.currentTime = (new Date()).getTime();
    this.endTime = this.currentTime + this.timeOut;
    this.isRunning = false;

    this.update = function() {
        
        if (this.isRunning) {
            this.currentTime += this.timeGap;
            if (this.currentTime >= this.endTime) {
                runOutOfTimeLoser = this.color;
                updateBoardAndPgn();
                console.log('end time');
            }

            if (this.guiTimer.hasClass('clock-active')) {
                this.guiTimer.removeClass('clock-active');
            } else {
                this.guiTimer.addClass('clock-active');
            }
        }

        this.updateGui();
    }

    this.updateGui = function() {
        var time = new Date();
        time.setTime(this.endTime - this.currentTime);
        var minutes = time.getMinutes();
        var seconds = time.getSeconds();
        this.guiTimerValue.html(
            (minutes < 10 ? '0' : '') + minutes
            + ':'
            + (seconds < 10 ? '0' : '') + seconds
        );
    }

    this.pause = function() {
        this.isRunning = false;
        this.guiTimer.removeClass('clock-active');
        if (this.incrementSeconds != null
                && !game.in_checkmate() 
                && !game.in_draw()) {
            this.currentTime -= this.incrementSeconds * 1000;
            this.updateGui();
        }
    }

    this.resume = function() {
        this.isRunning = true;
        this.guiTimer.addClass('clock-active');
    }
}