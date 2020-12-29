""" Contains some unit templates.
"""
from unit_template import UnitTemplate, MeleeWeaponSet, RangedWeaponSet

_spearmen_spear_and_shield = MeleeWeaponSet('Spear and Shield', 4, 6, True, 3, 4, 3, 7,
                                       3)
spearmen = UnitTemplate('Spearmen', 120, 100, 5, 1, 8, 100,
                        [_spearmen_spear_and_shield])

_swordsmen_sword_and_shield = MeleeWeaponSet('Sword and Shield', 9, 5, True, 4, 5, 2,
                                        9, 3)
swordsmen = UnitTemplate('Swordsmen', 120, 100, 5, 3, 5, 100,
                         [_swordsmen_sword_and_shield])

_greatshieldmen_sword_and_greatshield = MeleeWeaponSet('Sword and Great-Shield', 6,
                                                  6, True, 3, 6, 6, 7, 3.5)
great_shield_men = UnitTemplate('Great-Shield Men', 120, 100, 4.5, 4, 12, 140,
                                [_greatshieldmen_sword_and_greatshield])

_scavn_swordsmen_sword_and_shield = MeleeWeaponSet('Sword and Shield', 11, 7, True, 3, 8, 2, 10, 3)
scavn_swordsmen = UnitTemplate('Scavn Swordsmen', 120, 100, 5, 4, 4, 80, [_scavn_swordsmen_sword_and_shield])

_rendmen_axe_and_shield = MeleeWeaponSet('Axe and Shield', 16, 6, True, 6, 12, 1, 14, 2)
rendmen = UnitTemplate('Rendmen', 120, 100, 6, 2, 2, 60, [_rendmen_axe_and_shield])

_freewood_archers_shortbow = RangedWeaponSet('Shortbow', 1, 2, False, 1, 2, 1, 3, 2, 6, 5, 10, 2, 9)
freewood_archers = UnitTemplate('Freeword Archers', 100, 100, 6, 2, 0, 60, [_freewood_archers_shortbow])
