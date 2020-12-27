""" Contains the Unit class.
"""
from direction import Direction, RelativeDirection


class Unit(object):
    """ A single unit of soldiers.
    """
    KILLING_POWER_RATIO = 0.10
    ARMOR_DESTRUCTION_RATIO = 0.25
    MAX_STAMINA_ATTACK_REDUCTION_RATIO = 0.50

    def __init__(self, template, pop=None, morale=None, stamina=None, rank=0, exp=0, cohesion=1):
        """ Initializes a new Unit.
        """
        self.template = template
        self._pop = template.max_pop if pop is None else pop
        self._morale = template.max_morale if morale is None else morale
        self._stamina = template.max_stamina if stamina is None else stamina
        self._armor = template.armor
        self._shield = template.shield
        self.rank = rank
        self.exp = exp
        self.cohesion = cohesion
        self.alive = True

    @property
    def pop(self):
        return self._pop

    @pop.setter
    def pop(self, val):
        if val > self.template.max_pop:
            self._pop = self.template.max_pop
        elif val < 0:
            self._pop = 0
        else:
            self._pop = val

    @property
    def morale(self):
        return self._morale

    @morale.setter
    def morale(self, val):
        if val > self.template.max_morale:
            self._morale = self.template.max_morale
        elif val < 0:
            self._morale = 0
        else:
            self._morale = val

    @property
    def stamina(self):
        return self._stamina

    @stamina.setter
    def stamina(self, val):
        if val > self.template.max_stamina:
            self._stamina = self.template.max_stamina
        elif val < 0:
            self._stamina = 0
        else:
            self._stamina = val

    @property
    def armor(self):
        return self._armor
    
    @armor.setter
    def armor(self, val):
        if val > self.template.armor:
            self._armor = self.template.armor
        elif val < 0:
            self._armor = 0
        else:
            self._armor = val
    
    @property
    def shield(self):
        return self._shield

    @shield.setter
    def shield(self, val):
        if val > self.template.shield:
            self._shield = self.template.shield
        elif val < 0:
            self._shield = 0
        else:
            self._shield = val

    def fight(self, enemy, attack_weapon_index=0, defend_weapon_index=0, direction=RelativeDirection.front, charging=False):
        """ Triggers a round of battle between this unit and an enemy unit.
            This unit is the attacker.

        Positional arguments:
        enemy -- the Unit to fight against
        direction -- the relative direction from this unit to the enemy.
                     Front by default
        charging -- True if this unit is charging the enemy unit
        """
        attacker_killing_power = Unit.killing_power(self, enemy, charging=charging, attack_weapon_index=attack_weapon_index, defend_weapon_index=defend_weapon_index)
        defender_killing_power = Unit.killing_power(enemy, self, charging=False)
        self.pop -= defender_killing_power
        enemy.pop -= attacker_killing_power
        self.stamina -= self.template.weapons[attack_weapon_index].fighting_stamina_usage
        enemy.stamina -= enemy.template.weapons[defend_weapon_index].fighting_stamina_usage
        self.stamina += self.template.stamina_regen
        enemy.stamina += enemy.template.stamina_regen
        attacker_armor_damage = self.template.weapons[attack_weapon_index].piercing * Unit.ARMOR_DESTRUCTION_RATIO * (1 - Unit.stamina_attack_reduction_ratio(self))
        defender_armor_damage = enemy.template.weapons[defend_weapon_index].piercing * Unit.ARMOR_DESTRUCTION_RATIO * (1 - Unit.stamina_attack_reduction_ratio(enemy))
        if direction is RelativeDirection.front and self.template.weapons[attack_weapon_index].has_shield:
            initial_shield = self.shield
            self.shield -= defender_armor_damage
            defender_armor_damage -= initial_shield
        if defender_armor_damage > 0:
            self.armor -= defender_armor_damage
        if direction is RelativeDirection.front and enemy.template.weapons[defend_weapon_index].has_shield:
            initial_shield = enemy.shield
            enemy.shield -= attacker_armor_damage
            attacker_armor_damage -= initial_shield 
        if attacker_armor_damage > 0:
            enemy.armor -= attacker_armor_damage
        if self.pop <= 0:
            self.die()
        if enemy.pop <= 0:
            enemy.die()

    def armor_defense(self, weapon_index=0, direction=RelativeDirection.front):
        """ Calculates the defense power of this unit from armor.

            Positional arguments:
            direction -- the direction this unit is being attacked from

            Return:
            The defense power this unit gains from its armor (and possibly
            shield).
        """
        armor_def = self.armor
        if direction is RelativeDirection.front and self.template.weapons[weapon_index].has_shield:
            armor_def += self.shield
        return armor_def

    def die(self):
        self.alive = False

    def print_status(self):
        s = "{0.template.name} Status:\n\tHealth = {0.pop}/{0.template.max_pop}"
        s += "\n\tMorale = {0.morale}/{0.template.max_morale}"
        s += "\n\tStamina = {0.stamina}/{0.template.max_stamina}"
        s += "\n\tArmor = {0.armor}/{0.template.armor}"
        s += "\n\tShield = {0.shield}/{0.template.shield}"
        print(s.format(self))

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
            * defender.template.max_pop * Unit.KILLING_POWER_RATIO

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
        atk_pow *= 1 - Unit.stamina_attack_reduction_ratio(attacker)
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
    
    @staticmethod
    def stamina_attack_reduction_ratio(attacker):
        return ((1 - (attacker.stamina / attacker.template.max_stamina)) * Unit.MAX_STAMINA_ATTACK_REDUCTION_RATIO)


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
        self.active = True
        self.winner = None
        self.loser = None

    def battle(self):
        """ Triggers a round of battle between the attacker and defender.
        """
        self.attacker.fight(self.defender, direction=self.direction,
                            charging=self.charging)
        self.round += 1
        self.charging = False
        if not self.attacker.alive:
            self.active = False
            if self.defender.alive:
                self.winner = self.defender
                self.loser = self.attacker
        if not self.defender.alive:
            self.active = False
            if self.attacker.alive:
                self.winner = self.attacker
                self.loser = self.defender
