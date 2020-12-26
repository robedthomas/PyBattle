""" Contains some unit templates.
"""
from unit_template import UnitTemplate, WeaponSet

_spearmen_spear_and_shield = WeaponSet('Spear and Shield', 4, 6, 3, 3, 4, 3, 7,
                                       3)
spearmen = UnitTemplate('Spearmen', 120, 100, 5, 1, 4,
                        [_spearmen_spear_and_shield])

_swordsmen_sword_and_shield = WeaponSet('Sword and Shield', 9, 5, 4, 5, 5, 2,
                                        9, 3)
swordsmen = UnitTemplate('Swordsmen', 120, 100, 5, 1, 5,
                         [_swordsmen_sword_and_shield])

_greatshieldmen_sword_and_greatshield = WeaponSet('Sword and Great-Shield', 6,
                                                  6, 16, 3, 6, 6, 7, 3.5)
great_shield_men = UnitTemplate('Great-Shield Men', 120, 100, 4.5, 1, 7,
                                [_greatshieldmen_sword_and_greatshield])
