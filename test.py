from unit import Unit, BattleLink, RangedBattleLink
from templates import *


def simple_unit_fight_test(attacker_template, defender_template):
    attacker = Unit(attacker_template)
    defender = Unit(defender_template)
    link = BattleLink(attacker, defender)
    while link.active:
        link.battle()
    print(link)


def simple_unit_ranged_fight_test(attacker_template, defender_template):
    attacker = Unit(attacker_template)
    defender = Unit(defender_template)
    link = RangedBattleLink(attacker, defender)
    while link.active:
        link.battle()
    print(link)


if __name__ == "__main__":
    simple_unit_ranged_fight_test(freewood_archers, scavn_swordsmen)
    