#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import system

class Chat(object):

    JOUEURS_NAMES = ['Franklin', 'Martin', 'Arnaud', 'Odile', 'Raffin']
    FACES_DE = [
        (u'Piocher', 'pickCard'),
        (u'Jouer une carte', 'playCard'),
        (u'Echanger un objet', 'exchangeObject'),
        (u'Echanger une carte', 'exchangeCard'),
        (u'Piocher', 'pickCard'),
        (u'Avancer le temps', 'forwardTime'),
        ]
    COULEURS = ['Vert', 'Marron', 'Gris', 'Noir', 'Orange']
    OBJETS = ['Lettre', 'Chiffre', 'Ecrou', 'Rondelle', 'Vis']
    CARTES = [
        (u'Relancer le dé', 'rerollDice'),
        (u'Reculer le temps', 'backInTime'),
        (u'Echanger un objet', 'exchangeObject'),
        (u'Prendre un objet', 'pickObject'),
        ]
    DEFAULT_DECK_SIZE = 30

    TEMPS_MAX = 2

    def __init__(self, nb_joueurs):
        self.gameLog = []
        self.time = 0
        self.gameTurn = 0
        self.joueurs = [self.JOUEURS_NAMES[i] for i in range(nb_joueurs)]
        self.hands = [[] for i in range(nb_joueurs)]
        self.coffres = [[] for i in range(nb_joueurs)]
        self.addLog(u"Démarrage d'une partie avec les joueurs %s" % (self.joueurs,))
        self.cartes = self.newDeck(self.DEFAULT_DECK_SIZE)
        self.addLog(u"Utilisation du paquet %s" % (self.cartes,))
        self.cartes = self.shuffleDeck(self.cartes)
        self.addLog(u"Paquet mélangé : %s" % (self.cartes,))
        self.objets = []
        for i in range(nb_joueurs):
            self.objets.extend(["%s %s" % (obj_name, self.COULEURS[i]) for obj_name in self.OBJETS])
        self.objets = self.shuffleDeck(self.objets)
        self.addLog(u"Objets préparés : %s" % (self.objets,))
        self.joueur_courant = random.randrange(len(self.joueurs))
        self.run()

    def run(self, printLog=True):
        while not self.gameEnds():
            self.addLog(u"Tour du joueur %s (%s)" % (self.joueur_courant, self.joueurs[self.joueur_courant]))
            dice_result, function = self.rollDice()
            self.addLog(u"Lancement du dé : %s" % (dice_result,))
            getattr(self, function)()

            self.joueur_courant += 1
            if self.joueur_courant == len(self.joueurs):
                self.joueur_courant = 0
                self.gameTurn += 1
        self.addLog(u"Fin du jeu")

    def gameEnds(self):
        return self.time >= self.TEMPS_MAX

    def pickCard(self):
        card = self.pickUpcard()
        if card is None:
            self.addLog(u"Plus de cartes")
            return
        self.addLog(u"Pioche la carte %s" % (card,))
        self.hands[self.joueur_courant].append(card)

    def playCard(self):
        return

    def exchangeObject(self):
        if len(self.coffres[self.joueur_courant]) == 0:
            self.addLog(u"Impossible d'échanger un objet quand on n'en a pas")
            return
        others_objects = []
        for i, coffre in enumerate(self.coffres):
            if i != self.joueur_courant and len(coffre) > 0:
                others_objects.extend([(i, o) for o in coffre])
        self.addLog("Vous pouvez échanger un de vos objets contre l'un de ceux-ci : %s" % (others_objects,))

    def exchangeCard(self):
        if len(self.hands[self.joueur_courant]) == 0:
            self.addLog(u"Impossible d'échanger une carte quand on n'en a pas")
            return
        others_cards = []
        for i, hand in enumerate(self.hands):
            if i != self.joueur_courant and len(hand) > 0:
                others_cards.extend([(i, o) for o in hand])
        self.addLog("Vous pouvez échanger une de vos cartes contre l'une de celles-ci : %s" % (others_cards,))

    def forwardTime(self):
        self.time += 1

    def rollDice(self):
        return random.choice(self.FACES_DE)

    def addLog(self, msg, printLog=True):
        msg = "%s (%s) : %s" % (self.gameTurn, self.time, msg)
        self.gameLog.append(msg)
        print msg

    def pickUpcard(self):
        if len(self.cartes) == 0:
            return None
        return self.cartes.pop(random.randrange(len(self.cartes)))

    def newDeck(self, deck_size):
        deck = []
        current_subdeck = self.CARTES[:]
        while len(deck) < deck_size:
            deck.append(current_subdeck.pop(random.randrange(len(current_subdeck))))
            if len(current_subdeck) == 0:
                current_subdeck = self.CARTES[:]
        return deck

    def shuffleDeck(self, deck):
        new_deck = []
        deck_copy = deck[:]
        while len(deck_copy) > 0:
            new_deck.append(deck_copy.pop(random.randrange(len(deck_copy))))
        return new_deck

def main():
    partie = Chat(3)

if __name__ == "__main__":
    main()
