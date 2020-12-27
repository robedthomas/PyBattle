from unit import Unit, BattleLink
from templates import *


def simple_unit_fight_test(attacker_template, defender_template):
    attacker = Unit(attacker_template)
    defender = Unit(defender_template)
    link = BattleLink(attacker, defender)
    while link.active:
        attacker.print_status()
        defender.print_status()
        link.battle()
    if link.winner:
        print("Winner: {0.template.name}\tLoser: {1.template.name}\tNum Rounds: {2}".format(link.winner, link.loser, link.round))


if __name__ == "__main__":
    simple_unit_fight_test(spearmen, swordsmen)
    