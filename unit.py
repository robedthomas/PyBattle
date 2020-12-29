""" Contains the Unit class.
"""
import math
from direction import Direction, RelativeDirection


class Unit(object):
    """ A single unit of soldiers.
    """
    KILLING_POWER_RATIO = 8
    ARMOR_DESTRUCTION_RATIO = 0.25
    MAX_STAMINA_ATTACK_REDUCTION_RATIO = 0.50
    MAX_MORALE_ATTACK_REDUCTION_RATIO = 0.40
    MORALE_LOSS_FROM_COMBAT_FACTOR = 5
    MORALE_LOSS_FROM_RANGED_COMBAT_FACTOR = 50
    MORALE_LOSS_FROM_STAMINA_FACTOR = 5

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
        self.fleeing = False

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
            self._pop = int(val)

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

    @staticmethod
    def fight(attacker, defender, attack_weapon_index=0, defend_weapon_index=0, direction=RelativeDirection.front, charging=False):
        """ Triggers a round of battle between two units.

        Positional arguments:
        attacker -- the attacking Unit
        defender -- the defending Unit
        direction -- the relative direction from the attacker to the defender.
                     Front by default
        charging -- True if the attacker is charging the defender
        """
        # Calculate killing power
        attacker_killing_power = Unit.killing_power(attacker, defender, charging=charging, attack_weapon_index=attack_weapon_index, defend_weapon_index=defend_weapon_index)
        defender_killing_power = Unit.killing_power(defender, attacker, charging=False, attack_weapon_index=attack_weapon_index, defend_weapon_index=defend_weapon_index)
        # Deal health damage
        attacker.pop -= defender_killing_power
        defender.pop -= attacker_killing_power
        # Deal armor damage
        attacker_armor_damage = attacker.template.weapons[attack_weapon_index].piercing * Unit.ARMOR_DESTRUCTION_RATIO * (1 - Unit.stamina_attack_reduction_ratio(attacker))
        defender_armor_damage = defender.template.weapons[defend_weapon_index].piercing * Unit.ARMOR_DESTRUCTION_RATIO * (1 - Unit.stamina_attack_reduction_ratio(defender))
        attacker_shield_damage = 0
        defender_shield_damage = 0
        if direction is RelativeDirection.front and attacker.template.weapons[attack_weapon_index].has_shield:
            defender_shield_damage = attacker.shield if attacker.shield < defender_armor_damage else defender_armor_damage
            attacker.shield -= defender_shield_damage
            defender_armor_damage -= defender_shield_damage
        if defender_armor_damage > 0:
            attacker.armor -= defender_armor_damage
        if direction is RelativeDirection.front and defender.template.weapons[defend_weapon_index].has_shield:
            attacker_shield_damage = defender.shield if defender.shield < attacker_armor_damage else attacker_armor_damage
            defender.shield -= attacker_shield_damage
            attacker_armor_damage -= attacker_shield_damage 
        if attacker_armor_damage > 0:
            defender.armor -= attacker_armor_damage
        # Stamina loss and gain
        attacker_stamina_loss = attacker.template.weapons[attack_weapon_index].fighting_stamina_usage - attacker.template.stamina_regen
        attacker.stamina -= attacker_stamina_loss
        defender_stamina_loss = defender.template.weapons[defend_weapon_index].fighting_stamina_usage - defender.template.stamina_regen
        defender.stamina -= defender_stamina_loss
        # Morale loss and gain
        attacker_morale_loss = Unit.morale_loss_from_combat(attacker, defender_killing_power, attacker_killing_power) + Unit.morale_loss_from_stamina(attacker)
        attacker.morale -= attacker_morale_loss
        defender_morale_loss = Unit.morale_loss_from_combat(defender, attacker_killing_power, defender_killing_power) + Unit.morale_loss_from_stamina(defender)
        defender.morale -= defender_morale_loss
        # Check for unit death or fleeing
        if attacker.pop <= 0:
            attacker.die()
        elif attacker.morale <= 0:
            attacker.flee()
        if defender.pop <= 0:
            defender.die()
        elif defender.morale <= 0:
            defender.flee()
        # Create and return combat report
        attacker_report = UnitCombatReport(attacker, attack_weapon_index, math.ceil(defender_killing_power), attacker_morale_loss,
                                           attacker_stamina_loss, defender_shield_damage, defender_armor_damage,
                                           died=not attacker.alive, fled=attacker.fleeing, direction=direction, charged=charging)
        defender_report = UnitCombatReport(defender, defend_weapon_index, math.ceil(attacker_killing_power), defender_morale_loss,
                                           defender_stamina_loss, attacker_shield_damage, attacker_armor_damage,
                                           died=not defender.alive, fled=defender.fleeing, direction=direction, charged=False)
        combat_report = CombatReport(attacker, defender, attacker_report, defender_report)
        return combat_report

    @staticmethod
    def ranged_fight(attacker, defender, attack_weapon_index=0, defend_weapon_index=0, direction=RelativeDirection.front):
        """ Triggers a round of ranged battle between two units.

        Positional arguments:
        attacker -- the attacking Unit
        defender -- the defending Unit
        direction -- the relative direction from the attacker to the defender.
                     Front by default
        """
        # Calculate killing power
        attacker_killing_power = Unit.ranged_killing_power(attacker, defender, attack_weapon_index=attack_weapon_index, defend_weapon_index=defend_weapon_index)
        # Deal health damage
        defender.pop -= attacker_killing_power
        # Deal armor damage
        attacker_armor_damage = attacker.template.weapons[attack_weapon_index].ranged_piercing * Unit.ARMOR_DESTRUCTION_RATIO * (1 - Unit.stamina_attack_reduction_ratio(attacker))
        attacker_shield_damage = defender.shield if defender.shield < attacker_armor_damage else attacker_armor_damage
        defender.shield -= attacker_shield_damage
        attacker_armor_damage -= attacker_shield_damage 
        if attacker_armor_damage > 0:
            defender.armor -= attacker_armor_damage
        # Stamina loss and gain
        attacker_stamina_loss = attacker.template.weapons[attack_weapon_index].ranged_fighting_stamina_usage - attacker.template.stamina_regen
        attacker.stamina -= attacker_stamina_loss
        # Morale loss and gain
        attacker_morale_loss = Unit.morale_loss_from_stamina(attacker)
        attacker.morale -= attacker_morale_loss
        defender_morale_loss = Unit.morale_loss_from_ranged_combat(defender, attacker_killing_power) + Unit.morale_loss_from_stamina(defender)
        defender.morale -= defender_morale_loss
        # Check for unit death or fleeing
        if attacker.morale <= 0:
            attacker.flee()
        if defender.pop <= 0:
            defender.die()
        elif defender.morale <= 0:
            defender.flee()
        # Create and return combat report
        attacker_report = UnitCombatReport(attacker, attack_weapon_index, 0, attacker_morale_loss,
                                           attacker_stamina_loss, 0, 0,
                                           died=False, fled=attacker.fleeing, direction=direction, charged=False)
        defender_report = UnitCombatReport(defender, defend_weapon_index, math.ceil(attacker_killing_power), defender_morale_loss,
                                           0, attacker_shield_damage, attacker_armor_damage,
                                           died=not defender.alive, fled=defender.fleeing, direction=direction, charged=False)
        combat_report = CombatReport(attacker, defender, attacker_report, defender_report)
        return combat_report

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
    
    def ranged_armor_defense(self, weapon_index=0, direction=RelativeDirection.front):
        """ Calculates the ranged defense power of this unit from armor.

            Positional arguments:
            direction -- the direction this unit is being attacked from

            Return:
            The defense power this unit gains from its armor (and possibly
            shield).
        """
        armor_def = self.armor + (self.shield * 3)
        return armor_def

    def die(self):
        self.alive = False
    
    def flee(self):
        self.fleeing = True

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
        return Unit.attack_power(attacker, defender, attack_weapon_index=attack_weapon_index, defend_weapon_index=attack_weapon_index, charging=charging)\
            / Unit.defense_power(defender, attacker, attack_weapon_index=attack_weapon_index, defend_weapon_index=attack_weapon_index)\
            * Unit.KILLING_POWER_RATIO
        
    @staticmethod
    def ranged_killing_power(attacker, defender, attack_weapon_index=0, defend_weapon_index=0):
        return Unit.ranged_attack_power(attacker, defender, attack_weapon_index=attack_weapon_index, defend_weapon_index=defend_weapon_index)\
            / Unit.ranged_defense_power(defender, attacker, attack_weapon_index=attack_weapon_index, defend_weapon_index=defend_weapon_index)\
            * Unit.KILLING_POWER_RATIO

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
        atk_pow *= 1 - (Unit.stamina_attack_reduction_ratio(attacker) + Unit.morale_attack_reduction_ratio(attacker))
        return atk_pow
    
    @staticmethod
    def ranged_attack_power(attacker, defender, attack_weapon_index=0, defend_weapon_index=0):
        """ Calculates the ranged attack power of the attacker unit against the
            defender unit.

            Positional arguments:
            attacker -- the 'attacking' unit whose ranged attack power will be found
            defender -- the 'defending' unit


            Return:
            The ranged attack power of the attacker versus the defender.
        """
        atk_pow = attacker.template.weapons[attack_weapon_index].ranged_attack
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
    def ranged_defense_power(defender, attacker, attack_weapon_index=0, defend_weapon_index=0, direction=RelativeDirection.front):
        """ Calculates the ranged defense power of the defender unit against the
            attacker unit.

            Positional arguments:
            defender -- the 'defending' unit whose defense power will be found
            attacker -- the 'attacking' unit

            Return:
            The ranged defense power of the defender versus the attacker.
        """
        def_pow = defender.template.weapons[defend_weapon_index].defense / 2
        armor_val = defender.ranged_armor_defense()
        armor_val -= attacker.template.weapons[attack_weapon_index].ranged_piercing
        armor_val = 0 if armor_val < 0 else armor_val
        def_pow += armor_val
        return def_pow
    
    @staticmethod
    def stamina_attack_reduction_ratio(attacker):
        return ((1 - (attacker.stamina / attacker.template.max_stamina)) * Unit.MAX_STAMINA_ATTACK_REDUCTION_RATIO)

    @staticmethod
    def morale_attack_reduction_ratio(attacker):
        return ((1 - (attacker.morale / attacker.template.max_morale)) * Unit.MAX_MORALE_ATTACK_REDUCTION_RATIO)
    
    @staticmethod
    def morale_loss_from_combat(unit, friendly_losses, enemy_losses):
        return ((friendly_losses / enemy_losses) + (1 - (unit.pop / unit.template.max_pop))) * Unit.MORALE_LOSS_FROM_COMBAT_FACTOR
    
    @staticmethod
    def morale_loss_from_ranged_combat(unit, friendly_losses):
        return (friendly_losses / unit.template.max_pop) * Unit.MORALE_LOSS_FROM_RANGED_COMBAT_FACTOR
    
    @staticmethod
    def morale_loss_from_stamina(unit):
        return (1 - (unit.stamina / unit.template.max_stamina)) * Unit.MORALE_LOSS_FROM_STAMINA_FACTOR


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
        self.reports = []
        self.active = True
        self.winner = None
        self.loser = None

    def battle(self):
        """ Triggers a round of battle between the attacker and defender.
        """
        self.reports.append(Unit.fight(self.attacker, self.defender, direction=self.direction, charging=self.charging))
        self.round += 1
        self.charging = False
        if not self.attacker.alive or self.attacker.fleeing:
            self.active = False
            if self.defender.alive and not self.defender.fleeing:
                self.winner = self.defender
                self.loser = self.attacker
        if not self.defender.alive or self.defender.fleeing:
            self.active = False
            if self.attacker.alive and not self.attacker.fleeing:
                self.winner = self.attacker
                self.loser = self.defender

    def __str__(self):
        s = "BATTLE LINK REPORT - {0.attacker.template.name} vs {0.defender.template.name} - {0.round} ROUNDS"
        for i in range(len(self.reports)):
            s += "\n\nRound " + str(i)
            s += "\n" + str(self.reports[i])
        if self.winner and self.loser:
            s += "\n\nWinner: {0.winner.template.name}\tLoser ({1}): {0.loser.template.name}\tNum Rounds: {0.round}\n".format(self, "Dead" if not self.loser.alive else "Fleeing" if self.loser.fleeing else "")
        else:
            s+= "\n\nRESULT WAS A TIE\n"
        return s.format(self)


class RangedBattleLink(BattleLink):
    """ A link between a ranged attacking unit and a defending unit.
    """
    def __init__(self, attacker, defender, direction=RelativeDirection.front):
        super().__init__(attacker, defender, direction=direction, charging=False)
    
    def battle(self):
        """ Triggers a round of battle between the attacker and defender.
        """
        self.reports.append(Unit.ranged_fight(self.attacker, self.defender, direction=self.direction))
        self.round += 1
        self.charging = False
        if not self.attacker.alive or self.attacker.fleeing:
            self.active = False
            if self.defender.alive and not self.defender.fleeing:
                self.winner = self.defender
                self.loser = self.attacker
        if not self.defender.alive or self.defender.fleeing:
            self.active = False
            if self.attacker.alive and not self.attacker.fleeing:
                self.winner = self.attacker
                self.loser = self.defender


class CombatReport(object):
    """ A record of a single round of combat between two units.
    """
    def __init__(self, attacker, defender, attacker_report, defender_report):
        self.attacker = attacker
        self.defender = defender
        self.attacker_report = attacker_report
        self.defender_report = defender_report
    
    def __str__(self):
        return str(self.attacker_report) + "\n" + str(self.defender_report)


class UnitCombatReport(object):
    """ A record of a single round of combat for a one unit.
    """
    def __init__(self, unit, weapon_index, health_loss, morale_loss, stamina_loss, shield_loss, armor_loss,
                 died=False, fled=False, direction=RelativeDirection.front, charged=False):
        self.unit = unit
        self.weapon_index = weapon_index
        self.health = unit.pop
        self.health_loss = health_loss
        self.morale = unit.morale
        self.morale_loss = morale_loss
        self.stamina = unit.stamina
        self.stamina_loss = stamina_loss
        self.shield = unit.shield
        self.shield_loss = shield_loss
        self.armor = unit.armor
        self.armor_loss = armor_loss
        self.died = died
        self.fled = fled
        self.direction = direction
        self.charged = charged
    
    def __str__(self):
        s = "{0.unit.template.name} Status:"
        s += "\n\tHealth = {0.health}/{0.unit.template.max_pop} (-{0.health_loss})"
        s += "\n\tMorale = {0.morale}/{0.unit.template.max_morale} (-{0.morale_loss})"
        s += "\n\tStamina = {0.stamina}/{0.unit.template.max_stamina} (-{0.stamina_loss})"
        s += "\n\tArmor = {0.armor}/{0.unit.template.armor} (-{0.armor_loss})"
        s += "\n\tShield = {0.shield}/{0.unit.template.shield} (-{0.shield_loss})"
        return s.format(self)
