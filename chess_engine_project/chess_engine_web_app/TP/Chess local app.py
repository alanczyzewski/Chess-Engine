import pygame

pygame.init()

win = pygame.display.set_mode((640, 640))
pygame.display.set_caption("Chess")

blk = (0, 0, 0)
wht = (255, 255, 255)
grn = (0, 255, 0)
blu = (0, 0, 255)
red = (255, 0, 0)
crm = (255, 253, 208)
brw = (150, 75, 0)

board = dict()

players = []

fps = 30
game_on = True

check = False
checklist = []

pawn_shade_tiles = []

#sprites

sprites = []
for i in range(12):
    sprite = pygame.image.load('sprites/sprite' + str(i) + '.png')
    sprites.append(sprite)

sprite_index = dict()
sprite_index["<class '__main__.King'>"] = 0
sprite_index["<class '__main__.Queen'>"] = 1
sprite_index["<class '__main__.Bishop'>"] = 2
sprite_index["<class '__main__.Knight'>"] = 3
sprite_index["<class '__main__.Rook'>"] = 4
sprite_index["<class '__main__.Pawn'>"] = 5
#directions
#up, down, left, right, NE, NW, SW, SE
basic_directions = ((0, 1), (0, -1), (-1, 0), (1, 0))
diagonal_directions = ((1, 1), (-1, 1), (-1, -1), (1, -1))
all_directions = basic_directions + diagonal_directions

def revert(tup):
    return tuple(-1 * term for term in tup)

def tupad(tup1, tup2):
    return tuple(sum(pair) for pair in zip(tup1, tup2))

def tupsub(tup1, tup2):
    return tupad(tup1, revert(tup2))

def list_product(list1, list2):
    product = []
    for i in list1:
        if i in list2:
            product.append(i)
    return product
    ## return [el for el in list1 if el in list2]

#switch turns

def player_switch():
    global active_player
    active_player.is_active = False
    active_player.opponent.is_active = True
    active_player = active_player.opponent

#classic piece ranges
def step(home, direction):
    scope = tupad(home, direction)
    if scope in board:
        return [board[scope]]
    else:
        return []

def barrage(home, direction):
    scope = tupad(home, direction)
    targets = []
    search_on = True
    while scope in board and search_on:
        if board[scope].piece is None:
            targets.append(board[scope])
        else:
            targets.append(board[scope])
            search_on = False
        scope = tupad(scope, direction)
    return targets

#king uncovering check
def align(piece1, piece2):
    return piece1.x == piece2.x or piece1.y == piece2.y or abs(piece1.x - piece2.x) == abs(piece1.y - piece2.y)

def royal_lockdown(piece, allowed_targets):
    """Disables the moves which would expose the king to enemy pieces, returning the list of allowed moves only"""
    king = piece.player.king
    royal_duo = royal_march(king, align_direction(king, piece))
    palace = royal_lane(king, align_direction(king, piece))
    if len(royal_duo) == 2:
        royal_guard, royal_assassin = royal_duo
        if royal_guard == piece and royal_assassin.player == piece.player.opponent:
            if align_direction(king, piece) in diagonal_directions:
                if type(royal_assassin) == Queen or type(royal_assassin) == Bishop:
                    allowed_targets = list_product(allowed_targets, palace)
            else:
                if type(royal_assassin) == Queen or type(royal_assassin) == Rook:
                    allowed_targets = list_product(allowed_targets, palace)
    return allowed_targets

def signum(n):
    if n > 0:
        return 1
    if n < 0:
        return -1
    else:
        return 0

def align_direction(king, another):
    return (signum(another.x - king.x), signum(another.y - king.y))

def royal_march(king, direction):
    """Returns the 2 first pieces from the king in a given direction (look: align_direction
    If the first one is own, and the other is enemy, if enemy piece is the right type, the firts one
    must stay on the line to cover the king - on the royal lane"""
    home = (king.x, king.y)
    scope = tupad(home, direction)
    pieces = []
    while scope in board and len(pieces) < 2:
        if board[scope].piece is not None:
            pieces.append(board[scope].piece)
        scope = tupad(scope, direction)
    return pieces

def royal_lane(king, direction):
    """Iterates just like the royal march, but returns tiles on the way"""
    home = (king.x, king.y)
    scope = tupad(home, direction)
    pieces = []
    tiles = []
    while scope in board and len(pieces) < 2:
        tiles.append(board[scope])
        if board[scope].piece is not None:
            pieces.append(board[scope].piece)
        scope = tupad(scope, direction)
    return tiles

def check_guarding_tiles(king, chechking_piece):
    direction = align_direction(king, chechking_piece)
    return royal_oppression(king, direction)

def royal_oppression(king, direction):
    """Royal lane variant for check situation (royal lane is for prevention of uncovering own king),
    refers to a situation with the king is threatened by a single non-knight piece"""
    home = (king.x, king.y)
    scope = tupad(home, direction)
    pieces = []
    tiles = []
    while scope in board and len(pieces) == 0:
        tiles.append(board[scope])
        if board[scope].piece is not None:
            pieces.append(board[scope].piece)
        scope = tupad(scope, direction)
    return tiles

def castling_march(king, direction):
    home = (king.x, king.y)
    scope = tupad(home, direction)
    pieces = []
    while scope in board and len(pieces) < 1:
        if board[scope].piece is not None:
            pieces.append(board[scope].piece)
        scope = tupad(scope, direction)
    return pieces

def castling_lane(king, direction):
    """The 2 tiles that must not be threatened if you mean to castle"""
    home = (king.x, king.y)
    scope = tupad(home, direction)
    tiles = []
    for i in range(2):
        tiles.append(board[scope])
        scope = tupad(scope, direction)
    return tiles



#classes
class Tile():
    """Represents a tile on the board"""

    def __init__(self, x ,y):
        self.x = x
        self.y = y
        if (x+y)%2 == 1:
            self.colour = crm
        else:
            self.colour = brw
        board[(x, y)] = self
        self.piece = None
        self.is_active = False
        self.is_available = False
        self.pawn_shade = None


    def is_threatened(self, enemy_player):
        for piece in enemy_player.pieces:
            if self in piece.targets():
                return True
        return False

    def draw(self):
        pygame.draw.rect(win, self.colour, (-80 + 80 * self.x, 640 - 80 * self.y, 80, 80))

    def highlight(self, colour):
        pygame.draw.rect(win, colour, (-80 + 80 * self.x, 640 - 80 * self.y, 80, 80))
        pygame.draw.rect(win, self.colour, (-75 + 80 * self.x, 645 - 80 * self.y, 70, 70))

class Player():
    """Represents a player"""

    def __init__(self, colour, name):
        self.colour = colour
        self.pieces = []
        self.king = None
        players.append(self)
        self.opponent = None
        self.is_active = False
        self.name = name

    def is_opponent(self, other):
        return self.colour != other.colour

class Piece():
    """Represents the basic idea of a chess piece"""

    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.player = player
        self.colour = self.player.colour
        self.tile = board[x, y]
        self.tile.piece = self
        player.pieces.append(self)
        #relative directions
        if player.colour == wht:
            #self.basic_directions = basic_directions
            #self.diagonal_directions = diagonal_directions
            self.up, self.down, self.left, self.right = basic_directions
            self.NE, self.NW, self.SW, self.SE = diagonal_directions
        else:
            # self.basic_directions = (revert(direction) for direction in basic_directions)
            # self.diagonal_directions = (revert(direction) for direction in diagonal_directions)
            self.up, self.down, self.left, self.right = (revert(direction) for direction in basic_directions)
            self.NE, self.NW, self.SW, self.SE = (revert(direction) for direction in diagonal_directions)
        self.never_moved = True
        sprite_number = sprite_index[str(type(self))]
        if self.player.colour == blk:
            sprite_number += 6
        self.sprite = sprites[sprite_number]
        if type(self) == King:
            self.player.king = self
        is_captured = False
        #print(self.up, self.down, self.left, self.right)

    def is_opponent(self, other):
        return self.colour != other.colour

    def targets(self):
        return []

    def kill(self):
        self.x, self.y = 0, 0
        self.player.pieces.remove(self)
        self.player = None #?
        self.tile.piece = None #?
        self.tile = None
        self.is_captured = True

    def change_tile(self, newtile):
        self.x, self.y = newtile.x, newtile.y
        self.tile.piece = None
        self.tile.is_active = False
        newtile.piece = self
        self.tile = newtile
        self.never_moved = False


    def allowed_targets(self):
        allowed_targets = []
        if type(self) == King:
            for target in self.targets():
                if target.piece is None:
                    allowed_targets.append(target)
                elif target.piece.player == self.player.opponent:
                    allowed_targets.append(target)
                if self.never_moved and not check:
                    for direction in [self.left, self.right]:
                        if len(castling_march(self, direction)) != 0:
                            supposed_rook = castling_march(self, direction)[0]
                            if type(supposed_rook) == Rook and supposed_rook.never_moved: #no enemy rook check needed
                                castling_allowed = True
                                for piece in self.player.opponent.pieces:
                                    for tile in castling_lane(self, direction):
                                        if tile in piece.targets():
                                            castling_allowed = False
                                if castling_allowed:
                                    castling_tile_coordinates = tupad((self.x, self.y), tupad(direction, direction))
                                    allowed_targets.append(board[castling_tile_coordinates])
                for piece in self.player.opponent.pieces:
                    for target in piece.targets():
                        if target in allowed_targets:
                            allowed_targets.remove(target)
        elif type(self) != Pawn:
            for target in self.targets():
                if target.piece is None:
                    allowed_targets.append(target)
                elif target.piece.player == self.player.opponent:
                    allowed_targets.append(target)
            if align(self, self.player.king):
                allowed_targets = royal_lockdown(self, allowed_targets)
            if check:
                if len(checklist) >= 2:
                    allowed_targets.clear()
                else:
                    checking_piece = checklist[0]
                    if type(checking_piece) == Knight:
                        allowed_targets = list_product(allowed_targets, [checking_piece.tile])
                    else:
                        allowed_targets = list_product(allowed_targets,
                                                       check_guarding_tiles(self.player.king, checklist[0]))
        else:
            for target in self.targets():
                if target.piece is not None:
                    if target.piece.player == self.player.opponent:
                        allowed_targets.append(target)
            home = (self.x, self.y)
            step_forward = tupad(home, self.up)
            if step_forward in board:
                if board[step_forward].piece is None:
                    allowed_targets.append(board[step_forward])
                    another_step = tupad(step_forward, self.up)
                    if another_step in board:
                        if board[another_step].piece is None and self.never_moved:
                            allowed_targets.append(board[another_step])
            for direction in [self.NW, self.NE]:
                scope = tupad((self.x, self.y), direction)
                if scope in board:
                    if board[scope].pawn_shade is not None:
                        allowed_targets.append(board[scope])
            if align(self, self.player.king):
                allowed_targets = royal_lockdown(self, allowed_targets)
            if check:
                if len(checklist) >= 2:
                    allowed_targets.clear()
                else:
                    checking_piece = checklist[0]
                    if type(checking_piece) == Knight:
                        allowed_targets = list_product(allowed_targets, [checking_piece.tile])
                    else:
                        allowed_targets = list_product(allowed_targets,
                                                       check_guarding_tiles(self.player.king, checklist[0]))

        return allowed_targets

class Rook(Piece):
    """Represents a rook"""

    def targets(self):
        home = (self.x, self.y)
        targets = []
        for direction in basic_directions:
            targets += barrage(home, direction)
        return targets

class Bishop(Piece):
    """Represents a bishop"""

    def targets(self):
        home = (self.x, self.y)
        targets = []
        for direction in diagonal_directions:
            targets += barrage(home, direction)
        return targets

class Queen(Piece):
    """Represents the queen"""

    def targets(self):
        home = (self.x, self.y)
        targets = []
        for direction in all_directions:
            targets += barrage(home, direction)
        return targets

class King(Piece):
    """Represents the king"""

    def targets(self):
        home = (self.x, self.y)
        targets = []
        for direction in all_directions:
            targets += step(home, direction)
        return targets

class Knight(Piece):
    """Represents a knight"""

    def targets(self):
        home = (self.x, self.y)
        targets = []
        for diag in diagonal_directions:
            for basic in basic_directions:
                if diag[0] == basic[0] or diag[1] == basic[1]:
                    scope = tupad(home, tupad(diag, basic))
                    if scope in board:
                        targets.append(board[scope])
        return targets

class Pawn(Piece):
    """Represents a pawn"""

    def targets(self):
        home = (self.x, self.y)
        targets = []
        for direction in (self.NE, self.NW):
            targets += step(home, direction)
        return targets



# display-related functions

# line 155 (this + 6) guardian after 'and' probably not needed in the end, conditionals to improve
def board_display():
    for address in board:
        tile = board[address]
        tile.draw()
        if tile.is_available:
            if tile.piece is not None and active_piece is not None:
                if active_piece.is_opponent(tile.piece):
                    tile.highlight(red)
                else:
                    tile.highlight(grn)
            else:
                if tile.pawn_shade is not None and type(active_piece) == Pawn:
                    tile.highlight(red)
                else:
                    tile.highlight(grn)
        if check:
            active_player.king.tile.highlight(red)
        if tile.is_active:
            tile.highlight(blu)


def pieces_display():
    for player in players:
        for piece in player.pieces:
            win.blit(piece.sprite, (-80 + 80 * piece.x, 640 - 80 * piece.y))


def frame_display():
    win.fill(blk)
    board_display()
    pieces_display()
    pygame.display.update()

def promotion_frame_display():
    if active_player == white:
        colour = crm
    else:
        colour = brw
    win.fill(colour)
    pygame.draw.rect(win, blk, (0, 315, 640, 10))
    pygame.draw.rect(win, blk, (315, 0, 10, 640))
    if active_player == white:
        base_number = 1
    if active_player == black:
        base_number = 7
    for i in range(4):
        win.blit(sprites[base_number + i], (120 + 320 * (i%2), 120 + 320 * (i//2)))
    pygame.display.update()

#players initialization

white = Player(wht, 'white')
black = Player(blk, 'black')
white.opponent = black
black.opponent = white
active_player = white
white.is_active = True


#board initialization

active_piece = None
for i in range(1, 9):
    for j in range(1, 9):
        Tile(i, j)



#testing box

#pygame.time.delay(4000)
#board[(5, 4)].is_available = True
#board[(5, 3)].is_available = True
#board[(5, 2)].is_active = True


#pieces initialization

Rook(1, 1, white)
Knight(2, 1, white)
Bishop(3, 1, white)
Queen(4, 1, white)
King(5, 1, white)
Bishop(6, 1, white)
Knight(7, 1, white)
Rook(8, 1, white)
for i in range(1,9):
    Pawn(i, 2, white)

Rook(1, 8, black)
Knight(2, 8, black)
Bishop(3, 8, black)
Queen(4, 8, black)
King(5, 8, black)
Bishop(6, 8, black)
Knight(7, 8, black)
Rook(8, 8, black)
for i in range(1,9):
    Pawn(i, 7, black)
#active_piece = board[(4, 1)].piece
#board[(4, 1)].is_active = True
#for target in active_piece.targets():
 #   target.is_available = True


#mainloop not display-related functions
def select(piece):
    global active_piece
    if active_piece is not None:
        active_piece.tile.is_active = False
        active_piece = None #redundant line 99,9%
        for target in board:
            board[target].is_available = False
    active_piece = piece
    piece.tile.is_active = True

def move(active_piece, selected_tile):
    if selected_tile.piece is not None:
        selected_tile.piece.kill()
    if type(active_piece) == King: #guarded somewhere else
        if selected_tile.x - active_piece.x == 2:
            for piece in active_piece.player.pieces:
                if type(piece) == Rook and piece.x > selected_tile.x:
                    piece.change_tile(board[piece.x - 2, piece.y])
        if active_piece.x - selected_tile.x == 2:
            for piece in active_piece.player.pieces:
                if type(piece) == Rook and piece.x < selected_tile.x:
                    piece.change_tile(board[piece.x + 3, piece.y])
    if type(active_piece) == Pawn: #mainloop shade "miss the timing" prevents killing own pawns
        if selected_tile.pawn_shade is not None:
            selected_tile.pawn_shade.kill()
    if type(active_piece) == Pawn:
        if abs(active_piece.y - selected_tile.y) == 2:
            pawn_shade_tile = board[(active_piece.x, int((active_piece.y + selected_tile.y) / 2))]
            pawn_shade_tile.pawn_shade = active_piece
            pawn_shade_tiles.append(pawn_shade_tile)
    inactivate_targets()
    active_piece.change_tile(selected_tile)
    inactivate_piece()

def inactivate_piece():
    global active_piece
    active_piece.is_active = False
    active_piece = None

def inactivate_targets():
    for target in board:
        board[target].is_available = False

def check_check():
    global check
    checklist.clear()
    for piece in active_player.opponent.pieces:
        if active_player.king.tile in piece.targets():
            checklist.append(piece)
    check = len(checklist) > 0

def game_over_check():
    available_move_exists = False
    for piece in active_player.pieces:
        if len(piece.allowed_targets()) > 0:
            available_move_exists = True
    if not available_move_exists:
        if check:
            print("Checkmate! " + active_player.opponent.name.capitalize() + ' wins!')
        else:
            print("Stalemate! It's a draw!")

def promotion_check():
    for piece in active_player.pieces:
        if type(piece) == Pawn and piece.y in [1, 8]:
            promotion(piece)
#other loops
def promotion(pawn):
    global game_on
    promotion_on = True
    x, y = pawn.x, pawn.y
    player = active_player
    chosen_piece = None
    while promotion_on:
        pygame.time.delay(int(1000 / fps))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                choice = position[0]//320 + 2*(position[1]//320)
                print(choice)
                if choice == 0:
                    chosen_piece = Queen
                if choice == 1:
                    chosen_piece = Bishop
                if choice == 2:
                    chosen_piece = Knight
                if choice == 3:
                    chosen_piece = Rook
                promotion_on = False
            if event.type == pygame.QUIT:
                promotion_on = False
                game_on = False
        promotion_frame_display()
    pawn.kill()
    chosen_piece(x, y, player)


while game_on:
    pygame.time.delay(int(1000/fps))
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            position = pygame.mouse.get_pos()
            coordinates = (position[0]//80 + 1, 8 - position[1]//80)
            selected_tile = board[coordinates]
            if selected_tile.piece is not None: #alternative to the following
                if selected_tile.piece.player == active_player:
                    select(selected_tile.piece)
            if selected_tile.is_available: #alternative guarded well, own piece tile is never available
                move(active_piece, selected_tile)
                promotion_check()
                player_switch()
                check_check()
                game_over_check()
                #pawn shade check
                for tile in pawn_shade_tiles:
                    if tile.pawn_shade.player == active_player or tile.pawn_shade.player is None:
                        tile.pawn_shade = None
                        pawn_shade_tiles.remove(tile) #removing from currently iterating list is not a problem, cuz up to 1 element to remove
        if event.type == pygame.QUIT:
            game_on = False
    if active_piece is not None:
        for target in active_piece.allowed_targets():
            target.is_available = True
    frame_display()


pygame.quit()

#do sprawdzenia: bicie w przelocie
#do ponownego przeanalizowania: bicie w przelocie
#do wyczyszczenia roszada i trochę promocja?