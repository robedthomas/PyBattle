""" Contains the UnitTemplate class.
"""


class UnitTemplate(object):
    """ A template of a single type of unit.
    """
    def __init__(self, name, max_pop, max_stamina, stamina_regen, armor, shield, max_morale, weapons):
        """ Initializes a new UnitTemplate.
        """
        self.name = name
        self.max_pop = max_pop
        self.max_stamina = max_stamina
        self.stamina_regen = stamina_regen
        self.armor = armor
        self.shield = shield
        self.max_morale = max_morale
        self.weapons = weapons
        if not isinstance(self.weapons, list):
            self.weapons = [self.weapons]


class WeaponSet(object):
    """ A single weapon that a unit can use.
    """
    def __init__(self, name, attack, defense, has_shield, piercing, charge,
                 discipline, fighting_stamina_usage, moving_stamina_usage,
                 display_name=None):
        """ Initializes a new WeaponSet.
        """
        self.name = name
        self.display_name = display_name if display_name else self.name
        self.attack = attack
        self.defense = defense
        self.has_shield = has_shield
        self.piercing = piercing
        self.charge = charge
        self.discipline = discipline
        self.fighting_stamina_usage = fighting_stamina_usage
        self.moving_stamina_usage = moving_stamina_usage


class MeleeWeaponSet(WeaponSet):
    """ A melee WeaponSet.
    """
    pass


class RangedWeaponSet(WeaponSet):
    """ A ranged WeaponSet.
    """
    def __init__(self, name, attack, defense, has_shield, piercing, charge,
                 discipline, fighting_stamina_usage, moving_stamina_usage,
                 ranged_attack, range, ammunition, ranged_piercing, ranged_fighting_stamina_usage,
                 display_name=None):
        super().__init__(name, attack, defense, has_shield, piercing, charge,
                         discipline, fighting_stamina_usage, moving_stamina_usage, display_name=display_name)
        self.ranged_attack = ranged_attack
        self.range = range
        self.ammunition = ammunition
        self.ranged_piercing = ranged_piercing
        self.ranged_fighting_stamina_usage = ranged_fighting_stamina_usage
