from flask import Flask, Response
from flask_cors import CORS
import random
import uuid
import json
import flask_json
from flask_socketio import SocketIO

from flask_socketio import send, emit


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
flask_json.FlaskJSON(app)
from flask import request
from flask_socketio import join_room, leave_room

from flask import send_from_directory

#@app.after_request
def do_something_whenever_a_request_has_been_handled( msg="", response=None):
    # we have a response to manipulate, always return one
    #if("ignore" not in  response.__dict__) :
        socketio.emit("update","")
        socketio.emit("notif",msg)
    #return response

@socketio.on('join')
def handle_message(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', to=room)


@app.route("/game/init")
def initGame():
    np = int(request.args.get('np', default="4"))
    game = Game()
    game.initPlay(np)
    res = json.dumps(game.tojson(None), default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    socketio.emit("init", game.uid)
    result = Response(res, mimetype='application/json')
    result.ignore = True
    do_something_whenever_a_request_has_been_handled("new game initiated <a href=\"origin/?game_id="+game.uid+"\">join</a>")
    return result


@app.route("/game/init/<ip>")
def initGame2(ip):
    return initGame()



@app.route("/game/<uid>/<ip>")
def getGame(uid,ip):

    game = {}
    if(uid in games):
        game = games[uid]
        p = game.registerOrGetPlayer(ip)
        if(p == None):
            p = game.registerOrGetPlayer(ip, True)
            if(p!=None):
                do_something_whenever_a_request_has_been_handled(str(p.order) + " "+p.name+" joined game")
        if(p != None):
            game = game.tojson(p.uid)
        else:
             game = game.tojson(None)
        

    res = json.dumps(game, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    result = Response(res, mimetype='application/json')
    result.ignore = True
    return result

@app.route("/game/<uid>/<ip>/get")
def getCard(uid,ip):

    
    if(uid in games):
        game = games[uid]
        p = game.registerOrGetPlayer(ip, False)
        game.giveToPlayer(p.order)
    
    #res = json.dumps(game, default=lambda o: o.__dict__, 
    #        sort_keys=True, indent=4)
    do_something_whenever_a_request_has_been_handled(str(p.order) + " "+p.name+" get card")
    return Response({"ok":True}, mimetype='application/json')

@app.route("/game/<uid>/<ip>/name")
def changeName(uid,ip):
    name = request.args.get('name')
    
    if(uid in games):
        game = games[uid]
        p = game.registerOrGetPlayer(ip, False)
        p.name = name
    
        #res = json.dumps(game, default=lambda o: o.__dict__, 
        #        sort_keys=True, indent=4)
        do_something_whenever_a_request_has_been_handled(str(p.order) + " changed name to "+p.name )
    return Response({"ok":True}, mimetype='application/json')

@app.route("/game/<uid>/<ip>/getthrown")
def gethrown(uid,ip):

    
    if(uid in games):
        game = games[uid]
        p = game.registerOrGetPlayer(ip, False)
        card = game.giveToPlayerFromThrown(p.order)
    
        #res = json.dumps(game, default=lambda o: o.__dict__, 
        #        sort_keys=True, indent=4)
        do_something_whenever_a_request_has_been_handled(str(p.order) +" "+p.name+" get from thrown " + str(card.number)+" "+card.color )
    return Response({"ok":True}, mimetype='application/json')

@app.route("/game/<uid>/<ip>/revert")
def revert(uid,ip):
    game = games[uid]
    game.revert()
    p = game.registerOrGetPlayer(ip)
    socketio.emit("revert", p.order)
    
    #res = json.dumps(game, default=lambda o: o.__dict__, 
    #        sort_keys=True, indent=4)
    do_something_whenever_a_request_has_been_handled(str(p.order) +" "+p.name+" reverted")
    return Response({"ok":True}, mimetype='application/json')

@app.route("/game/<uid>/<ip>/sort/<tp>")
def sortCards(uid,ip, tp):
    cards = request.args.get('cards')
    game = games[uid]

    p = game.registerOrGetPlayer(ip)
    game.sort(p.order, [int(ic) for ic in cards.split(',')], int(tp))

    return Response({"ok":True}, mimetype='application/json')

@app.route("/game/<uid>/<ip>/down")
def getDownCards(uid,ip):
    cards = request.args.get('cards')
    game = games[uid]

    p = game.registerOrGetPlayer(ip)
    game.getDown(p.order, [int(ic) for ic in cards.split(',')])

    do_something_whenever_a_request_has_been_handled(str(p.order) +" "+p.name+ " get down")
    return Response({"ok":True}, mimetype='application/json')

@app.route("/game/<uid>/<ip>/downcard")
def getDownCards2(uid,ip):
    ps = [x.split(",") for x in request.args.get('possible').split(";")]
    game = games[uid]

    p = game.registerOrGetPlayer(ip)
    if(len(ps)>0):
        pr = ps[0]
        game.getDownCard(p.order, int(pr[0]), int(pr[1]), int(pr[2]),int(pr[3]) )

    do_something_whenever_a_request_has_been_handled(str(p.order) +" "+p.name+ " get down card ")
    return Response({"ok":True}, mimetype='application/json')


@app.route("/game/<uid>/<ip>/<ic>")
def throwCard(uid,ip, ic):
    game = games[uid]
    

    p = game.registerOrGetPlayer(ip)
    card = game.throwCard(p.order, int(ic))
    if(card != None):
        do_something_whenever_a_request_has_been_handled(str(p.order) +" "+ p.name +" throw card " + str(card.number)+ " " +card.color)
    return Response({"ok":True}, mimetype='application/json')


import os
@app.route('/<path:path>')
def send_report(path):
    if(os.path.exists("dist/"+path)):
        return send_from_directory('dist', path)
    else:
        return defau()

@app.route('/')
def defau():
    path ="index.html"

    resp =  send_from_directory('dist', path)
    return resp

colors = ['hearts', 'diamonds', 'clubs', 'spades']

class Card:
    def __init__(self, number, color, id) -> None:
        self.number = number
        self.color = color
        self.id = id

class Player:
    cards : list[Card] = []
    cardsDown :list[Card] = []
    order:int = -1
    uid:str
    def __init__(self, order:int) -> None:
        self.order = order
        self.cards = []
        self.cardsDown = []
        self.uid = ""
        self.name = ""

    def tojson(self, verbose:bool) -> dict:
        dic = {"cardsDown":self.cardsDown, "order":self.order, "name":self.name}
        if(verbose):
            dic["cards"] =self.cards
            dic["uid"] = self.uid
        else:
            dic["cards"] = [[] for i in self.cards]
        return dic
    


class Game:
    players : list[Player]
    cards : list[Card] 
    thrownCards : list[Card]

    def getDownCard(self, ip, ic, ip2, id2, ic2):
        p1 = self.players[ip]

        p2 = self.players[ip2]
        card = [c for c in p1.cards if c.id == ic][0]
        down2 = p2.cardsDown[id2]
        self.players[ip].cards.remove(card)
        down2.append(card)
        self.actions.append(["downcard", ip, ic, ip2, id2])

    def revertDownCard(self, ip, ic, ip2, id2):
        p2 = self.players[ip2]
        card = [c for c in p2.cardsDown[id2] if c.id == ic][0]
        p2.cardsDown[id2].remove(card)
        self.players[ip].cards.append(card)

    def registerOrGetPlayer(self, ip:str, register=False) -> Player:
        for p in self.players:
            if(p.uid != "" and p.uid == ip):
                return p
        if(register):
            for p in self.players:
                if(p.uid =="" and ip.isdecimal() and  p.order == int(ip)):
                    puid = str(uuid.uuid4())
                    p.uid = puid
                    return p


    def tojson(self, ip):
        result = { "uid":self.uid, "cards":len(self.cards), "thrownCards":self.thrownCards[max(len(self.thrownCards) - 4, 0):], 
                  "players":[ p.tojson(p.uid == ip and p.uid != "") for p in self.players]}
        return result
    

    def __init__(self) -> str:
        initialCards = [[i%13, colors[int(i/26)], i] for i in range(104)] + [[0, '', 104], [0, '', 105],[0, '', 106],[0, '', 107]]
        #random.seed()
        initialCards = sorted(initialCards, key=lambda c : random.random())
        #random.shuffle(initialCards)
        self.cards = [Card(c[0], c[1], c[2]) for c in initialCards]
        self.players = []
        self.thrownCards = []
        self.uid = str(uuid.uuid4())
        games[self.uid] = self
        self.actions = []

    def revert(self):
        if(len(self.actions) == 0):
            return 
        else:
            action = self.actions[len(self.actions)-1]
            match action[0]:
                case "give" : self.returnCard(action[1], action[2])
                case "givethrown" :  self.throwCard(action[1], action[2], False)
                case "throw": self.giveToPlayerFromThrown(action[1], False)
                case "down": self.revertDown(action[1])
                case "downcard": self.revertDownCard(action[1], action[2], action[3], action[4])
            self.actions.pop()
            
    def revertDown(self, ip:int):
        cards = self.players[ip].cardsDown.pop()
        for c in cards:
            self.players[ip].cards.append(c)

    def initPalayer(self) -> Player:
        p = Player(len(self.players))
        self.players.append(p)
        return p
    
    def giveToPlayer(self, ip:int, c:int = 1, history = True):
        for j in range(c):
            card = self.cards.pop()
            self.players[ip].cards.append(card)
            if(history):
                self.actions.append(["give", ip, card.id])
    
    def returnCard(self, ip:int, ic:int):
        cards = self.players[ip].cards
        for card in  cards:
            if(card.id == ic):
                self.cards.append(card)
                self.players[ip].cards.remove(card)
                #self.actions.append[["throw", ip, card.id]]
                return card
    
    def giveToPlayerFromThrown(self, ip:int, history=True):

            card = self.thrownCards.pop()
            self.players[ip].cards.append(card)
            if(history):
                self.actions.append(["givethrown", ip, card.id])
            return card
    
    def throwCard(self, ip:int, ic:int, history=True) -> Card:
        cards = self.players[ip].cards
        for card in  cards:
            if(card.id == ic):
                self.thrownCards.append(card)
                self.players[ip].cards.remove(card)
                if(history):
                    self.actions.append(["throw", ip, card.id])
                return card

    def getDown(self, ip:int, ics:list[int]):
        nd = []
        self.players[ip].cardsDown.append(nd)
        self.actions.append(["down", ip])
        cards = self.players[ip].cards
        for ic in ics:
            for card in  cards:
                if(card.id == ic):
                    nd.append(card)
                    self.players[ip].cards.remove(card)
        
    def sort(self, ip:int, ics:list[int], tp):

        nd = []
        if(tp == 100):
            cards = self.players[ip].cards
        else:
            cards = self.players[ip].cardsDown[tp]
        for ic in ics:
            for card in  cards:
                if(card.id == ic):
                    nd.append(card)
        if(tp == 100):
            self.players[ip].cards = nd
        else:
            self.players[ip].cardsDown[tp] = nd
      
    
    def initPlay(self, np:int):
        game = self
        for i in range(np):
            p = game.initPalayer()
        
        for i in range(7):
            if( i == 0):
                game.giveToPlayer(game.players[0].order, history=False)
            for p in game.players:
                game.giveToPlayer(p.order, 2, history=False)

    def end(self):
        pass

games : dict[str, Game] = {}


if(__name__ == "__main__"):
    context = ('certs/host.cert', 'certs/host.key')
    socketio.run(app,host="0.0.0.0", ssl_context=context, port=8086)
    #socketio.run(app,host="0.0.0.0", port=8086)

    game = Game()
    p1 = game.initPalayer()
    p2 = game.initPalayer()
    p3 = game.initPalayer()
    p4 = game.initPalayer()

    assert len(p1.cards) == 0, "player cards should be 0 at first"
    assert len(game.cards) == 108, "game cards should be 108 at first"
    assert len(game.players) == 4, "game players should be 4 at first"

    for i in range(7):
        if( i == 0):
            game.giveToPlayer(game.players[0].order)
        for p in game.players:
            game.giveToPlayer(p.order, 2)
        
    
    for p in game.players:
        if(p.order == 0):
            assert len(p.cards) == 15, f"player {p.order} cards should be 14 after init"
        else:
            len(p.cards) == 14, f"player {p.order} cards should be 14 after init"

    assert len(game.cards) == 51, "game cards should be 51 at first"

    c5 = p1.cards[5]
    game.throwCard(0, 5)
    assert len(p.cards) == 14, f"player {p.order} cards should be 14 after first throw"
    assert c5.number == game.thrownCards[0].number, "error throwing"
