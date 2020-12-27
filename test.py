from unit import Unit, BattleLink
from templates import *


def simple_unit_fight_test(attacker_template, defender_template):
    attacker = Unit(attacker_template)
    defender = Unit(defender_template)
    link = BattleLink(attacker, defender)
    while link.active:
        print("\nRound {}".format(link.round))
        attacker.print_status()
        defender.print_status()
        link.battle()
    if link.winner and link.loser:
        print("\nWinner: {0.template.name}\tLoser ({3}): {1.template.name}\tNum Rounds: {2}\n".format(link.winner, link.loser, link.round, "Dead" if not link.loser.alive else "Fleeing" if link.loser.fleeing else ""))
    else:
        print("\nRESULT WAS A TIE\n")
    attacker.print_status()
    defender.print_status()


if __name__ == "__main__":
    simple_unit_fight_test(rendmen, scavn_swordsmen)
    