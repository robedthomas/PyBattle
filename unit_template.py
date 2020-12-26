""" Contains the UnitTemplate class.
"""


class UnitTemplate(object):
    """ A template of a single type of unit.
    """
    def __init__(self, name, max_pop, max_stamina, stamina_regen, armor,
                 weapons):
        """ Initializes a new UnitTemplate.
        """
        self.name = name
        self.max_pop = max_pop
        self.armor = armor
        self.weapons = weapons
        if not isinstance(self.weapons, list):
            self.weapons = [self.weapons]


class WeaponSet(object):
    """ A single weapon that a unit can use.
    """
    def __init__(self, name, attack, defense, shield, piercing, charge,
                 discipline, fighting_stamina_usage, moving_stamina_usage,
                 display_name=None):
        """ Initializes a new WeaponSet.
        """
        self.name = name
        self.display_name = display_name if display_name else self.name
        self.attack = attack
        self.defense = defense
        self.shield = shield
        self.piercing = piercing
        self.charge = charge
        self.discipline = discipline
        self.fighting_stamina_usage = fighting_stamina_usage
        self.moving_stamina_usage = moving_stamina_usage
