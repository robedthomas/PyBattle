""" Contains the Unit class.
"""
from direction import Direction, RelativeDirection


class Unit(object):
    """ A single unit of soldiers.
    """
    KILLING_POWER_RATIO = 0.10

    def __init__(self, template, pop=None, morale=None, stamina=None, rank=0, exp=0, cohesion=1):
        """ Initializes a new Unit.
        """
        self.template = template
        self.pop = template.max_pop if pop is None else pop
        self.morale = template.max_morale if morale is None else morale
        self.stamina = template.max_stamina if stamina is None else stamina
        self.rank = rank
        self.exp = exp
        self.cohesion = cohesion

    def fight(self, enemy, attack_weapon_index=0, defend_weapon_index=0, direction=RelativeDirection.front, charging=False):
        """ Triggers a round of battle between this unit and an enemy unit.
            This unit is the attacker.

        Positional arguments:
        enemy -- the Unit to fight against
        direction -- the relative direction from this unit to the enemy.
                     Front by default
        charging -- True if this unit is charging the enemy unit
        """
        attacker_killing_power = killing_power(self, enemy, charging=charging, attack_weapon_index=attack_weapon_index, defend_weapon_index=defend_weapon_index)
        defender_killing_power = killing_power(enemy, self, charging=False)
        self.pop -= defender_killing_power
        enemy.pop -= attacker_killing_power
        self.stamina -= self.template.weapons[attack_weapon_index].fighting_stamina_usage
        enemy.stamina -= enemy.template.weapons[defend_weapon_index].fighting_stamina_usage

    def armor_defense(self, weapon_index=0, direction=RelativeDirection.front):
        """ Calculates the defense power of this unit from armor.

            Positional arguments:
            direction -- the direction this unit is being attacked from

            Return:
            The defense power this unit gains from its armor (and possibly
            shield).
        """
        armor_def = self.template.armor
        if direction is Direction.front:
            armor_def += self.template.weapons[weapon_index].shield
        return armor_def

    @staticmethod
    def killing_power(attacker, defender, attack_weapon_index=0, defend_weapon_index=0, charging=False):
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
        return Unit.attack_power(attacker, defender, attack_weapon_index=0, defend_weapon_index=0, charging=charging)\
            / Unit.defense_power(defender, attacker, attack_weapon_index=0, defend_weapon_index=0)\
            * defender.template.max_pop * KILLING_POWER_RATIO

    @staticmethod
    def attack_power(attacker, defender, attack_weapon_index=0, defend_weapon_index=0, charging=False):
        """ Calculates the attack power of the attacker unit against the
            defender unit.

            Positional arguments:
            attacker -- the 'attacking' unit whose attack power will be found
            defender -- the 'defending' unit


            Return:
            The attack power of the attacker versus the defender.
        """
        atk_pow = attacker.template.weapons[attack_weapon_index].attack
        if charging:
            atk_pow += attacker.template.weapons[attack_weapon_index].charge
        return atk_pow

    @staticmethod
    def defense_power(defender, attacker, attack_weapon_index=0, defend_weapon_index=0, direction=RelativeDirection.front):
        """ Calculates the defense power of the defender unit against the
            attacker unit.

            Positional arguments:
            defender -- the 'defending' unit whose defense power will be found
            attacker -- the 'attacking' unit

            Return:
            The defense power of the defender versus the attacker.
        """
        def_pow = defender.template.weapons[defend_weapon_index].defense
        armor_val = defender.armor_defense()
        armor_val -= attacker.template.weapons[attack_weapon_index].piercing
        armor_val = 0 if armor_val < 0 else armor_val
        def_pow += armor_val
        def_pow += defender.template.weapons[defend_weapon_index].discipline * defender.cohesion
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
        self.round = 0

    def battle(self):
        """ Triggers a round of battle between the attacker and defender.
        """
        self.attacker.fight(self.defender, direction=self.direction,
                            charging=self.charging)
        self.round += 1
        self.charging = False
