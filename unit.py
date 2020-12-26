""" Contains the Unit class.
"""
from direction import Direction, RelativeDirection


class Unit(object):
    """ A single unit of soldiers.
    """
    def __init__(self, template, pop=None, rank=0, exp=0, cohesion=1):
        """ Initializes a new Unit.
        """
        self.template = template
        self.pop = template.max_pop if pop is None else pop
        self.rank = rank
        self.exp = exp
        self.cohesion = cohesion

    def fight(self, enemy, direction=RelativeDirection.front, charging=False):
        """ Triggers a round of battle between this unit and an enemy unit.
            This unit is the attacker.

        Positional arguments:
        enemy -- the Unit to fight against
        direction -- the relative direction from this unit to the enemy.
                     Front by default
        charging -- True if this unit is charging the enemy unit
        """

    def armor_defense(self, direction=RelativeDirection.front):
        """ Calculates the defense power of this unit from armor.

            Positional arguments:
            direction -- the direction this unit is being attacked from

            Return:
            The defense power this unit gains from its armor (and possibly
            shield).
        """
        armor_def = self.template.armor
        if direction is Direction.front:
            armor_def += self.template.shield
        return armor_def

    @staticmethod
    def killing_power(attacker, defender, charging=False):
        """ Calculates the average killing power of the attacker unit against the
            defender unit.

            Positional arguments:
            attacker -- the 'attacking' unit whose killing power will be found
            defender -- the 'defending' unit

            Keyword arguments:
            charging -- True if the attacker is charging the defender.
                        False by default.

            Return:
            The average number of pops in the defender unit that will be killed
            per fronted pop in the attacker unit.
        """
        return Unit.attack_power(attacker, defender, charging=charging)\
            / Unit.defense_power(defender, attacker)

    @staticmethod
    def attack_power(attacker, defender, charging=False):
        """ Calculates the attack power of the attacker unit against the
            defender unit.

            Positional arguments:
            attacker -- the 'attacking' unit whose attack power will be found
            defender -- the 'defending' unit


            Return:
            The attack power of the attacker versus the defender.
        """
        atk_pow = attacker.template.attack
        if charging:
            atk_pow += attacker.template.charge
        return atk_pow

    @staticmethod
    def defense_power(defender, attacker, direction=RelativeDirection.front):
        """ Calculates the defense power of the defender unit against the
            attacker unit.

            Positional arguments:
            defender -- the 'defending' unit whose defense power will be found
            attacker -- the 'attacking' unit

            Return:
            The defense power of the defender versus the attacker.
        """
        def_pow = defender.template.defense
        armor_val = defender.template.armor
        if direction is Direction.front:
            armor_val += defender.template.shield
        armor_val -= attacker.template.piercing
        armor_val = 0 if armor_val < 0 else armor_val
        def_pow += armor_val
        def_pow += defender.template.discipline * defender.cohesion
        return def_pow


class BattleLink(object):
    """ A link between two units that are locked in battle with each other.
    """
    def __init__(self, attacker, defender, direction=RelativeDirection.front,
                 charging=False):
        """ Initializes a new BattleLink.

        Positional arguments:
        attacker -- the attacking Unit
        defender -- the defending Unit
        direction -- the RelativeDirection that the attacker is hitting the
                     defender from
        charging -- True if the attacker is charging the defender
        """
        self.attacker = attacker
        self.defender = defender
        self.direction = direction
        self.charging = charging

    def battle(self):
        """ Triggers a round of battle between the attacker and defender.
        """
        self.attacker.fight(self.defender, direction=self.direction,
                            charging=self.charging)
