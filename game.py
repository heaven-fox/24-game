# coding: utf8

import random

from twisted.internet import (
    protocol, reactor, endpoints
)

CARDS = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10,
         10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13]

CONNECTIONS = []
CARD_RECORD = {}
SCORE_RECORD = {}
COMMANDS = ('start', 'commit', 'quit')


class GameProtocol(protocol.Protocol):

    def transform_unique_key(self):
        peer = self.transport.getPeer()
        return '{host}:{port}'.format(host=peer.host, port=peer.port)

    def connectionMade(self):
        uk = self.transform_unique_key()
        if uk not in SCORE_RECORD:
            SCORE_RECORD[uk] = 0
        if uk not in CONNECTIONS:
            CONNECTIONS.append(uk)

    def dataReceived(self, data):
        sp = data.strip().split(' ')
        command = sp[0]
        if command == 'start':
            uk = self.transform_unique_key()
            if uk not in CARD_RECORD:
                cards = random.sample(CARDS, 4)
                for i, c in enumerate(cards):
                    cards[i] = str(c)
                CARD_RECORD[uk] = cards
            response = '{0}\n'.format(' '.join(CARD_RECORD[uk]))
        elif command == 'quit':
            response = 'Go to quit game.\n'
        elif command == 'commit':
            solution = sp[1]
            response = 'Your solution {0} is wrong.\n'.format(solution)
        else:
            response = 'Unknown command {0}.\n'.format(sp[0])
        self.transport.write(response)
        if command == 'quit':
            self.transport.loseConnection()

    def connectionLost(self, reason=protocol.connectionDone):
        uk = self.transform_unique_key()
        if uk in CONNECTIONS:
            CONNECTIONS.remove(uk)
        if uk in CARD_RECORD:
            CARD_RECORD.pop(uk)
            if SCORE_RECORD[uk] > 0:
                SCORE_RECORD[uk] -= 1


class GameFactory(protocol.Factory):

    def buildProtocol(self, addr):
        return GameProtocol()


endpoints.serverFromString(reactor, 'tcp:1234').listen(GameFactory())
reactor.run()