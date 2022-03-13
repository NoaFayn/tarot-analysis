# -*- coding: utf-8 -*-
import argparse
import json
import re

from rich.console import Console

from src.Logger import Logger

# ====================
# | GLOBAL VARIABLES |
# ====================

class Player:
    def __init__(self, name) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

class Card:
    def __init__(self, value, colour) -> None:
        self.value = value
        self.colour = colour

    def __str__(self) -> str:
        return '[{}:{}]'.format(self.value, self.colour)

    def __repr__(self) -> str:
        return str(self)

    def serialise(self):
        return '{} {}'.format(self.value, self.colour)

    def is_oudler(self):
        return self.colour == 'O'

    def is_fool(self):
        return self.value == '0'

    def get_score(self):
        if self.value == 'R':
            return 4.5
        if self.value == 'D':
            return 3.5
        if self.value == 'C':
            return 2.5
        if self.value == 'V':
            return 1.5
        return 0.5

def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        '--verbose',
        dest='verbosity',
        action='count',
        default=0,
        help='Verbosity level (-v for verbose, -vv for debug)',
    )
    parser.add_argument(
        '-q',
        '--quiet',
        dest='quiet',
        action='store_true',
        default=False,
        help='Show no information at all'
    )

    parser.add_argument(
        'game',
        help='Game associated with this round',
    )

    options = parser.parse_args()
    return options

def prompt_card():
    search = None
    while not search:
        card = input('CARD: ').upper()
        regex = r'^([0-9]{1,2}|[RDCV]) ?([SHDCO])$'
        search = re.search(regex, card)
        if search:
            return Card(search.group(1), search.group(2))
        else:
            logger.error('Please enter a correct card')

def prompt_player(players):
    while True:
        data = input('PLAYER: ')
        try:
            player_index = int(data)
            if player_index < 0 or player_index >= len(players):
                logger.error('Bad index {}, must be between 0 and {}'.format(player_index, len(players)-1))
            else:
                logger.info('Selected {}'.format(players[player_index]))
                return players[player_index]
        except:
            # Not an index, is a player name
            possible_players = [p for p in players if p.name.lower().startswith(data.lower())]
            if len(possible_players) == 0:
                logger.error('No player name starts with {}'.format(data))
            elif len(possible_players) > 1:
                logger.error('{} players name start with {}'.format(len(possible_players), data))
            else:
                logger.info('Selected {}'.format(possible_players[0]))
                return possible_players[0]

def find_taker(cards):
    """Finds the index of the card that takes the trick."""
    caller_index = 0
    taker_card = cards[0]
    # On regarde la couleur de la carte
    # Si meme couleur, on compare la valeur
    # Si couleur differente, on regarde si c'est de l'atout
    # Si atout, alors prend
    # Si pas atout, ne prend pas
    # Si excuse, ne prend pas
    # Si premiere carte est l'excuse, le suivant devient le preneur par defaut
    if taker_card.is_fool():
        caller_index = 1
        taker_card = cards[1]
        logger.debug('First card is fool, new taker is {}'.format(taker_card))

    taker_index = caller_index

    for offset,card in enumerate(cards[caller_index+1:]):
        logger.debug('Comparing {} and {}'.format(taker_card, card))
        if card.colour == taker_card.colour:
            logger.debug('Same colour')
            if card.value > taker_card.value:
                logger.debug('{} > {}, new taker is {}'.format(card.value, taker_card.value, card))
                taker_index = caller_index + 1 + offset
                taker_card = card
        else:
            logger.debug('Different colour')
            # excuse ne prend pas
            if card.is_oudler() and not card.is_fool():
                # si atout on prend
                logger.debug('{} is oudler, new taker is {}'.format(card, card))
                taker_index = caller_index + 1 + offset
                taker_card = card
    logger.debug('Taker is {}'.format(taker_card))
    return taker_index



def main(options, logger):
    logger.info('Hellow world!')

    logger.info('Loading game data...')
    with open(options.game, 'r') as fin:
        game_data = json.load(fin)

    round_data = {
        "meta": {},
        "dog": {},
        "dealing": [],
        "round": []
    }
    
    players = []
    for player_data in game_data['players']:
        players.append(Player(player_data['name']))
    if game_data['meta']['nb_players'] != len(players):
        logger.warning('Required {} players, found {}'.format(game_data['meta']['nb_players'], len(players)))
    logger.info('Loaded {} players'.format(len(players)))

    print('Enter metadata:')
    round_data['meta']['id'] = input('ID: ')
    round_data['meta']['name'] = input('NAME: ')
    round_data['meta']['game_id'] = game_data['meta']['id']

    print('Enter 3 dog cards:')
    dog = []
    while len(dog) != 3:
        dog.append(prompt_card())
    round_data['dog']['dealt'] = [c.serialise() for c in dog]
    
    print('Enter starting player:')
    start_player = prompt_player(players)
    start_player_index = players.index(start_player)

    print('Enter attacker player:')
    attacker_player = prompt_player(players)

    rounds = []
    NB_ROUNDS = int((78-3)/len(players))
    for counter in range(NB_ROUNDS):
        logger.info('Trick #{}/{}'.format(counter+1, NB_ROUNDS))
        trick_cards = []
        for turn in range(len(players)):
            current_player_index = (start_player_index + turn) % len(players)
            current_player = players[current_player_index]
            console.print(players)
            console.print('current_player=',current_player_index)
            logger.info('{} to play ({}/{})'.format(current_player.name, turn+1, len(players)))
            trick_cards.append(prompt_card())
        taker_index = find_taker(trick_cards)
        old_opener_index = start_player_index
        start_player_index = (players.index(start_player) + taker_index) % len(players)
        taker = players[start_player_index]
        logger.info('{} wins the trick'.format(taker.name))
        start_player = taker
        rounds.append({
            "opener": old_opener_index,
            "trick": [c.serialise() for c in trick_cards],
            "taker": start_player_index
        })

    round_data['round'] = rounds

    with open('round_{}.json'.format(round_data['meta']['id']), 'w') as fout:
        json.dump(round_data, fout)


if __name__ == "__main__":
    # Command line arguments
    options = get_options()

    logger = Logger(options.verbosity, options.quiet)

    console = Console()

    main(options, logger)
    
