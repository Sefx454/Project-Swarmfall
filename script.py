"""PROJECT-SWARMFALL — field-engineer core defense.
Python 3.10+ / Tkinter only. No image files or third-party packages needed.
"""
from __future__ import annotations
import math
import random
import heapq
import time
import json
from pathlib import Path
from collections import deque, defaultdict
from dataclasses import dataclass, field
import tkinter as tk

MAP_NAMES = ('Verdant Basin', 'Amber Pass', 'Bluewater Station')

MAP_NOTES = ('Open fields, stone outcrops, room to expand.', 'Rocky corridors reward clever walls and gates.', 'Water divides your base into connected districts.')

COLORS = dict(bg='#101f31', panel='#192c40', card='#22394e', line='#35536a', text='#edf5f6', muted='#a5becd', blue='#63c8ec', green='#85dfab', gold='#ffd580', red='#ff917f', purple='#bea6f4')

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

ROBOTS = [{'name': 'Ranger',
  'price': 100,
  'metal': 22,
  'circuits': 4,
  'crystal': 0,
  'color': '#72c9e8',
  'chassis': 'humanoid',
  'role': 'rifle',
  'range': 4.2,
  'damage': 19,
  'cooldown': 0.65,
  'power': 1,
  'hp': 300,
  'paths': (('Precision',
             [{'name': 'Calibrated sights',
               'price': 85,
               'description': '+25% range; target armored bugs.',
               'effects': {'range': 1.25, 'priority': 1}},
              {'name': 'Armor-break rounds',
               'price': 210,
               'description': 'Shots ignore armor and mark targets.',
               'effects': {'pierce_armor': 1, 'mark': 1}},
              {'name': 'Overwatch burst',
               'price': 480,
               'description': 'Three shots per trigger; +35% damage.',
               'effects': {'burst': 3, 'damage': 1.35}}]),
            ('Rapid response',
             [{'name': 'Quick loader',
               'price': 80,
               'description': 'Fire 25% faster.',
               'effects': {'rate': 1.25}},
              {'name': 'Twin receivers',
               'price': 195,
               'description': 'Fire two bullets per trigger.',
               'effects': {'burst': 2}},
              {'name': 'Swarm sweeper',
               'price': 460,
               'description': 'Defeated targets trigger small explosions.',
               'effects': {'death_blast': 1, 'rate': 1.3}}]))},
 {'name': 'Bulwark',
  'price': 180,
  'metal': 38,
  'circuits': 6,
  'crystal': 0,
  'color': '#e5bd7e',
  'chassis': 'heavy',
  'role': 'heavy',
  'range': 3.8,
  'damage': 10,
  'cooldown': 0.18,
  'power': 2,
  'hp': 300,
  'paths': (('Suppression',
             [{'name': 'Belt feed',
               'price': 100,
               'description': '+25% firing speed.',
               'effects': {'rate': 1.25}},
              {'name': 'Pinning fire',
               'price': 240,
               'description': 'Bullets slow targets.',
               'effects': {'slow': 0.72}},
              {'name': 'Rotary storm',
               'price': 540,
               'description': 'Twin shots and much faster barrels.',
               'effects': {'burst': 2, 'rate': 1.45}}]),
            ('Bunker',
             [{'name': 'Reinforced frame',
               'price': 90,
               'description': 'Double structural health.',
               'effects': {'hp': 2}},
              {'name': 'Guard plating',
               'price': 220,
               'description': 'Nearby buildings take 30% less damage.',
               'effects': {'guard': 1}},
              {'name': 'Bastion rounds',
               'price': 500,
               'description': 'Triple damage and improved range.',
               'effects': {'damage': 3, 'range': 1.2}}]))},
 {'name': 'Longshot',
  'price': 200,
  'metal': 26,
  'circuits': 10,
  'crystal': 0,
  'color': '#c3adf2',
  'chassis': 'humanoid',
  'role': 'sniper',
  'range': 7.0,
  'damage': 100,
  'cooldown': 2.1,
  'power': 2,
  'hp': 300,
  'paths': (('Hunter',
             [{'name': 'Long lens',
               'price': 120,
               'description': '+25% range.',
               'effects': {'range': 1.25}},
              {'name': 'Carapace breaker',
               'price': 270,
               'description': 'Ignore armor; +60% damage.',
               'effects': {'pierce_armor': 1, 'damage': 1.6}},
              {'name': 'Colossus hunter',
               'price': 650,
               'description': 'Deals triple damage to elite and boss bugs.',
               'effects': {'boss_bonus': 3}}]),
            ('Spotter',
             [{'name': 'Target beacon',
               'price': 110,
               'description': 'Hit bugs take 20% extra damage.',
               'effects': {'mark': 1}},
              {'name': 'Tracking scope',
               'price': 250,
               'description': 'Fires 60% faster.',
               'effects': {'rate': 1.6}},
              {'name': 'Linked shot',
               'price': 560,
               'description': 'Shots ricochet to two nearby targets.',
               'effects': {'chain': 2}}]))},
 {'name': 'Ember Tank',
  'price': 190,
  'metal': 40,
  'circuits': 7,
  'crystal': 0,
  'color': '#ffab79',
  'chassis': 'tank',
  'role': 'flame',
  'range': 3.0,
  'damage': 16,
  'cooldown': 0.3,
  'power': 2,
  'hp': 300,
  'paths': (('Inferno',
             [{'name': 'Hot mix',
               'price': 110,
               'description': '+35% damage.',
               'effects': {'damage': 1.35}},
              {'name': 'Lingering fire',
               'price': 260,
               'description': 'Flames burn enemies over time.',
               'effects': {'burn': 12}},
              {'name': 'Firestorm',
               'price': 590,
               'description': 'Wider cone; doubled burning damage.',
               'effects': {'splash': 1.6, 'burn': 24, 'damage': 1.3}}]),
            ('Pressure',
             [{'name': 'Long nozzle',
               'price': 100,
               'description': '+30% range.',
               'effects': {'range': 1.3}},
              {'name': 'Pressure jet',
               'price': 240,
               'description': 'Scorches armor and slows targets.',
               'effects': {'mark': 1, 'slow': 0.8}},
              {'name': 'Flash ignition',
               'price': 540,
               'description': 'Attacks ignite a large blast at the target.',
               'effects': {'explosion': 1.6, 'damage': 1.65}}]))},
 {'name': 'Rocket Rover',
  'price': 210,
  'metal': 32,
  'circuits': 10,
  'crystal': 0,
  'color': '#9bdbad',
  'chassis': 'rover',
  'role': 'rocket',
  'range': 5.0,
  'damage': 65,
  'cooldown': 1.8,
  'power': 2,
  'hp': 300,
  'paths': (('Demolition',
             [{'name': 'Bigger warheads',
               'price': 120,
               'description': '+40% blast radius.',
               'effects': {'splash': 1.4}},
              {'name': 'Shaped charge',
               'price': 290,
               'description': 'Ignore armor; +35% damage.',
               'effects': {'pierce_armor': 1, 'damage': 1.35}},
              {'name': 'Cluster payload',
               'price': 650,
               'description': 'Each rocket releases three secondary blasts.',
               'effects': {'cluster': 3}}]),
            ('Guidance',
             [{'name': 'Targeting radar',
               'price': 110,
               'description': '+25% range; rockets hit flying bugs harder.',
               'effects': {'range': 1.25, 'air_bonus': 1.4}},
              {'name': 'Dual launchers',
               'price': 270,
               'description': 'Launch two rockets at once.',
               'effects': {'burst': 2}},
              {'name': 'Rapid salvo',
               'price': 620,
               'description': 'Fires twice as fast.',
               'effects': {'rate': 2}}]))},
 {'name': 'Atlas Mortar',
  'price': 235,
  'metal': 42,
  'circuits': 10,
  'crystal': 0,
  'color': '#e5a5a8',
  'chassis': 'rig',
  'role': 'mortar',
  'range': 7.0,
  'damage': 95,
  'cooldown': 2.8,
  'power': 3,
  'hp': 300,
  'paths': (('Siege',
             [{'name': 'Heavy shell',
               'price': 140,
               'description': '+40% damage.',
               'effects': {'damage': 1.4}},
              {'name': 'Seismic impact',
               'price': 320,
               'description': 'Blasts briefly stun ground bugs.',
               'effects': {'stun': 0.8}},
              {'name': 'Crater maker',
               'price': 740,
               'description': 'Huge splash and +80% damage.',
               'effects': {'splash': 1.7, 'damage': 1.8}}]),
            ('Barrage',
             [{'name': 'Extended barrel',
               'price': 125,
               'description': '+25% range.',
               'effects': {'range': 1.25}},
              {'name': 'Double drop',
               'price': 295,
               'description': 'Two shells per volley.',
               'effects': {'burst': 2}},
              {'name': 'Rolling thunder',
               'price': 680,
               'description': 'Explosions leave damaging ground zones.',
               'effects': {'hazard': 24, 'rate': 1.4}}]))},
 {'name': 'Frost Crawler',
  'price': 155,
  'metal': 24,
  'circuits': 8,
  'crystal': 0,
  'color': '#8edeea',
  'chassis': 'crawler',
  'role': 'cryo',
  'range': 3.8,
  'damage': 10,
  'cooldown': 0.85,
  'power': 2,
  'hp': 300,
  'paths': (('Deep freeze',
             [{'name': 'Cold front',
               'price': 90,
               'description': 'Stronger slowing mist.',
               'effects': {'slow': 0.52}},
              {'name': 'Ice lock',
               'price': 225,
               'description': 'Hits briefly freeze targets.',
               'effects': {'stun': 0.4}},
              {'name': 'Absolute chill',
               'price': 540,
               'description': 'Longer freeze and brittle armor.',
               'effects': {'stun': 0.85, 'mark': 1}}]),
            ('Mist network',
             [{'name': 'Wide diffuser',
               'price': 85,
               'description': '+30% range.',
               'effects': {'range': 1.3}},
              {'name': 'Dense cloud',
               'price': 210,
               'description': 'Doubles affected area.',
               'effects': {'splash': 2}},
              {'name': 'Glacial pulse',
               'price': 490,
               'description': 'Much faster pulses; improved damage.',
               'effects': {'rate': 1.8, 'damage': 3}}]))},
 {'name': 'Rail Strider',
  'price': 280,
  'metal': 38,
  'circuits': 16,
  'crystal': 0,
  'color': '#b1c6df',
  'chassis': 'walker',
  'role': 'rail',
  'range': 6.0,
  'damage': 110,
  'cooldown': 2.1,
  'power': 3,
  'hp': 300,
  'paths': (('Penetrator',
             [{'name': 'Charged coils',
               'price': 160,
               'description': '+35% damage.',
               'effects': {'damage': 1.35}},
              {'name': 'Hypervelocity',
               'price': 370,
               'description': 'Wider piercing beam; ignore armor.',
               'effects': {'beam_width': 0.7, 'pierce_armor': 1}},
              {'name': 'Titan lance',
               'price': 850,
               'description': 'Triple damage against elites and bosses.',
               'effects': {'boss_bonus': 3, 'damage': 1.3}}]),
            ('Capacitor',
             [{'name': 'Fast recharge',
               'price': 145,
               'description': '+30% fire rate.',
               'effects': {'rate': 1.3}},
              {'name': 'Split discharge',
               'price': 340,
               'description': 'A second beam seeks another target.',
               'effects': {'burst': 2}},
              {'name': 'Aftershock',
               'price': 780,
               'description': 'Beam ends in a stunning explosion.',
               'effects': {'explosion': 1.5, 'stun': 0.65}}]))},
 {'name': 'Skyguard',
  'price': 145,
  'metal': 24,
  'circuits': 8,
  'crystal': 0,
  'color': '#f4d77c',
  'chassis': 'rover',
  'role': 'air',
  'range': 6.0,
  'damage': 34,
  'cooldown': 0.6,
  'power': 1,
  'hp': 300,
  'paths': (('Interceptor',
             [{'name': 'Radar array',
               'price': 90,
               'description': '+30% range.',
               'effects': {'range': 1.3}},
              {'name': 'Flak rounds',
               'price': 220,
               'description': 'Shots explode among flying insects.',
               'effects': {'explosion': 1.1}},
              {'name': 'Air superiority',
               'price': 520,
               'description': 'Triple anti-air damage.',
               'effects': {'damage': 3}}]),
            ('Multirole',
             [{'name': 'Ground targeting',
               'price': 85,
               'description': 'Can also attack ground insects.',
               'effects': {'ground': 1}},
              {'name': 'Tracking burst',
               'price': 210,
               'description': 'Fires two shots per trigger.',
               'effects': {'burst': 2}},
              {'name': 'Storm battery',
               'price': 490,
               'description': 'Faster shots that stun briefly.',
               'effects': {'rate': 1.8, 'stun': 0.3}}]))},
 {'name': 'Patch Rover',
  'price': 145,
  'metal': 24,
  'circuits': 10,
  'crystal': 0,
  'color': '#82dfa9',
  'chassis': 'rover',
  'role': 'repair',
  'range': 3.4,
  'damage': 0,
  'cooldown': 1.0,
  'power': 1,
  'hp': 300,
  'paths': (('Mechanic',
             [{'name': 'Precision tools',
               'price': 90,
               'description': '+60% repair strength.',
               'effects': {'heal': 1.6}},
              {'name': 'Repair network',
               'price': 225,
               'description': 'Repair up to three buildings at once.',
               'effects': {'heal_targets': 3}},
              {'name': 'Reconstruction',
               'price': 550,
               'description': 'Repairs add temporary protective shields.',
               'effects': {'shield': 1, 'heal': 1.5}}]),
            ('Field support',
             [{'name': 'Long cable',
               'price': 85,
               'description': '+35% repair range.',
               'effects': {'range': 1.35}},
              {'name': 'Core specialist',
               'price': 210,
               'description': 'Much stronger repairs on the core.',
               'effects': {'core_heal': 3}},
              {'name': 'Service station',
               'price': 500,
               'description': 'Nearby robots fire 20% faster.',
               'effects': {'support_rate': 1.2}}]))},
 {'name': 'Marshal',
  'price': 225,
  'metal': 32,
  'circuits': 16,
  'crystal': 0,
  'color': '#83aef0',
  'chassis': 'heavy',
  'role': 'command',
  'range': 4.0,
  'damage': 18,
  'cooldown': 1.0,
  'power': 2,
  'hp': 300,
  'paths': (('Tactics',
             [{'name': 'Battle uplink',
               'price': 125,
               'description': 'Nearby weapons gain 10% more firing speed.',
               'effects': {'aura_rate': 1.1}},
              {'name': 'Range telemetry',
               'price': 290,
               'description': 'Nearby weapons gain 20% range.',
               'effects': {'aura_range': 1.2}},
              {'name': 'Coordinated assault',
               'price': 700,
               'description': 'Nearby weapons deal 35% more damage.',
               'effects': {'aura_damage': 1.35}}]),
            ('Logistics',
             [{'name': 'Wideband antenna',
               'price': 115,
               'description': '+35% command radius.',
               'effects': {'range': 1.35}},
              {'name': 'Salvage protocol',
               'price': 270,
               'description': 'Kills in range give 40% more dollars.',
               'effects': {'bounty': 1.4}},
              {'name': 'Emergency shielding',
               'price': 640,
               'description': 'Allies in range receive protective shields.',
               'effects': {'shield': 1}}]))},
 {'name': 'Scatter Mech',
  'price': 140,
  'metal': 28,
  'circuits': 5,
  'crystal': 0,
  'color': '#e9a0ce',
  'chassis': 'humanoid',
  'role': 'scatter',
  'range': 2.9,
  'damage': 15,
  'cooldown': 0.95,
  'power': 1,
  'hp': 300,
  'paths': (('Breach',
             [{'name': 'Dense pellets',
               'price': 90,
               'description': '+35% pellet damage.',
               'effects': {'damage': 1.35}},
              {'name': 'Slug spread',
               'price': 220,
               'description': 'Ignore armor and fire two extra pellets.',
               'effects': {'pierce_armor': 1, 'pellets': 7}},
              {'name': 'Point blank',
               'price': 530,
               'description': 'Double damage; hits briefly stun.',
               'effects': {'damage': 2, 'stun': 0.25}}]),
            ('Crowd control',
             [{'name': 'Wide choke',
               'price': 85,
               'description': '+20% range and wider spread.',
               'effects': {'range': 1.2, 'cone': 1.5}},
              {'name': 'Concussion shot',
               'price': 210,
               'description': 'Pellets slow enemies.',
               'effects': {'slow': 0.62}},
              {'name': 'Volley engine',
               'price': 500,
               'description': 'Double firing speed; nine pellets.',
               'effects': {'rate': 2, 'pellets': 9}}]))}]

STRUCTURES = [{'name': 'Wall',
  'price': 12,
  'metal': 12,
  'circuits': 0,
  'crystal': 0,
  'color': '#adbac8',
  'role': 'wall',
  'hp': 850,
  'power': 0},
 {'name': 'Gate',
  'price': 30,
  'metal': 20,
  'circuits': 2,
  'crystal': 0,
  'color': '#e7c78d',
  'role': 'gate',
  'hp': 700,
  'power': 0},
 {'name': 'Relay Generator',
  'price': 100,
  'metal': 34,
  'circuits': 10,
  'crystal': 0,
  'color': '#91dcd8',
  'role': 'generator',
  'hp': 450,
  'power': 0},
 {'name': 'Mining Rig',
  'price': 100,
  'metal': 28,
  'circuits': 8,
  'crystal': 0,
  'color': '#e6be75',
  'role': 'mine',
  'hp': 380,
  'power': 1},
 {'name': 'Shield Pylon',
  'price': 180,
  'metal': 35,
  'circuits': 14,
  'crystal': 5,
  'color': '#b7a0ee',
  'role': 'shield',
  'hp': 450,
  'power': 3}]

SPECS = ROBOTS + STRUCTURES

BUGS = {'Ant': (55, 1.15, 9, 9, '#915c3c', 'bite', 18, 0.9),
 'Beetle': (210, 0.67, 17, 13, '#447561', 'ram', 45, 1.0),
 'Termite': (85, 1.0, 12, 10, '#d7b982', 'chew', 24, 1.0),
 'Cockroach': (110, 1.65, 14, 11, '#a57b50', 'scuttle', 18, 0.95),
 'Wasp': (105, 1.4, 17, 11, '#efd16a', 'sting', 26, 1.1),
 'Grasshopper': (170, 1.1, 21, 13, '#91ba65', 'leap', 30, 1.0),
 'Mantis': (280, 0.95, 28, 15, '#74a96a', 'slash', 48, 1.5),
 'Moth': (180, 1.0, 23, 14, '#c2b397', 'dust', 10, 3.2),
 'Stag Beetle': (650, 0.6, 40, 18, '#675b4d', 'crush', 70, 1.2),
 'Dragonfly': (200, 1.9, 27, 13, '#6dbfc5', 'dive', 35, 1.2),
 'Ladybug': (350, 0.78, 30, 14, '#e77e69', 'shell', 30, 1.1),
 'Bombardier Beetle': (410, 0.75, 36, 15, '#b1966e', 'spray', 24, 3.6),
 'Goliath Beetle': (36000, 0.34, 1600, 34, '#857b68', 'boss', 150, 1.4)}

FLIERS = {'Wasp', 'Moth', 'Dragonfly'}

@dataclass
class Building:
    x: int
    y: int
    kind: int
    hp: float = 0
    paths: list = field(default_factory=lambda: [0, 0])
    cooldown: float = 0
    invested: int = 0
    opened: bool = False
    angle: float = -0.8
    shield: float = 0
    jam: float = 0
    animation: float = 0

    def __post_init__(self):
        self.hp = self.stats()['hp']
        self.invested = self.spec['price']

    @property
    def spec(self):
        return SPECS[self.kind]

    @property
    def role(self):
        return self.spec['role']

    @property
    def pos(self):
        return (self.x + 0.5, self.y + 0.5)

    def stats(self):
        s = dict(range=self.spec.get('range', 0), damage=self.spec.get('damage', 0), rate=1.0, hp=self.spec['hp'], burst=1, splash=1.0, slow=0.7 if self.role == 'cryo' else 1.0, heal=1.0, heal_targets=1, core_heal=1.0, aura_rate=1.15, aura_range=1.0, aura_damage=1.0, bounty=1.0, pellets=5, cone=1.0, beam_width=0.32, air_bonus=1.0, boss_bonus=1.0, burn=0.0, stun=0.0, mark=0.0, ground=0, shield=0, pierce_armor=0, death_blast=0, chain=0, explosion=0, cluster=0, hazard=0, support_rate=1.0)
        for path, tier in enumerate(self.paths):
            if not tier:
                continue
            for u in self.spec.get('paths', ())[path][1][:tier]:
                for key, value in u['effects'].items():
                    if key in ('range', 'damage', 'rate', 'hp', 'heal', 'core_heal', 'splash', 'aura_rate'):
                        s[key] *= value
                    else:
                        s[key] = value
        return s

    def next_upgrade(self, path):
        if self.kind >= len(ROBOTS) or self.paths[path] >= 3:
            return None
        return self.spec['paths'][path][1][self.paths[path]]

    def upgrade_locked(self, path):
        return self.paths[path] >= 3 or (self.paths[1 - path] >= 2 and self.paths[path] >= 1)

@dataclass
class Enemy:
    name: str
    x: float
    y: float
    wave: int
    hp: float = 0
    maxhp: float = 0
    angle: float = 0
    timer: float = 1
    ability: float = 4
    slow: float = 1
    slow_time: float = 0
    stun: float = 0
    burn: float = 0
    burn_time: float = 0
    marked: float = 0
    dead: bool = False
    waypoint: tuple | None = None
    nav_version: int = -1
    last_source: Building | None = None

    def __post_init__(self):
        scale = 1 + 0.095 * (self.wave - 1) + 0.002 * (self.wave - 1) ** 2
        self.hp = self.maxhp = BUGS[self.name][0] * (1 if self.name == 'Goliath Beetle' else scale)

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def flying(self):
        return self.name in FLIERS

    @property
    def role(self):
        return BUGS[self.name][5]

class World:
    """Game simulation independent of Tk, so it can be tested without a window."""

    def __init__(self, mapid=0):
        self.mapid = mapid
        self.rng = random.Random(920 + mapid)
        self.core = (14, 11)
        self.corepos = (14.5, 11.5)
        self.corehp = self.coremax = 4500
        self.money = 1250
        self.materials = dict(metal=300, circuits=80, crystal=12)
        self.buildings = {}
        self.enemies = []
        self.projectiles = []
        self.effects = []
        self.hazards = []
        self.terrain = set()
        self.deposits = {}
        self.spawns = [(0, 4), (27, 17), (13, 0), (13, 21)]
        self.wave = 0
        self.queue = deque()
        self.spawn_timer = 0
        self.active = False
        self.autoplay = False
        self.intermission = 8.0
        self.outcome = ''
        self.kills = 0
        self.elapsed = 0
        self.message = 'Choose defenses, gather materials, then launch wave 1.'
        self.message_time = 10
        self.shake = 0
        self.nav_version = 0
        self.mine_timer = 0
        self.harvest_timer = 0
        self.generate_map()
        self.repath()

    def generate_map(self):
        for y in range(NY):
            for x in range(NX):
                blocked = x in (8, 9) and 3 <= y <= 7 or (19 <= x <= 22 and y in (15, 16)) if self.mapid == 0 else x in (7, 8, 19, 20) and y not in (4, 5, 6, 10, 11, 15, 16, 17) if self.mapid == 1 else (x - 8) ** 2 + (y - 6) ** 2 < 13 or (x - 21) ** 2 + (y - 16) ** 2 < 13
                if blocked and distance((x, y), self.core) > 3:
                    self.terrain.add((x, y))
        for x, y, resource in [(11, 8, 'metal'), (17, 13, 'circuits'), (12, 15, 'crystal'), (3, 10, 'metal'), (23, 6, 'circuits'), (18, 3, 'metal'), (4, 18, 'crystal')]:
            if (x, y) not in self.terrain:
                self.deposits[x, y] = [resource, 250 if resource == 'metal' else 120]

    def say(self, message):
        self.message, self.message_time = (message, 5)

    def fx(self, kind, pos, color, duration=0.4, size=1, end=None, text=''):
        self.effects.append(dict(kind=kind, pos=pos, end=end, color=color, ttl=duration, life=duration, size=size, text=text))

    def connected_relays(self):
        connected = set()
        pending = [p for p, b in self.buildings.items() if b.role == 'generator']
        while pending:
            added = [p for p in pending if distance((p[0] + 0.5, p[1] + 0.5), self.corepos) <= 7 or any((distance(p, q) <= 5 for q in connected))]
            if not added:
                break
            connected.update(added)
            pending = [p for p in pending if p not in connected]
        return connected

    def in_network(self, pos, relays=None):
        relays = self.connected_relays() if relays is None else relays
        return distance(pos, self.corepos) <= 7 or any((distance(pos, (x + 0.5, y + 0.5)) <= 5 for x, y in relays))

    def power(self):
        relays = self.connected_relays()
        return (12 + len(relays) * 8, sum((b.spec['power'] for b in self.buildings.values())))

    def can_place(self, x, y, kind):
        if not (0 <= x < NX and 0 <= y < NY):
            return 'Outside the map.'
        if (x, y) in self.terrain or (x, y) == self.core or (x, y) in self.buildings or ((x, y) in self.spawns):
            return 'That tile is occupied.'
        if (x, y) in self.deposits:
            return 'Keep deposits clear; place a mining rig beside them.'
        if not self.in_network((x + 0.5, y + 0.5)):
            return 'Extend your build area with a connected relay generator.'
        if any((distance(e.pos, (x + 0.5, y + 0.5)) < 0.8 and (not e.flying) for e in self.enemies)):
            return 'A bug is on that tile.'
        spec = SPECS[kind]
        if spec['role'] == 'mine' and (not any((distance((x, y), p) <= 2 for p, d in self.deposits.items() if d[1] > 0))):
            return 'Mining rigs need a deposit within 2 tiles.'
        if self.money < spec['price']:
            return 'Not enough dollars.'
        for res in self.materials:
            if self.materials[res] < spec.get(res, 0):
                return f'Not enough {res}. Salvage deposits or build mining rigs.'
        return ''

    def place(self, x, y, kind):
        error = self.can_place(x, y, kind)
        if error:
            self.say(error)
            return False
        spec = SPECS[kind]
        self.money -= spec['price']
        for res in self.materials:
            self.materials[res] -= spec.get(res, 0)
        b = Building(x, y, kind)
        self.buildings[x, y] = b
        self.repath()
        self.fx('build', b.pos, spec['color'], 0.6, 1)
        return True

    def salvage(self, pos):
        if self.harvest_timer > 0:
            self.say('Salvage tool recharging.')
            return
        if pos not in self.deposits or self.deposits[pos][1] <= 0:
            self.say('Click a resource deposit to salvage it.')
            return
        if not self.in_network((pos[0] + 0.5, pos[1] + 0.5)):
            self.say('Connect a relay before salvaging this deposit.')
            return
        res, remaining = self.deposits[pos]
        amount = min(remaining, 16 if res == 'metal' else 8)
        self.materials[res] += amount
        self.deposits[pos][1] -= amount
        self.harvest_timer = 1.5
        self.fx('text', (pos[0] + 0.5, pos[1] + 0.5), COLORS['gold'], 1, text=f'+{amount} {res}')

    def buy_upgrade(self, b, path):
        if b.upgrade_locked(path):
            self.say('Path locked: only tier 1 is allowed after specializing in the other path.')
            return False
        u = b.next_upgrade(path)
        if not u:
            return False
        if self.money < u['price']:
            self.say('Not enough dollars for that upgrade.')
            return False
        oldmax = b.stats()['hp']
        self.money -= u['price']
        b.invested += u['price']
        b.paths[path] += 1
        b.hp += b.stats()['hp'] - oldmax
        self.fx('upgrade', b.pos, COLORS['gold'], 0.9, 1.4)
        self.say(f"{b.spec['name']}: {u['name']} installed.")
        return True

    def sell(self, pos):
        b = self.buildings.pop(pos, None)
        if not b:
            return
        self.money += int(b.invested * 0.7)
        for res in self.materials:
            self.materials[res] += int(b.spec.get(res, 0) * 0.5)
        self.fx('text', b.pos, COLORS['gold'], 1, text=f'+{int(b.invested * 0.7)} dollars')
        self.repath()

    def repair(self, b):
        missing = b.stats()['hp'] - b.hp
        cost, metal = (math.ceil(missing * 0.1), math.ceil(missing * 0.025))
        if self.money < cost or self.materials['metal'] < metal:
            self.say('Repair needs more dollars or metal.')
            return
        self.money -= cost
        self.materials['metal'] -= metal
        b.hp = b.stats()['hp']
        self.fx('repair', b.pos, COLORS['green'], 0.7)

    def repath(self):
        self.nav_version += 1
        blocked = self.terrain | {p for p, b in self.buildings.items() if not (b.role == 'gate' and b.opened)}
        self.nav = {self.core: 0}
        q = deque([self.core])
        while q:
            p = q.popleft()
            for n in self.neighbors(p):
                if n not in blocked and n not in self.nav:
                    self.nav[n] = self.nav[p] + 1
                    q.append(n)
        self.siege = {self.core: 0}
        frontier = [(0, self.core)]
        while frontier:
            cost, p = heapq.heappop(frontier)
            if cost != self.siege[p]:
                continue
            b = self.buildings.get(p)
            extra = 12 if b and (not (b.role == 'gate' and b.opened)) else 0
            for n in self.neighbors(p):
                if n in self.terrain:
                    continue
                nc = cost + 1 + extra
                if nc < self.siege.get(n, float('inf')):
                    self.siege[n] = nc
                    heapq.heappush(frontier, (nc, n))

    @staticmethod
    def neighbors(p):
        x, y = p
        return [(a, b) for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)) if 0 <= a < NX and 0 <= b < NY]

    def start_wave(self):
        if self.active or self.wave >= 40 or self.outcome:
            return
        self.wave += 1
        self.active = True
        roster = list(BUGS)[:-1]
        available = min(len(roster), 2 + (self.wave - 1) // 3)
        count = 11 + self.wave * 3
        self.queue = deque((self.rng.choice(roster[:available]) for _ in range(count)))
        if self.wave == 40:
            self.queue.insert(16, 'Goliath Beetle')
        self.spawn_timer = 0
        self.say('FINAL WAVE — the Goliath Beetle has arrived!' if self.wave == 40 else f'Wave {self.wave}: {len(self.queue)} bugs incoming.')

    def hurt_building(self, b, amount):
        if (b.x, b.y) not in self.buildings:
            return
        guard = any((t.role == 'heavy' and t.stats().get('guard') and (distance(t.pos, b.pos) <= 3.5) for t in self.buildings.values()))
        if guard:
            amount *= 0.7
        absorbed = min(b.shield, amount)
        b.shield -= absorbed
        amount -= absorbed
        b.hp -= amount
        self.fx('hit', b.pos, COLORS['red'], 0.2, 0.35)
        if b.hp <= 0:
            self.fx('explosion', b.pos, b.spec['color'], 0.6, 1.0)
            del self.buildings[b.x, b.y]
            self.repath()

    def damage(self, e, amount, source=None, stats=None):
        if e.dead:
            return
        stats = stats or {}
        armor = 0.62 if e.name in ('Beetle', 'Stag Beetle', 'Ladybug', 'Goliath Beetle') else 1
        if stats.get('pierce_armor'):
            armor = 1
        if e.marked > 0:
            amount *= 1.2
        if e.name in ('Stag Beetle', 'Goliath Beetle') or getattr(e, 'elite', False):
            amount *= stats.get('boss_bonus', 1)
        if e.flying:
            amount *= stats.get('air_bonus', 1)
        e.hp -= amount * armor
        e.last_source = source or e.last_source
        if stats.get('slow', 1) < 1:
            e.slow = min(e.slow, stats['slow'])
            e.slow_time = 2
        e.stun = max(e.stun, stats.get('stun', 0))
        if stats.get('mark'):
            e.marked = 4
        if stats.get('burn'):
            e.burn = max(e.burn, stats['burn'])
            e.burn_time = 3
        if e.hp > 0:
            return
        e.dead = True
        self.kills += 1
        bounty = 1
        for b in self.buildings.values():
            if b.role == 'command' and distance(b.pos, e.pos) <= b.stats()['range']:
                bounty = max(bounty, b.stats()['bounty'])
        self.money += int(BUGS[e.name][2] * bounty)
        self.materials['metal'] += 2 if e.name not in FLIERS else 1
        if self.rng.random() < 0.3:
            self.materials['circuits'] += 1
        if e.name in ('Stag Beetle', 'Bombardier Beetle') or self.rng.random() < 0.035:
            self.materials['crystal'] += 1
        self.fx('defeat', e.pos, BUGS[e.name][4], 0.45, 0.5)
        if source and stats.get('death_blast'):
            self.fx('explosion', e.pos, COLORS['gold'], 0.4, 0.8)
            secondary = dict(stats, death_blast=0)
            for other in self.enemies:
                if not other.dead and distance(other.pos, e.pos) < 1:
                    self.damage(other, 35, source, secondary)

    def launch(self, b, e, stats, role, damage, offset=0):
        speed = 7 if role == 'mortar' else 10 if role == 'rocket' else 22
        self.projectiles.append(dict(x=b.pos[0], y=b.pos[1], origin=b.pos, target=e, dest=e.pos, stats=dict(stats), role=role, damage=damage, source=b, speed=speed, age=-offset, life=5))

    def impact(self, p):
        role, s = (p['role'], p['stats'])
        pos = (p['x'], p['y'])
        splash = (1.45 if role == 'mortar' else 1.05 if role == 'rocket' else 0) * s['splash']
        splash = max(splash, s.get('explosion', 0))
        if splash:
            self.fx('explosion', pos, COLORS['blue'] if role == 'air' else COLORS['gold'], 0.55, splash)
            if role == 'mortar':
                self.shake = max(self.shake, 2)
            for e in self.enemies:
                if not e.dead and distance(e.pos, pos) <= splash:
                    if role == 'air' and (not e.flying):
                        continue
                    self.damage(e, p['damage'], p['source'], s)
            if s['cluster']:
                for i in range(s['cluster']):
                    a = i * math.tau / s['cluster']
                    q = (pos[0] + math.cos(a), pos[1] + math.sin(a))
                    self.fx('explosion', q, '#ffb37c', 0.5, 0.7)
                    for e in self.enemies:
                        if not e.dead and distance(e.pos, q) < 0.85:
                            self.damage(e, p['damage'] * 0.4, p['source'], s)
            if s['hazard']:
                self.hazards.append(dict(pos=pos, ttl=3, damage=s['hazard'], source=p['source'], radius=splash))
        else:
            e = p['target']
            if not e.dead:
                self.damage(e, p['damage'], p['source'], s)
            self.fx('hit', pos, p['source'].spec['color'], 0.2, 0.35)
            if s['chain']:
                others = sorted([q for q in self.enemies if not q.dead and distance(q.pos, pos) < 2], key=lambda q: distance(q.pos, pos))[:s['chain']]
                previous = pos
                for q in others:
                    self.fx('beam', previous, COLORS['purple'], 0.25, end=q.pos)
                    self.damage(q, p['damage'] * 0.65, p['source'], s)
                    previous = q.pos

    def operate_buildings(self, dt):
        supply, used = self.power()
        relays = self.connected_relays()
        efficiency = min(1, supply / max(1, used))
        for b in list(self.buildings.values()):
            b.cooldown -= dt
            b.animation = max(0, b.animation - dt)
            b.jam = max(0, b.jam - dt)
            b.shield = max(0, b.shield - dt * 1.5)
            if b.role in ('wall', 'gate', 'generator'):
                continue
            if b.cooldown > 0:
                continue
            s = b.stats()
            net = self.in_network(b.pos, relays)
            power = efficiency * (1 if net else 0.2) * (0.45 if b.jam else 1)
            if b.role == 'mine':
                if net:
                    candidates = [(p, d) for p, d in self.deposits.items() if d[1] > 0 and distance((b.x, b.y), p) <= 2]
                    if candidates:
                        p, d = min(candidates, key=lambda pd: distance((b.x, b.y), pd[0]))
                        amount = min(d[1], 4 if d[0]=='metal' else 2 if d[0]=='circuits' else 1)
                        d[1] -= amount
                        self.materials[d[0]] += amount
                        self.fx('beam', b.pos, COLORS['gold'], 0.6, end=(p[0] + 0.5, p[1] + 0.5))
                        self.fx('text', b.pos, COLORS['gold'], 1, text=f'+{amount} {d[0]}')
                b.cooldown = 10 / max(0.2,power)
                continue
            if b.role in ('repair', 'shield'):
                radius = s['range'] if b.role == 'repair' else 3.0
                if b.role == 'shield':
                    for t in self.buildings.values():
                        if distance(b.pos, t.pos) <= radius:
                            t.shield = min(120, t.shield + 18 * power)
                    self.fx('ring', b.pos, COLORS['purple'], 0.8, radius)
                    b.cooldown = 2
                    continue
                hurt = sorted([t for t in self.buildings.values() if t.hp < t.stats()['hp'] and distance(b.pos, t.pos) <= radius], key=lambda t: t.hp / t.stats()['hp'])
                for t in hurt[:s['heal_targets']]:
                    t.hp = min(t.stats()['hp'], t.hp + 40 * s['heal'] * power)
                    if s['shield']:
                        t.shield = min(150, t.shield + 35)
                    self.fx('beam', b.pos, COLORS['green'], 0.5, end=t.pos)
                    self.fx('repair', t.pos, COLORS['green'], 0.5)
                if distance(b.pos, self.corepos) <= radius and self.corehp < self.coremax:
                    self.corehp = min(self.coremax, self.corehp + 12 * s['core_heal'] * power)
                    self.fx('beam', b.pos, COLORS['green'], 0.5, end=self.corepos)
                b.cooldown = 1 / max(0.2, power)
                continue
            rate, extra_range, extra_damage = (1.0, 1.0, 1.0)
            for t in self.buildings.values():
                ts = t.stats()
                if t.role == 'command' and distance(b.pos, t.pos) <= ts['range']:
                    rate = max(rate, ts['aura_rate'])
                    extra_range = max(extra_range, ts['aura_range'])
                    extra_damage = max(extra_damage, ts['aura_damage'])
                    if ts['shield']:
                        b.shield = min(130, b.shield + 15)
                if t.role == 'repair' and distance(b.pos, t.pos) <= ts['range']:
                    rate = max(rate, ts['support_rate'])
            candidates = [e for e in self.enemies if not e.dead and distance(e.pos, b.pos) <= s['range'] * extra_range and (not (b.role == 'air' and (not s['ground']) and (not e.flying))) and (not (b.role in ('flame', 'mortar', 'scatter') and e.flying)) and (not (b.role == 'mortar' and distance(e.pos, b.pos) < 1.5))]
            if not candidates:
                continue
            e = self.choose_target(b, candidates) if hasattr(self, 'choose_target') else min(candidates, key=lambda e: distance(e.pos, self.corepos))
            b.angle = math.atan2(e.y - b.pos[1], e.x - b.pos[0])
            b.animation = 0.18
            damage = s['damage'] * extra_damage
            if b.role == 'flame':
                self.fx('flame', b.pos, '#ffb478', 0.3, s['range'], end=e.pos)
                for q in candidates:
                    a = math.atan2(q.y - b.pos[1], q.x - b.pos[0])
                    diff = abs((a - b.angle + math.pi) % math.tau - math.pi)
                    if diff < 0.48 * s['splash']:
                        self.damage(q, damage, b, s)
                if s['explosion']:
                    self.launch(b, e, s, 'rocket', damage)
            elif b.role == 'cryo':
                center = e.pos
                radius = 1.1 * s['splash']
                self.fx('frost', center, COLORS['blue'], 0.65, radius)
                for q in candidates:
                    if distance(q.pos, center) <= radius:
                        self.damage(q, damage, b, s)
            elif b.role == 'rail':
                for target in candidates[:s['burst']]:
                    dx, dy = (target.x - b.pos[0], target.y - b.pos[1])
                    length = max(0.1, math.hypot(dx, dy))
                    end = (b.pos[0] + dx / length * s['range'] * extra_range, b.pos[1] + dy / length * s['range'] * extra_range)
                    self.fx('rail', b.pos, COLORS['blue'], 0.3, end=end)
                    for q in candidates:
                        ex, ey = (q.x - b.pos[0], q.y - b.pos[1])
                        if abs(ex * dy - ey * dx) / length < s['beam_width'] and ex * dx + ey * dy > 0:
                            self.damage(q, damage, b, s)
                    if s['explosion']:
                        self.launch(b, target, s, 'rocket', damage * 0.5)
            elif b.role == 'scatter':
                spread = 0.65 * s['cone']
                pellets = s['pellets']
                for i in range(pellets):
                    a = b.angle + (i / max(1, pellets - 1) - 0.5) * spread
                    end = (b.pos[0] + math.cos(a) * s['range'], b.pos[1] + math.sin(a) * s['range'])
                    self.fx('beam', b.pos, '#ffe8a5', 0.12, end=end)
                    lined = [q for q in candidates if abs((math.atan2(q.y - b.pos[1], q.x - b.pos[0]) - a + math.pi) % math.tau - math.pi) < 0.15]
                    if lined:
                        self.damage(min(lined, key=lambda q: distance(q.pos, b.pos)), damage, b, s)
            else:
                for i in range(s['burst']):
                    self.launch(b, e, s, b.role, damage, i * 0.07)
                self.fx('muzzle', b.pos, COLORS['gold'], 0.12, 0.35, end=e.pos)
            b.cooldown = b.spec['cooldown'] / max(0.15, power) / rate / s['rate']

    def bug_attack(self, e, target):
        """Recognizable insects with distinct gameplay behaviors and attack effects."""
        spec = BUGS[e.name]
        role = e.role
        strength = 1 + self.wave * 0.055
        pos = target.pos if isinstance(target, Building) else self.corepos
        amount = spec[6] * strength
        if role == 'chew' and isinstance(target, Building) and (target.role in ('wall', 'gate')):
            amount *= 3
        if role == 'ram':
            amount *= 1.8 if e.ability <= 0 else 1
            e.ability = 4
        if role == 'scuttle':
            amount *= 0.65
        if role == 'sting':
            self.fx('beam', e.pos, '#eac86a', 0.2, end=pos)
            if isinstance(target, Building):
                target.jam = max(target.jam, 1.5)
        elif role == 'dust':
            self.fx('dust', e.pos, '#d9cdb0', 0.9, 2)
            for b in self.buildings.values():
                if distance(e.pos, b.pos) <= 3:
                    b.jam = 3
        elif role == 'spray':
            self.fx('acid', e.pos, '#c0de79', 0.5, end=pos)
            self.hazards.append(dict(pos=pos, ttl=2, damage=10 * strength, enemy=True, radius=0.8))
        elif role == 'slash':
            self.fx('slash', pos, '#b5e2a3', 0.35, 0.8)
            for b in list(self.buildings.values()):
                if b is not target and distance(b.pos, pos) < 1.3:
                    self.hurt_building(b, amount * 0.4)
        elif role == 'crush':
            self.fx('ring', pos, '#e6c993', 0.5, 1.4)
            for b in list(self.buildings.values()):
                if b is not target and distance(b.pos, pos) < 1.2:
                    self.hurt_building(b, amount * 0.4)
        elif role == 'shell':
            self.fx('ring', e.pos, '#efab92', 0.5, 1.1)
            e.hp = min(e.maxhp, e.hp + e.maxhp * 0.015)
        elif role == 'boss':
            self.fx('shockwave', e.pos, '#f6c586', 0.9, 3)
            self.shake = 6
            for b in list(self.buildings.values()):
                if b is not target and distance(b.pos, e.pos) <= 2.5:
                    self.hurt_building(b, amount * 0.45)
        else:
            self.fx('slash' if role == 'leap' else 'hit', pos, '#f3c49b', 0.3, 0.6)
        if isinstance(target, Building):
            self.hurt_building(target, amount)
        else:
            self.corehp -= amount
            self.shake = max(self.shake, 2)
            self.fx('hit', self.corepos, COLORS['red'], 0.3, 1)
        e.timer = 0.45 if role == 'scuttle' else 1.8 if role in ('boss', 'spray', 'crush') else 1.1

    def move_enemies(self, dt):
        spawned = []
        for e in self.enemies:
            if e.dead:
                continue
            e.timer -= dt
            e.ability -= dt
            e.marked = max(0, e.marked - dt)
            e.slow_time = max(0, e.slow_time - dt)
            if not e.slow_time:
                e.slow = 1
            e.stun = max(0, e.stun - dt)
            if e.burn_time > 0:
                e.burn_time -= dt
                self.damage(e, e.burn * dt, e.last_source)
                if e.dead:
                    continue
            if e.stun:
                continue
            cell = (min(NX - 1, max(0, int(e.x))), min(NY - 1, max(0, int(e.y))))
            nearby = [b for b in self.buildings.values() if distance(e.pos, b.pos) <= BUGS[e.name][7]]
            target = None
            if e.role in ('spray', 'dust') and nearby:
                target = min(nearby, key=lambda b: distance(e.pos, b.pos))
            elif distance(e.pos, self.corepos) <= BUGS[e.name][7]:
                target = 'core'
            if target:
                if e.timer <= 0:
                    self.bug_attack(e, target)
                continue
            if e.role == 'boss' and e.ability <= 0:
                for i in range(3):
                    x = max(0.5, min(NX - 0.5, e.x + self.rng.uniform(-1, 1)))
                    y = max(0.5, min(NY - 0.5, e.y + self.rng.uniform(-1, 1)))
                    if (int(x), int(y)) not in self.terrain:
                        spawned.append(Enemy('Ant', x, y, self.wave))
                e.ability = 8
                self.fx('shockwave', e.pos, COLORS['gold'], 1, 2)
            if e.nav_version != self.nav_version:
                e.waypoint = None
                e.nav_version = self.nav_version
            approach=self.approach_destination(e) if hasattr(self,'approach_destination') else None
            if approach is not None:
                destination=approach
            elif e.flying:
                destination = self.corepos
            else:
                if e.waypoint is None:
                    field = self.nav if cell in self.nav else self.siege
                    options = [p for p in self.neighbors(cell) if p in field]
                    if not options:
                        continue

                    def score(p):
                        b = self.buildings.get(p)
                        return field[p] + (12 if b and (not (b.role == 'gate' and b.opened)) else 0)
                    p = min(options, key=score)
                    e.waypoint = (p[0] + 0.5, p[1] + 0.5)
                destination = e.waypoint
                b = self.buildings.get((int(destination[0]), int(destination[1])))
                if e.role == 'leap' and e.ability <= 0:
                    if b and b.role in ('wall', 'gate'):
                        dx, dy = (int(destination[0]) - cell[0], int(destination[1]) - cell[1])
                        landing = (cell[0] + dx * 2, cell[1] + dy * 2)
                        if 0 <= landing[0] < NX and 0 <= landing[1] < NY and (landing not in self.terrain) and (landing not in self.buildings) and (not hasattr(self,'reserved_trails') or landing in self.reserved_trails or self.in_core_area((landing[0]+.5,landing[1]+.5))):
                            old = e.pos
                            e.x, e.y = (landing[0] + 0.5, landing[1] + 0.5)
                            e.waypoint = None
                            e.ability = 7
                            self.fx('leap', old, '#b8dc8f', 0.6, end=e.pos)
                            continue
                if b and (not (b.role == 'gate' and b.opened)):
                    if distance(e.pos, b.pos) <= BUGS[e.name][7]:
                        if e.timer <= 0:
                            self.bug_attack(e, b)
                        continue
            dx, dy = (destination[0] - e.x, destination[1] - e.y)
            dist = math.hypot(dx, dy)
            speed = BUGS[e.name][1] * (1 + min(0.35, self.wave * 0.006)) * e.slow * getattr(e, 'speed_multiplier', 1)
            if e.role == 'dive' and e.ability <= 0:
                speed *= 3
            if e.role == 'dive' and e.ability < -1.2:
                e.ability = 5
            if e.role == 'ram' and e.ability <= 0:
                speed *= 1.6
            step = min(dist, speed * dt)
            if dist > 0.001:
                nx, ny = (e.x + dx / dist * step, e.y + dy / dist * step)
                block = self.buildings.get((int(nx), int(ny)))
                if not e.flying and block and (not (block.role == 'gate' and block.opened)):
                    if e.timer <= 0:
                        self.bug_attack(e, block)
                elif e.flying or (int(nx), int(ny)) not in self.terrain:
                    e.x, e.y = (nx, ny)
                e.angle = math.atan2(dy, dx)
            if dist <= step + 0.001:
                e.waypoint = None
        self.enemies.extend(spawned)

    def update(self, dt):
        if self.outcome:
            return
        self.elapsed += dt
        self.message_time = max(0, self.message_time - dt)
        self.harvest_timer = max(0, self.harvest_timer - dt)
        self.shake = max(0, self.shake - dt * 12)
        if self.active and self.queue:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                spawn = self.rng.choice(self.incoming_spawns() if hasattr(self,'incoming_spawns') else self.spawns[:min(4,1+self.wave//5)])
                self.enemies.append(Enemy(self.queue.popleft(), spawn[0] + 0.5, spawn[1] + 0.5, self.wave))
                self.spawn_timer = max(0.2, 0.75 - self.wave * 0.012)
        self.operate_buildings(dt)
        for p in self.projectiles:
            p['age'] += dt
            p['life'] -= dt
            if p['age'] < 0:
                continue
            if not p['target'].dead and p['role'] != 'mortar':
                p['dest'] = p['target'].pos
            dx, dy = (p['dest'][0] - p['x'], p['dest'][1] - p['y'])
            dist = math.hypot(dx, dy)
            step = p['speed'] * dt
            if dist <= step:
                p['x'], p['y'] = p['dest']
                self.impact(p)
                p['life'] = 0
            elif dist:
                p['x'] += dx / dist * step
                p['y'] += dy / dist * step
        self.projectiles = [p for p in self.projectiles if p['life'] > 0]
        self.move_enemies(dt)
        for h in self.hazards:
            h['ttl'] -= dt
            if h.get('enemy'):
                for b in list(self.buildings.values()):
                    if distance(b.pos, h['pos']) < h['radius']:
                        self.hurt_building(b, h['damage'] * dt)
            else:
                for e in self.enemies:
                    if not e.flying and distance(e.pos, h['pos']) < h['radius']:
                        self.damage(e, h['damage'] * dt, h['source'])
        self.hazards = [h for h in self.hazards if h['ttl'] > 0]
        self.enemies = [e for e in self.enemies if not e.dead]
        for f in self.effects:
            f['ttl'] -= dt
        self.effects = [f for f in self.effects if f['ttl'] > 0][-450:]
        if self.corehp <= 0:
            self.corehp = 0
            self.outcome = 'lost'
        elif self.active and (not self.queue) and (not self.enemies):
            self.active = False
            self.projectiles = []
            self.intermission = 8
            reward = 100 + self.wave * 18
            self.money += reward
            self.materials['metal'] += 18
            self.materials['circuits'] += 5
            self.say(f'Wave cleared! +{reward} dollars, +18 metal, +5 circuits.')
            if self.wave == 40:
                self.outcome = 'won'
        elif not self.active and self.autoplay:
            self.intermission -= dt
            if self.intermission <= 0:
                self.start_wave()

def tint(color, target, amount):
    """Blend two RGB colors without third-party imaging packages."""
    amount = max(0, min(1, amount))
    a = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(target[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join((f'{round(x + (y - x) * amount):02x}' for x, y in zip(a, b)))

def ease(t):
    t = max(0, min(1, t))
    return 1 - (1 - t) ** 3

class CanvasPool:
    """Reuse Canvas objects and update only changed coordinates or properties.

    Unlike deleting and recreating the whole scene, this preserves Tk objects
    and avoids thousands of allocations every frame. Fixed drawing layers keep
    reused items in the proper visual order when objects appear or disappear.
    """
    LAYERS = ('terrain', 'ground', 'actors', 'effects', 'masks', 'hud', 'modal', 'transition')

    def __init__(self, widget, app):
        self.widget = widget
        self.app = app
        self.layer = 'hud'
        self.pools = defaultdict(list)
        self.cursors = defaultdict(int)
        self.hidden = set()
        self.records = {}
        self.width = WIDTH
        self.height = HEIGHT
        self.calls = 0
        self.updated = 0
        self.sequence = defaultdict(list)
        self.previous_sequence = {}
        self.held = set()

    def begin(self):
        self.cursors.clear()
        self.sequence.clear()
        self.held.clear()
        self.calls = 0
        self.updated = 0

    def reuse_layer(self, name):
        self.held.add(name)
        self.sequence[name] = self.previous_sequence.get(name, [])

    def set_layer(self, name):
        self.layer = name

    def coordinates(self, values):
        out = []
        camera_layer = False
        scale = self.app.scale
        ox, oy = self.app.offset
        for i in range(0, len(values), 2):
            x, y = (values[i], values[i + 1])
            if camera_layer:
                x, y = self.app.camera.project(x, y)
            out.extend((round(x * scale + ox, 2), round(y * scale + oy, 2)))
        return tuple(out)

    def create(self, kind, coords, options):
        self.calls += 1
        key = (self.layer, kind)
        index = self.cursors[key]
        self.cursors[key] += 1
        coords = self.coordinates(coords)
        options = dict(options)
        options['tags'] = (self.layer,)
        if kind == 'image':
            options.pop('width', None)
        if index == len(self.pools[key]):
            item = getattr(self.widget, 'create_' + kind)(*coords, **options)
            self.pools[key].append(item)
            self.records[item] = (coords, options)
            self.updated += 1
        else:
            item = self.pools[key][index]
            oldcoords, oldoptions = self.records[item]
            if oldcoords != coords:
                self.widget.coords(item, *coords)
                self.updated += 1
            changed = {name: value for name, value in options.items() if oldoptions.get(name) != value}
            if item in self.hidden:
                changed['state'] = 'normal'
                self.hidden.remove(item)
            if changed:
                self.widget.itemconfigure(item, **changed)
                self.updated += 1
            self.records[item] = (coords, options)
        self.sequence[self.layer].append(item)
        return item

    def create_rectangle(self, *coords, **options):
        return self.create('rectangle', coords, options)

    def create_oval(self, *coords, **options):
        return self.create('oval', coords, options)

    def create_polygon(self, *coords, **options):
        return self.create('polygon', coords, options)

    def create_line(self, *coords, **options):
        return self.create('line', coords, options)

    def create_text(self, *coords, **options):
        return self.create('text', coords, options)

    def create_image(self, *coords, **options):
        return self.create('image', coords, options)

    def end(self):
        for key, pool in self.pools.items():
            if key[0] in self.held:
                continue
            used = self.cursors.get(key, 0)
            for item in pool[used:]:
                if item not in self.hidden:
                    self.widget.itemconfigure(item, state='hidden')
                    self.hidden.add(item)
        for layer in self.LAYERS:
            order = self.sequence.get(layer, [])
            if order != self.previous_sequence.get(layer):
                for item in order:
                    self.widget.tag_raise(item)
                self.previous_sequence[layer] = list(order)
            self.widget.tag_raise(layer)

    def bind(self, *args, **kwargs):
        return self.widget.bind(*args, **kwargs)

    def winfo_width(self):
        return self.widget.winfo_width()

    def winfo_height(self):
        return self.widget.winfo_height()

@dataclass
class WavePlan:
    wave: int
    name: str
    description: str
    focus: str
    count_bonus: int = 0
    health_bonus: float = 1.0
    speed_bonus: float = 1.0

WAVE_DEFINITIONS = [{'wave': 1,
  'name': 'First contact',
  'description': 'Small groups of ants test the perimeter.',
  'focus': 'Ant',
  'count_bonus': 0,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 2,
  'name': 'Under the shell',
  'description': 'Armored beetles join the march.',
  'focus': 'Beetle',
  'count_bonus': 0,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 3,
  'name': 'Long trail',
  'description': 'A longer procession approaches.',
  'focus': 'Ant',
  'count_bonus': 3,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 4,
  'name': 'Fast feet',
  'description': 'Cockroaches close the distance quickly.',
  'focus': 'Cockroach',
  'count_bonus': 0,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 5,
  'name': 'The first rush',
  'description': 'A larger swarm approaches from two sides.',
  'focus': 'Ant',
  'count_bonus': 8,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 6,
  'name': 'Hard shells',
  'description': 'Beetles soak up ordinary bullets.',
  'focus': 'Beetle',
  'count_bonus': 0,
  'health_bonus': 1.15,
  'speed_bonus': 1.0},
 {'wave': 7,
  'name': 'Foundation trouble',
  'description': 'Termites chew through walls.',
  'focus': 'Termite',
  'count_bonus': 0,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 8,
  'name': 'Scuttling column',
  'description': 'Fast ground insects mix with armored escorts.',
  'focus': 'Cockroach',
  'count_bonus': 4,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 9,
  'name': 'Wall test',
  'description': 'Termites probe the outer defenses.',
  'focus': 'Termite',
  'count_bonus': 4,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 10,
  'name': 'Iron procession',
  'description': 'An elite beetle leads the wave.',
  'focus': 'Beetle',
  'count_bonus': 5,
  'health_bonus': 1.1,
  'speed_bonus': 1.0},
 {'wave': 11,
  'name': 'Wings overhead',
  'description': 'Wasps bypass walls and disrupt robots.',
  'focus': 'Wasp',
  'count_bonus': 0,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 12,
  'name': 'Mixed signals',
  'description': 'Wasps and ground bugs attack together.',
  'focus': 'Wasp',
  'count_bonus': 4,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 13,
  'name': 'Over the fence',
  'description': 'Grasshoppers jump single walls.',
  'focus': 'Grasshopper',
  'count_bonus': 0,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 14,
  'name': 'No easy route',
  'description': 'Ground squads look for openings.',
  'focus': 'Termite',
  'count_bonus': 7,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 15,
  'name': 'Crossfire',
  'description': 'A quick swarm attacks from several entrances.',
  'focus': 'Cockroach',
  'count_bonus': 12,
  'health_bonus': 1,
  'speed_bonus': 1.08},
 {'wave': 16,
  'name': 'Sharp approach',
  'description': 'Mantises threaten tightly packed structures.',
  'focus': 'Mantis',
  'count_bonus': 0,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 17,
  'name': 'Heavy escorts',
  'description': 'Armored insects shield the attackers.',
  'focus': 'Beetle',
  'count_bonus': 5,
  'health_bonus': 1.15,
  'speed_bonus': 1.0},
 {'wave': 18,
  'name': 'Spring loaded',
  'description': 'Grasshoppers challenge narrow defensive lines.',
  'focus': 'Grasshopper',
  'count_bonus': 8,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 19,
  'name': 'Dust cloud',
  'description': 'Moths disrupt nearby weapon systems.',
  'focus': 'Moth',
  'count_bonus': 0,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 20,
  'name': 'Mandibles',
  'description': 'An elite stag beetle leads an armored column.',
  'focus': 'Stag Beetle',
  'count_bonus': 8,
  'health_bonus': 1.1,
  'speed_bonus': 1.0},
 {'wave': 21,
  'name': 'High and low',
  'description': 'Flying and armored bugs arrive together.',
  'focus': 'Wasp',
  'count_bonus': 10,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 22,
  'name': 'Shell formation',
  'description': 'Stag beetles crush nearby buildings.',
  'focus': 'Stag Beetle',
  'count_bonus': 3,
  'health_bonus': 1.15,
  'speed_bonus': 1.0},
 {'wave': 23,
  'name': 'Wide wings',
  'description': 'Moths fill the air above the base.',
  'focus': 'Moth',
  'count_bonus': 10,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 24,
  'name': 'Endless legs',
  'description': 'A dense ground wave tests sustained damage.',
  'focus': 'Ant',
  'count_bonus': 22,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 25,
  'name': 'Sudden dive',
  'description': 'Dragonflies make fast diving attacks.',
  'focus': 'Dragonfly',
  'count_bonus': 6,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 26,
  'name': 'Heavy landing',
  'description': 'Stag beetles and airborne scouts converge.',
  'focus': 'Stag Beetle',
  'count_bonus': 8,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 27,
  'name': 'Cutting edge',
  'description': 'Mantises attack the front line.',
  'focus': 'Mantis',
  'count_bonus': 10,
  'health_bonus': 1.1,
  'speed_bonus': 1.0},
 {'wave': 28,
  'name': 'Red armor',
  'description': 'Ladybugs bring tough defensive shells.',
  'focus': 'Ladybug',
  'count_bonus': 4,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 29,
  'name': 'Four directions',
  'description': 'A mixed wave surrounds the base.',
  'focus': 'Dragonfly',
  'count_bonus': 12,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 30,
  'name': 'Crushing pressure',
  'description': 'A reinforced elite leads the assault.',
  'focus': 'Stag Beetle',
  'count_bonus': 14,
  'health_bonus': 1.12,
  'speed_bonus': 1.0},
 {'wave': 31,
  'name': 'Chemical defense',
  'description': 'Bombardier beetles spray damaging chemicals.',
  'focus': 'Bombardier Beetle',
  'count_bonus': 0,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 32,
  'name': 'No safe distance',
  'description': 'Ranged attackers pressure clustered defenses.',
  'focus': 'Bombardier Beetle',
  'count_bonus': 8,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 33,
  'name': 'Air current',
  'description': 'Flying bugs approach at increased speed.',
  'focus': 'Dragonfly',
  'count_bonus': 12,
  'health_bonus': 1,
  'speed_bonus': 1.1},
 {'wave': 34,
  'name': 'Carapace wall',
  'description': 'Heavy armor advances down every route.',
  'focus': 'Ladybug',
  'count_bonus': 6,
  'health_bonus': 1.2,
  'speed_bonus': 1.0},
 {'wave': 35,
  'name': 'Swarmfront',
  'description': 'A very large combined swarm approaches.',
  'focus': 'Ant',
  'count_bonus': 30,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 36,
  'name': 'Breach team',
  'description': 'Termites and bombardiers attack your perimeter.',
  'focus': 'Termite',
  'count_bonus': 18,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 37,
  'name': 'Last flight',
  'description': 'A final dense airborne formation.',
  'focus': 'Wasp',
  'count_bonus': 20,
  'health_bonus': 1.1,
  'speed_bonus': 1.0},
 {'wave': 38,
  'name': 'Heavy footsteps',
  'description': 'Elite beetles escort the vanguard.',
  'focus': 'Stag Beetle',
  'count_bonus': 12,
  'health_bonus': 1.2,
  'speed_bonus': 1.0},
 {'wave': 39,
  'name': 'The gathering',
  'description': 'Every species joins the final approach.',
  'focus': 'Bombardier Beetle',
  'count_bonus': 25,
  'health_bonus': 1.0,
  'speed_bonus': 1.0},
 {'wave': 40,
  'name': 'Goliath',
  'description': 'The Goliath Beetle and its escorts arrive.',
  'focus': 'Goliath Beetle',
  'count_bonus': 20,
  'health_bonus': 1.0,
  'speed_bonus': 1.0}]

WAVE_PLANS = [WavePlan(**entry) for entry in WAVE_DEFINITIONS]

# FIELD ENGINEER GAMEPLAY -----------------------------------------------------
WIDTH, HEIGHT = 1440, 940
TILE = 46
NX, NY = 28, 22
LEFT, TOP = 18, 94
VIEW_W, VIEW_H = 1100, 750
PANEL_X = 1136
TITLE = 'PROJECT-SWARMFALL'

ROBOT_NAMES = (
    'Rifle Robot', 'Heavy Robot', 'Sniper Robot', 'Flame Tank',
    'Rocket Buggy', 'Artillery Robot', 'Cooling Robot', 'Piercing Walker',
    'Anti-Air Robot', 'Repair Robot', 'Support Robot', 'Shotgun Robot',
)
for spec, name in zip(ROBOTS, ROBOT_NAMES):
    spec['name'] = name
STRUCTURES[2]['name'] = 'Power Generator'
STRUCTURES[3]['name'] = 'Mining Station'
STRUCTURES[4]['name'] = 'Shield Generator'
STRUCTURES[0].update(price=22,metal=20,hp=520)
STRUCTURES[1].update(price=45,metal=26,hp=540)
STRUCTURES[3].update(price=145,metal=36,circuits=14,power=2)

DESCRIPTIONS = {
    'rifle': ('Reliable defender', 'Fires at one bug at a time. A useful first robot that can hit both ground and flying enemies.'),
    'heavy': ('Fast sustained fire', 'Rapid bullets wear down swarms. Place it where bugs stay within range for a long time.'),
    'sniper': ('Long-range specialist', 'Slow, powerful shots against tough bugs. Its upgrades can break armor and counter the boss.'),
    'flame': ('Close-range crowd damage', 'Sprays a cone of fire through groups of ground bugs. Cannot hit flying enemies.'),
    'rocket': ('Explosive support', 'Fires rockets that explode around a target. Can hit ground and flying bugs.'),
    'mortar': ('Long-range artillery', 'Lobs shells over your walls. Good against crowds, but cannot fire at very close targets or flying bugs.'),
    'cryo': ('Slows the swarm', 'Cooling bursts slow groups of bugs so your other robots can keep firing at them.'),
    'rail': ('Piercing heavy weapon', 'A straight shot passes through several bugs. Best when aimed along an enemy approach.'),
    'air': ('Protects the skies', 'Fast tracking weapons target flying insects. Its multirole upgrade unlocks ground attacks.'),
    'repair': ('Keeps the base working', 'Repairs nearby robots, structures and the core. This robot does not attack.'),
    'command': ('Helps nearby robots', 'Boosts the firing speed of nearby defenders and fires a small support weapon.'),
    'scatter': ('Close-range interception', 'Fires several pellets into nearby ground bugs. Works well at bends in your defenses.'),
    'wall': ('Redirects ground bugs', 'Stops ground bugs for a while. Uses one wall slot. Keep routes to the core open.'),
    'gate': ('A passage you control', 'Walk up and press E to open or close it. Open gates let your engineer and bugs through.'),
    'generator': ('Power and building reach', 'Adds 8 power and extends your connected construction area by 5 tiles. Keep generators linked to the core.'),
    'mine': ('Slow automatic mining', 'Collects small amounts every 10 seconds. Place near a deposit. Maximum two stations.'),
    'shield': ('Extra protection', 'Adds protective shields to nearby structures. Shields absorb damage before buildings lose health.'),
}
RESOURCE_NAMES = {'metal': 'Metal', 'circuits': 'Parts', 'crystal': 'Crystals'}
RESOURCE_COLORS = {'metal': '#c1d3db', 'circuits': '#e9bd80', 'crystal': '#c1a8ee'}


@dataclass(frozen=True)
class Level:
    name: str
    difficulty: str
    description: str
    terrain_style: str
    ground: str
    ground_dark: str
    accent: str
    health_factor: float
    core_health: int
    weather: str = 'pollen'


LEVELS = (
    Level('Sunlit Meadow', 'Easy', 'Two trails and plenty of room to build.',
          'meadow', '#a8c88c', '#91b476', '#dbeab6', .72, 5600),
    Level('Pine Clearing', 'Easy', 'Three trails. Trees break up the open ground.',
          'grove', '#96b987', '#7ca275', '#d1dfac', .8, 5400),
    Level('River Bend', 'Easy', 'Three trails with river crossings.',
          'river', '#a1c4a0', '#85ae91', '#b9e2cf', .9, 5200, 'water'),
    Level('Amber Quarry', 'Medium', 'Four trails through the quarry.',
          'quarry', '#d5b78c', '#c4a276', '#f3d6a2', 1., 4500, 'dust'),
    Level('Canyon Pass', 'Medium', 'Four trails and narrow gaps between rocks.',
          'canyon', '#d0a37d', '#b98b67', '#efc79b', 1.1, 4500, 'dust'),
    Level('Wetland Station', 'Medium', 'Five trails around pools of water.',
          'wetland', '#9bb9a2', '#7d9f8e', '#c1dfc8', 1.2, 4300, 'water'),
    Level('Ironworks', 'Hard', 'Five trails through the old factory.',
          'industrial', '#a9b4a7', '#8e9e93', '#dbd6b4', 1.35, 4000, 'dust'),
    Level('Storm Basin', 'Hard', 'Six trails, rain, and tougher bugs.',
          'storm', '#8caeaa', '#739591', '#c6dedb', 1.5, 3900, 'rain'),
    Level('Last Outpost', 'Hard', 'Seven trails and the strongest bugs.',
          'outpost', '#b8b18f', '#9f987b', '#eddbac', 1.7, 3800, 'dust'),
)


@dataclass
class Engineer:
    x: float = 14.5
    y: float = 13.6
    vx: float = 0.
    vy: float = 0.
    angle: float = -math.pi/2
    stride: float = 0.
    contact_cooldown: float = 0.
    stagger: float = 0.
    tool_time: float = 0.
    moving: bool = False
    working: bool = False
    tool_target: tuple | None = None

    @property
    def pos(self):
        return self.x, self.y


@dataclass
class WorkOrder:
    x: int
    y: int
    kind: int
    duration: float
    progress: float = 0.
    task: str = 'build'
    path: int = -1
    cost: int = 0
    paid_materials: dict = field(default_factory=dict)
    name: str = ''

    @property
    def pos(self):
        return self.x+.5, self.y+.5

    @property
    def fraction(self):
        return min(1., self.progress / max(.1, self.duration))


class Foundation(Building):
    @property
    def role(self):
        return 'wall'

    @property
    def spec(self):
        return dict(SPECS[self.kind], power=0)

    def stats(self):
        return {'hp': 220, 'range': 0}


TUTORIAL_STEPS = (
    ('Meet your engineer', 'Move with WASD. Walk a few steps around the core. You carry tools, not a weapon.'),
    ('Gather metal', 'Hold E by the Metal deposit. Release E to cool. Press Space in the green for a bonus. Collect 16 Metal.'),
    ('Choose a robot', 'Click Rifle Robot in the sidebar. The panel explains what it does and what it costs.'),
    ('Set a construction site', 'Face an empty tile near the core, then press F. The preview must be green and within reach.'),
    ('Build it yourself', 'Walk beside the construction frame and hold E until the robot is finished. Work pauses when you leave.'),
    ('Meet your robot', 'Walk up to your completed robot and press E. Upgrades are available only while you are beside it.'),
    ('Install an upgrade', 'Choose an affordable upgrade, then hold E beside the robot to install it. It takes time.'),
    ('Get ready for wave 1', 'The first wave starts automatically after the prep timer. Visit the core to check it or upgrade your drill.'),
    ('Protect the core', 'Let your robot fight. Bugs damage defenses and the core. Touching a bug knocks you back. Survive wave 1.'),
)


class FieldWorld(World):
    """Local, character-driven mining and construction over the combat engine."""
    def __init__(self, level_id=0, tutorial=False):
        self.level_id = level_id
        self.level = LEVELS[level_id]
        self.player = Engineer()
        self.orders = {}
        self.record = defaultdict(float)
        self.tutorial = tutorial
        self.tutorial_step = 0
        self.tutorial_complete = False
        self.selected_once = False
        self.opened_robot = False
        self.built_robots = 0
        self.upgrades_completed = 0
        self.mined_metal = 0
        self.walk_distance = 0
        self.mine_progress = 0
        self.mine_target = None
        self.feedback = []
        self.last_action = ''
        super().__init__(level_id)
        self.coremax = self.corehp = self.level.core_health
        self.money = 950
        self.materials = {'metal': 58, 'circuits': 22, 'crystal': 8}
        self.autoplay = True
        self.intermission = 60.
        self.break_duration=60.
        self.tool_heat=0.
        self.overheated=False
        self.drill_level=0
        self.strike_cooldown=0.
        self.precision_used=False
        self.mine_bonus=0
        self.barrier_limit=(10,8,6)[level_id//3]
        self.supply_pending=None
        self.clean_wave=True
        self.say('WASD to move • Hold E to mine or build • F places the selected blueprint nearby')

    def mining_duration(self,resource,key=None):
        base={'metal':1.5,'circuits':2.1,'crystal':2.7}[resource]
        hardness=1+.12*(self.level_id//3)
        if key is not None:
            hardness+=.08*((key[0]*3+key[1])%3)
        return base*hardness/(1+.2*self.drill_level)

    def barrier_count(self):
        return sum(SPECS[b.kind]['role'] in ('wall','gate') for b in self.buildings.values())

    def core_routes_open(self,extra=None):
        blocked=set(self.terrain)
        for key,b in self.buildings.items():
            if not(b.role=='gate' and b.opened):blocked.add(key)
        if extra is not None:blocked.add(extra)
        exits=[p for p in World.neighbors(self.core) if p not in blocked]
        if len(exits)<2:return False
        reached={self.core};queue=deque([self.core])
        while queue:
            p=queue.popleft()
            for n in self.neighbors(p):
                if n not in blocked and n not in reached:
                    reached.add(n);queue.append(n)
        return all(route[-1] in reached for route in self.approach_routes)

    def precision_strike(self):
        context=self.local_context()
        if not context or context[0]!='deposit' or self.overheated or self.strike_cooldown>0:
            return False
        resource,_=self.deposits[context[1]]
        duration=self.mining_duration(resource,context[1])
        fraction=self.mine_progress/duration
        self.strike_cooldown=.4
        if .52<=fraction<=.78 and not self.precision_used:
            self.precision_used=True
            self.mine_bonus=2 if resource=='metal' else 1
            self.mine_progress+=duration*.22
            self.tool_heat=max(0,self.tool_heat-.18)
            self.fx('text',self.player.pos,'#f6df8b',.65,text='Good hit!')
            return True
        self.tool_heat=min(1,self.tool_heat+.14)
        self.mine_progress=max(0,self.mine_progress-duration*.12)
        self.say('Watch the marker. Press Space in the green section.')
        return False

    def incoming_spawns(self):
        initial=1 if self.level_id<3 else 2 if self.level_id<6 else 3
        count=min(len(self.spawns),initial+max(0,self.wave-1)//5)
        return self.spawns[:count]

    @staticmethod
    def break_after(wave):
        return 60. if wave%5==0 else 15.

    def claim_supply(self,choice):
        if self.supply_pending is None or self.active or distance(self.player.pos,self.corepos)>1.95:
            return False
        if choice=='materials':
            self.materials['metal']+=48;self.materials['circuits']+=16;self.materials['crystal']+=3
            message='+48 Metal, +16 Parts, +3 Crystals'
        elif choice=='repair':
            self.corehp=min(self.coremax,self.corehp+900)
            for b in self.buildings.values():b.hp=min(b.stats()['hp'],b.hp+b.stats()['hp']*.35)
            message='Core +900 health; buildings repaired by 35%'
        elif choice=='money':
            amount=250+self.wave*10;self.money+=amount;message=f'+${amount}'
        else:return False
        self.supply_pending=None
        self.notice('Supplies collected',message,'#f4d78f')
        return True

    def buy_drill(self):
        if self.drill_level>=3 or distance(self.player.pos,self.corepos)>1.95:return False
        rank=self.drill_level+1
        money,metal,parts=220*rank,20*rank,8*rank
        if self.money<money or self.materials['metal']<metal or self.materials['circuits']<parts:
            self.say('Not enough supplies for the drill upgrade.')
            return False
        self.money-=money;self.materials['metal']-=metal;self.materials['circuits']-=parts
        self.drill_level+=1
        self.notice('Drill upgraded',f'Level {self.drill_level}: faster mining and cooling.','#b6e7d5')
        return True

    def generate_map(self):
        style = self.level.terrain_style
        for y in range(1, NY-1):
            for x in range(1, NX-1):
                p = (x, y)
                blocked = False
                if style == 'meadow':
                    blocked = (x-7)**2+(y-5)**2<5 or (x-22)**2+(y-17)**2<5
                elif style == 'grove':
                    blocked = any((x-a)**2+(y-b)**2<5 for a,b in ((6,6),(21,5),(7,17),(23,16)))
                elif style == 'river':
                    blocked = x in (7,8) and y not in (4,5,10,11,16,17)
                elif style == 'quarry':
                    blocked = (5<=x<=8 and 4<=y<=6) or (19<=x<=22 and 15<=y<=18)
                elif style == 'canyon':
                    blocked = x in (7,8,20,21) and y not in (4,5,10,11,16,17)
                elif style == 'wetland':
                    blocked = any((x-a)**2+(y-b)**2<7 for a,b in ((6,6),(21,6),(6,17),(22,17)))
                elif style == 'industrial':
                    blocked = ((4<=x<=8 or 20<=x<=24) and y in (5,6,15,16)) or (x==19 and 2<=y<=5)
                elif style == 'storm':
                    blocked = ((x-6)**2+(y-8)**2<10) or ((x-22)**2+(y-15)**2<10)
                else:
                    blocked = ((x in (6,21) and y not in (5,6,11,12,17)) or
                               (y in (4,18) and 10<=x<=17 and x not in (13,14)))
                if blocked and distance(p,self.core)>4.4:
                    self.terrain.add(p)
        deposits = (
            (12,14,'metal'), (17,13,'circuits'), (13,8,'crystal'),
            (4,11,'metal'), (23,10,'metal'), (15,18,'circuits'),
            (11,3,'metal'), (24,3,'crystal'), (3,19,'circuits'),
        )
        for x,y,resource in deposits:
            self.terrain.discard((x,y))
            for q in self.neighbors((x,y)):
                self.terrain.discard(q)
            self.deposits[x,y] = [resource, 700 if resource=='metal' else 400]
        for p in self.spawns:
            self.terrain.discard(p)
        # Guarantee space to leave and circle the core.
        for x in range(11,18):
            for y in range(9,15):
                self.terrain.discard((x,y))

        self.generate_approaches()

    def notice(self,title,body='',color='#b8e2c1'):
        self.feedback.append({'title': title, 'body': body, 'color': color, 'age':0., 'life':4.})
        self.feedback = self.feedback[-3:]

    def generate_approaches(self):
        self.core_build_radius=7.
        v=self.level_id%3
        plans=(
            [(0,4),(3,4),(3,7+v),(6,7+v),(7,10),(9,10)],
            [(27,17),(24,17),(24,14-v),(22,14-v),(20,12)],
            [(13,0),(13,2),(16+self.level_id%2,2),(16+self.level_id%2,5),(15,6)],
            [(13,21),(13,20),(10+v,20),(10+v,18),(12,17)],
        )
        plans=list(plans)+[
            [(0,18),(3,18),(3,15),(6,15),(9,14)],
            [(25,0),(25,3),(23,3),(23,7),(19,7)],
            [(26,21),(26,19),(23,19),(23,16),(19,15)],
        ]
        plans=plans[:(2,3,3,4,4,5,5,6,7)[self.level_id]]
        self.spawns=[route[0] for route in plans]
        self.approach_routes=[]
        self.path_tiles=set()
        for number,waypoints in enumerate(plans):
            cells=[waypoints[0]]
            for endpoint in waypoints[1:]:
                x,y=cells[-1]
                while x!=endpoint[0]:
                    x+=1 if endpoint[0]>x else -1
                    cells.append((x,y))
                while y!=endpoint[1]:
                    y+=1 if endpoint[1]>y else -1
                    cells.append((x,y))
            trimmed=[]
            for cell in cells:
                trimmed.append(cell)
                if self.in_core_area((cell[0]+.5,cell[1]+.5)):
                    break
            self.approach_routes.append(trimmed)
            for cell in trimmed:
                self.terrain.discard(cell)
                if not self.in_core_area((cell[0]+.5,cell[1]+.5)):
                    self.path_tiles.add(cell)
            # Ensure resources never sit on an enemy trail.
            for cell in list(self.deposits):
                if cell in self.path_tiles:
                    data=self.deposits.pop(cell)
                    candidates=[(x,y) for x in range(2,NX-2) for y in range(2,NY-2)
                                if (x,y) not in self.terrain and (x,y) not in self.path_tiles
                                and (x,y) not in self.deposits and (x,y)!=self.core]
                    if candidates:
                        chosen=min(candidates,key=lambda p:distance(p,cell))
                        self.deposits[chosen]=data

        self.route_gates={route[-1] for route in self.approach_routes}
        self.reserved_trails=self.path_tiles|self.route_gates

    def neighbors(self,p):
        candidates=World.neighbors(p)
        if not hasattr(self,'reserved_trails'):
            return candidates
        return [cell for cell in candidates if cell in self.reserved_trails
                or self.in_core_area((cell[0]+.5,cell[1]+.5))]

    def in_core_area(self,pos):
        return distance(pos,self.corepos)<=getattr(self,'core_build_radius',7.)

    def approach_destination(self,e):
        if getattr(e,'route_entered',False):
            return None
        if self.in_core_area(e.pos):
            e.route_entered=True
            return None
        if not hasattr(e,'route_number'):
            candidates=[(distance(e.pos,(cell[0]+.5,cell[1]+.5)),route_index,index)
                        for route_index,route in enumerate(self.approach_routes)
                        for index,cell in enumerate(route)]
            _,e.route_number,e.route_index=min(candidates)
        route=self.approach_routes[e.route_number]
        index=e.route_index
        target=(route[index][0]+.5,route[index][1]+.5)
        if distance(e.pos,target)<.035 and index<len(route)-1:
            e.route_index+=1
            cell=route[e.route_index]
            target=(cell[0]+.5,cell[1]+.5)
        return target

    def can_place(self,x,y,kind):
        if (x,y) in getattr(self,'reserved_trails',set()):
            return 'Enemy trail: build beside it, not on it.'
        role=SPECS[kind]['role']
        if role in ('wall','gate'):
            if distance((x+.5,y+.5),self.corepos)<2.5:
                return 'Keep walls outside the small circle around the core.'
            if self.barrier_count()>=self.barrier_limit:
                return f'Wall limit reached ({self.barrier_limit}). Sell one to move it.'
        if role=='mine' and sum(SPECS[b.kind]['role']=='mine' for b in self.buildings.values())>=2:
            return 'You can build two mining stations. Mine other deposits by hand.'
        error=super().can_place(x,y,kind)
        if error:return error
        if not self.core_routes_open((x,y)):
            return 'Keep routes into the core open. Use walls as cover, not a sealed ring.'
        return ''


    def walkable(self,x,y,radius=.24):
        if x<radius or y<radius or x>NX-radius or y>NY-radius:
            return False
        for dx,dy in ((-radius,-radius),(radius,-radius),(-radius,radius),(radius,radius),(0,0)):
            p = (int(x+dx),int(y+dy))
            b = self.buildings.get(p)
            if p in self.terrain or p==self.core:
                return False
            if b and not(b.role=='gate' and b.opened):
                return False
        return True

    def move_player(self,dt,axis,sprint=False):
        p = self.player
        p.contact_cooldown = max(0,p.contact_cooldown-dt)
        p.stagger = max(0,p.stagger-dt)
        p.working = False
        p.tool_target = None
        dx,dy = axis
        length = math.hypot(dx,dy)
        speed = 4.1 if sprint else 3.15
        if length:
            dx,dy = dx/length,dy/length
            p.angle = math.atan2(dy,dx)
        if p.stagger:
            p.vx *= max(0,1-dt*5)
            p.vy *= max(0,1-dt*5)
        else:
            target_x,target_y = dx*speed,dy*speed
            response = min(1,dt*22)
            p.vx += (target_x-p.vx)*response
            p.vy += (target_y-p.vy)*response
        old = p.pos
        nx = p.x+p.vx*dt
        if self.walkable(nx,p.y):
            p.x = nx
        else:
            p.vx = 0
        ny = p.y+p.vy*dt
        if self.walkable(p.x,ny):
            p.y = ny
        else:
            p.vy = 0
        traveled = distance(old,p.pos)
        self.walk_distance += traveled
        p.stride += traveled*9
        p.moving = traveled>.0005
        # The engineer never inflicts contact damage or blocks enemy movement.
        if not p.contact_cooldown:
            for e in self.enemies:
                if e.dead:
                    continue
                radius = .9 if e.name=='Goliath Beetle' else .57
                if distance(p.pos,e.pos)<radius:
                    vx,vy = p.x-e.x,p.y-e.y
                    length = math.hypot(vx,vy)
                    if length<.01:
                        vx,vy,length = -math.cos(e.angle),-math.sin(e.angle),1
                    p.vx,p.vy = vx/length*5.4,vy/length*5.4
                    p.stagger = .32
                    p.contact_cooldown = .85
                    self.fx('ring',p.pos,'#ffe1a1',.35,.6)
                    self.notice('Knocked back','Your tools cannot hurt bugs. Let the robots defend you.','#edc28b')
                    break

    def local_context(self):
        pos = self.player.pos
        choices = []
        for key,order in self.orders.items():
            d = distance(pos,order.pos)
            if d<=1.72:
                choices.append((d-.45,'order',key))
        for key,(resource,amount) in self.deposits.items():
            d = distance(pos,(key[0]+.5,key[1]+.5))
            if d<=1.62 and amount>0:
                choices.append((d,'deposit',key))
        for key,b in self.buildings.items():
            if isinstance(b,Foundation) or key in self.orders:
                continue
            d = distance(pos,b.pos)
            if d<=1.7:
                choices.append((d+.05,'robot',key))
        d = distance(pos,self.corepos)
        if d<=1.9:
            choices.append((d+.1,'core',self.core))
        if not choices:
            return None
        _,kind,key = min(choices,key=lambda item:item[0])
        return kind,key

    def blueprint_tile(self):
        p = self.player
        return int(p.x+math.cos(p.angle)*1.35),int(p.y+math.sin(p.angle)*1.35)

    def site_error(self,x,y,kind):
        if distance(self.player.pos,(x+.5,y+.5))>2.05:
            return 'Walk closer to the construction site.'
        if distance(self.player.pos,(x+.5,y+.5))<.78:
            return 'Leave room for yourself. Face an adjacent empty tile.'
        if (x,y) in self.orders:
            return 'There is already work here.'
        return self.can_place(x,y,kind)

    def start_construction(self,kind):
        x,y = self.blueprint_tile()
        error = self.site_error(x,y,kind)
        if error:
            self.say(error)
            return False
        spec = SPECS[kind]
        self.money -= spec['price']
        paid = {}
        for resource in self.materials:
            amount = spec.get(resource,0)
            self.materials[resource] -= amount
            paid[resource] = amount
        duration = 2.5 if spec['role']=='wall' else 3 if spec['role']=='gate' else 5 if kind<12 else 4
        self.buildings[x,y] = Foundation(x,y,kind)
        self.orders[x,y] = WorkOrder(x,y,kind,duration,cost=spec['price'],paid_materials=paid,name=spec['name'])
        self.repath()
        self.record['sites'] += 1
        self.notice('Construction site ready','Stand beside it and hold E to build. Leaving pauses the work.')
        return True

    def request_upgrade(self,key,path):
        b = self.buildings.get(key)
        if not b or isinstance(b,Foundation) or b.kind>=12 or key in self.orders:
            return False
        if distance(self.player.pos,b.pos)>1.75:
            self.say('Walk beside this robot to upgrade it.')
            return False
        if b.upgrade_locked(path):
            self.say('That path is locked. Only tier 1 of the other path is allowed.')
            return False
        upgrade = b.next_upgrade(path)
        if not upgrade or self.money<upgrade['price']:
            self.say('Not enough dollars for that upgrade.')
            return False
        self.money -= upgrade['price']
        self.orders[key] = WorkOrder(b.x,b.y,b.kind,3+b.paths[path]*1.5,task='upgrade',path=path,
                                    cost=upgrade['price'],name=upgrade['name'])
        self.notice('Upgrade prepared','Hold E beside this robot to install it. The robot keeps defending.')
        return True

    def request_repair(self,key):
        b = self.buildings.get(key)
        if not b or key in self.orders or distance(self.player.pos,b.pos)>1.75:
            return False
        missing = b.stats()['hp']-b.hp
        if missing<1:
            self.say('This structure is already fully repaired.')
            return False
        cost = math.ceil(missing*.08)
        metal = math.ceil(missing*.02)
        if self.money<cost or self.materials['metal']<metal:
            self.say('Repairs need more dollars or Metal.')
            return False
        self.money -= cost
        self.materials['metal'] -= metal
        self.orders[key] = WorkOrder(b.x,b.y,b.kind,2.5,task='repair',cost=cost,name='Repair')
        return True

    def finish_order(self,key):
        order = self.orders.pop(key)
        b = self.buildings.get(key)
        if not b:
            return
        if order.task=='build':
            finished = Building(order.x,order.y,order.kind)
            finished.hp = finished.stats()['hp']*max(.3,min(1,b.hp/220))
            self.buildings[key] = finished
            self.built_robots += int(order.kind<12)
            self.repath()
            self.notice(order.name+' online','Walk up and press E to inspect, upgrade or repair.','#aee5bd')
        elif order.task=='upgrade':
            old_max = b.stats()['hp']
            b.paths[order.path] += 1
            b.invested += order.cost
            b.hp += b.stats()['hp']-old_max
            self.upgrades_completed += 1
            self.notice(order.name+' installed','Your robot is ready.','#edd28d')
        else:
            b.hp = b.stats()['hp']
            self.notice('Repairs complete',b.spec['name'])
        self.fx('upgrade',order.pos,'#f4d393',.9,1.2)

    def use_tool(self,dt,holding):
        p=self.player
        self.strike_cooldown=max(0,self.strike_cooldown-dt)
        context=self.local_context()
        mining=holding and context and context[0]=='deposit' and not p.stagger
        if self.overheated:
            self.tool_heat=max(0,self.tool_heat-dt*(.16 if mining else .52))
            if self.tool_heat<=.24:
                self.overheated=False
                self.notice('Tool cooled','Ready to mine again.','#b6e3c3')
            mining=False
        elif not mining:
            self.tool_heat=max(0,self.tool_heat-dt*(.42+.06*self.drill_level))
        if not holding or not context or p.stagger:
            return
        kind,key=context
        if kind=='order':
            order=self.orders.get(key)
            if order is None:return
            p.working=True;p.tool_target=order.pos;p.tool_time+=dt
            order.progress+=dt
            if int(order.progress*7)!=int((order.progress-dt)*7):
                self.fx('hit',order.pos,'#f5d493',.2,.12)
            if order.progress>=order.duration:self.finish_order(key)
        elif kind=='deposit' and mining:
            if self.mine_target!=key:
                self.mine_target=key;self.mine_progress=0;self.precision_used=False;self.mine_bonus=0
            resource,remaining=self.deposits[key]
            duration=self.mining_duration(resource,key)
            p.working=True;p.tool_target=(key[0]+.5,key[1]+.5);p.tool_time+=dt
            self.mine_progress+=dt
            self.tool_heat=min(1,self.tool_heat+dt*.18)
            if self.mine_progress>=duration:
                self.mine_progress-=duration
                amount=min(remaining,({'metal':4,'circuits':2,'crystal':1}[resource])+self.mine_bonus)
                self.deposits[key][1]-=amount
                self.materials[resource]+=amount
                if resource=='metal':self.mined_metal+=amount
                self.mine_bonus=0;self.precision_used=False
                self.fx('text',p.tool_target,RESOURCE_COLORS[resource],.7,text=f'+{amount} {RESOURCE_NAMES[resource]}')
                self.fx('hit',p.tool_target,RESOURCE_COLORS[resource],.25,.2)
            if self.tool_heat>=1:
                self.overheated=True
                self.notice('Tool overheated','Release E to cool it faster.','#f2b589')

        # No branch attacks insects. E is exclusively a mining / construction tool.

    def choose_target(self,b,candidates):
        priority=b.stats().get('priority',False)
        armored=('Beetle','Stag Beetle','Ladybug','Goliath Beetle')
        return min(candidates,key=lambda e:(0 if not priority or e.name in armored else 1,
                                           distance(e.pos,self.corepos)))

    def start_wave(self,automatic=False):
        if self.intermission>0 or self.active or self.wave>=40 or self.outcome:
            return False
        super().start_wave()
        self.clean_wave=True
        self.supply_pending=None
        plan=WAVE_PLANS[self.wave-1]
        names=list(self.queue)
        if plan.focus!='Goliath Beetle':
            for i in range(min(8,len(names)//4)):names[i*4]=plan.focus
        self.queue=deque(names)
        self.notice(f'Wave {self.wave}',plan.description,'#f3c18e')
        return True


    def damage(self,e,amount,source=None,stats=None):
        old = e.hp
        super().damage(e,amount,source,stats)
        if source:
            self.record['robot_damage'] += max(0,min(old,old-e.hp))

    def tick_tutorial(self):
        if not self.tutorial or self.tutorial_complete:
            return
        checks = (
            self.walk_distance>=2.3,
            self.mined_metal>=16,
            self.selected_once,
            self.record['sites']>=1,
            self.built_robots>=1,
            self.opened_robot,
            self.upgrades_completed>=1,
            self.wave>=1,
            self.wave>=1 and not self.active,
        )
        if checks[self.tutorial_step]:
            self.tutorial_step += 1
            self.fx('upgrade',self.player.pos,'#b4e7bd',.6,.75)
            if self.tutorial_step>=len(TUTORIAL_STEPS):
                self.tutorial_complete = True
                self.tutorial = False
                self.autoplay = True
                self.notice('Tutorial complete','You can continue this level or return to the nine-level menu.','#efd596')
            else:
                title,description = TUTORIAL_STEPS[self.tutorial_step]
                self.notice(title,description)

    def bug_attack(self,e,target):
        super().bug_attack(e,target)
        if not isinstance(target,Building):self.clean_wave=False
        e.attack_clock=.62 if e.role in ('slash','crush','boss','ram') else .42
        e.attack_length=e.attack_clock

    def move_enemies(self,dt):
        before={id(e):e.pos for e in self.enemies}
        super().move_enemies(dt)
        for e in self.enemies:
            previous=before.get(id(e),e.pos)
            traveled=distance(previous,e.pos)
            e.walk_phase=getattr(e,'walk_phase',0)+min(.3,traveled)*11
            target=1. if traveled>.0005 and not e.stun else 0.
            e.walk_blend=getattr(e,'walk_blend',0)+(target-getattr(e,'walk_blend',0))*min(1,dt*16)
            e.attack_clock=max(0,getattr(e,'attack_clock',0)-dt)
            if traveled>.8:
                e.leap_clock=.5
            else:
                e.leap_clock=max(0,getattr(e,'leap_clock',0)-dt)

    def operate_buildings(self,dt):
        previous={id(b):b.cooldown for b in self.buildings.values()}
        super().operate_buildings(dt)
        for b in self.buildings.values():
            b.recoil_clock=max(0,getattr(b,'recoil_clock',0)-dt)
            if b.animation>0 and b.cooldown>previous.get(id(b),b.cooldown)+.01:
                b.recoil_clock=.34
            age=.34-b.recoil_clock
            strength=9 if b.role in ('sniper','rail','mortar','scatter') else 6
            b.visual_recoil=strength*math.exp(-age*13)*math.sin(min(1,age/.045)*math.pi/2) if b.recoil_clock else 0.

    def update_field(self,dt,axis=(0,0),holding=False,sprint=False):
        if self.outcome:return
        self.move_player(dt,axis,sprint)
        self.use_tool(dt,holding)
        old_ids={id(e) for e in self.enemies}
        was_active=self.active
        self.autoplay=False
        super().update(dt)
        self.autoplay=True
        for e in self.enemies:
            if id(e) not in old_ids:
                e.hp*=self.level.health_factor;e.maxhp*=self.level.health_factor
        for key in list(self.orders):
            if key not in self.buildings:
                self.orders.pop(key)
                self.notice('Site destroyed','Keep unfinished buildings behind your defenders.','#e7a58d')
        if was_active and not self.active:
            if self.outcome:
                self.intermission=0
            else:
                self.intermission=self.break_after(self.wave)
                self.break_duration=self.intermission
                if self.clean_wave:
                    bonus=40+self.wave*3;self.money+=bonus
                    self.notice('Core untouched!',f'+${bonus} bonus','#f6da8e')
                if self.wave%5==0:
                    self.supply_pending=self.wave
                    self.notice('Supply break','One minute. Visit the core and choose a supply pack.','#c6e3b3')
                else:
                    self.notice('Wave cleared','15 seconds to mine, build and repair.','#b8e3bb')
        elif not self.active:
            training_pause=self.tutorial and self.tutorial_step<7
            if not training_pause:
                self.intermission=max(0,self.intermission-dt)
                if self.intermission<.000001:self.intermission=0
                if self.intermission<=0:self.start_wave(automatic=True)
        self.tick_tutorial()
        for notice in self.feedback:notice['age']+=dt;notice['life']-=dt
        self.feedback=[n for n in self.feedback if n['life']>0]
        self.record['time']+=dt



class FollowCamera:
    def __init__(self):
        self.x,self.y = 14.5,12.5
        self.zoom = 1.
        self.target_zoom = 1.

    def follow(self,pos,dt):
        self.zoom += (self.target_zoom-self.zoom)*min(1,dt*12)
        self.x += (pos[0]-self.x)*min(1,dt*8)
        self.y += (pos[1]-self.y)*min(1,dt*8)
        half_w = VIEW_W/(2*TILE*self.zoom)
        half_h = VIEW_H/(2*TILE*self.zoom)
        self.x = NX/2 if half_w>=NX/2 else max(half_w,min(NX-half_w,self.x))
        self.y = NY/2 if half_h>=NY/2 else max(half_h,min(NY-half_h,self.y))

    def project(self,x,y):
        return x,y


class ArtBase:
    def draw_effect(self, f):
        progress = 1 - f['ttl'] / f['life']
        x, y = self.point(f['pos'])
        c = f['color']
        size = f['size']
        kind = f['kind']
        end = self.point(f['end']) if f['end'] else (x, y)
        if kind in ('beam', 'rail', 'acid'):
            self.line([(x, y), end], c, 5 * (1 - progress) + 1 if kind == 'rail' else 2)
            if kind == 'rail':
                self.line([(x, y), end], '#ecfcff', 2 * (1 - progress) + 0.5)
        elif kind == 'flame':
            a = math.atan2(end[1] - y, end[0] - x)
            for i in range(11):
                t = (i + progress) / 11
                r = (5 + 12 * t) * (1 - progress * 0.4)
                offset = math.sin(i * 8) * 0.3
                px = x + math.cos(a + offset) * size * TILE * t
                py = y + math.sin(a + offset) * size * TILE * t
                self.oval(px - r / 2, py - r / 2, r, r, '#ffd08c' if i % 2 else '#f1a36d')
        elif kind in ('ring', 'shockwave', 'frost', 'build', 'upgrade', 'repair', 'explosion', 'defeat', 'hit', 'dust'):
            radius = max(2, (0.12 + progress * 0.88) * size * TILE)
            if kind in ('explosion', 'hit') and progress < 0.3:
                self.oval(x - radius / 2, y - radius / 2, radius, radius, '#fff0bf')
            self.oval(x - radius, y - radius, 2 * radius, 2 * radius, '', c, max(0.5, 3 * (1 - progress)))
            count = 12 if kind in ('explosion', 'upgrade', 'defeat') else 6
            for i in range(count):
                a = i * math.tau / count + progress * 0.8
                px = x + math.cos(a) * radius
                py = y + math.sin(a) * radius
                if kind == 'repair':
                    self.line([(px - 3, py), (px + 3, py)], c, 2)
                    self.line([(px, py - 3), (px, py + 3)], c, 2)
                elif kind == 'frost':
                    self.line([(px - 3, py - 3), (px + 3, py + 3)], c, 2)
                else:
                    r = max(1, 3 * (1 - progress))
                    self.oval(px - r, py - r, r * 2, r * 2, c)
        elif kind == 'text':
            self.text(x, y - progress * 32, f['text'], 12, c, True, anchor='center')
        elif kind == 'slash':
            self.line([(x - 12, y + 9), (x + 11, y - 10)], c, 3 * (1 - progress) + 1)
            self.line([(x - 5, y + 12), (x + 15, y - 7)], c, 2)
        elif kind == 'leap':
            for i in range(5):
                t = i / 4
                px = x + (end[0] - x) * t
                py = y + (end[1] - y) * t - math.sin(t * math.pi) * 24
                self.oval(px - 2, py - 2, 4, 4, c)
        elif kind == 'muzzle':
            a = math.atan2(end[1] - y, end[0] - x)
            px = x + math.cos(a) * 19
            py = y + math.sin(a) * 19
            self.polygon([(px - 5, py), (px, py - 5), (px + 5, py), (px, py + 5)], c)


def plain_upgrade(upgrade):
    effects=upgrade['effects']
    pieces=[]
    for key,value in effects.items():
        if key=='damage':pieces.append(f'{round((value-1)*100)}% more damage')
        elif key=='range':pieces.append(f'{round((value-1)*100)}% farther reach')
        elif key=='rate':pieces.append(f'fires {round((value-1)*100)}% faster')
        elif key=='burst':pieces.append(f'{value} shots each time it fires')
        elif key=='pierce_armor':pieces.append('bug shells no longer reduce its damage')
        elif key=='mark':pieces.append('hit bugs take 20% more damage from all robots')
        elif key=='boss_bonus':pieces.append(f'{value}× damage to big beetles and the boss')
        elif key=='splash':pieces.append('hits a wider area')
        elif key=='slow':pieces.append(f'hit bugs move {round((1-value)*100)}% slower')
        elif key=='stun':pieces.append(f'freezes bugs in place for {value:g}s')
        elif key=='burn':pieces.append(f'burning deals {value} damage each second')
        elif key=='hp':pieces.append(f'{round((value-1)*100)}% more building health')
        elif key=='guard':pieces.append('nearby buildings take 30% less damage')
        elif key=='heal':pieces.append(f'repairs {round((value-1)*100)}% more health')
        elif key=='heal_targets':pieces.append(f'repairs {value} neighbors at once')
        elif key=='core_heal':pieces.append(f'repairs the core {value:g}× as quickly')
        elif key=='shield':pieces.append('gives nearby allies damage-absorbing shields')
        elif key=='aura_rate':pieces.append('nearby robots fire faster')
        elif key=='aura_range':pieces.append('nearby robots reach 20% farther')
        elif key=='aura_damage':pieces.append('nearby robots deal 35% more damage')
        elif key=='bounty':pieces.append('nearby kills earn 40% more dollars')
        elif key=='support_rate':pieces.append('nearby robots fire 20% faster')
        elif key=='ground':pieces.append('can now shoot ground bugs too')
        elif key=='air_bonus':pieces.append('extra damage against flying bugs')
        elif key=='chain':pieces.append(f'shots bounce to {value} more bugs')
        elif key=='pellets':pieces.append(f'fires {value} pellets per shot')
        elif key=='death_blast':pieces.append('defeated bugs explode and damage neighbors')
        elif key=='explosion':pieces.append('hits explode and damage nearby bugs')
        elif key=='cluster':pieces.append(f'rockets split into {value} smaller blasts')
        elif key=='hazard':pieces.append('leaves a damaging patch on the ground')
        elif key=='beam_width':pieces.append('a wider beam hits more bugs in a line')
        elif key=='cone':pieces.append('a wider spread catches more bugs')
        elif key=='priority':pieces.append('aims at armored bugs first')
    text='; '.join(pieces) if pieces else upgrade['description']
    return text[0].upper()+text[1:]+'.'


def upgrade_comparison(building,path):
    before=building.stats()
    preview=Building(building.x,building.y,building.kind)
    preview.paths=list(building.paths)
    preview.paths[path]+=1
    after=preview.stats()
    pairs=[]
    if before['damage']!=after['damage']:pairs.append(f'Damage {before["damage"]:g} to {after["damage"]:g}')
    if before['range']!=after['range']:pairs.append(f'Reach {before["range"]:.1f} to {after["range"]:.1f} tiles')
    if before['rate']!=after['rate']:
        cooldown=building.spec['cooldown']
        pairs.append(f'Shot delay {cooldown/before["rate"]:.2f}s to {cooldown/after["rate"]:.2f}s')
    if before['hp']!=after['hp']:pairs.append(f'Health {before["hp"]:g} to {after["hp"]:g}')
    if before['burst']!=after['burst']:pairs.append(f'Shots {before["burst"]} to {after["burst"]}')
    if before['heal']!=after['heal']:pairs.append(f'Repair {40*before["heal"]:g} to {40*after["heal"]:g} health')
    return '  ·  '.join(pairs[:2]) or 'Adds the ability described above'


class EngineerGame(ArtBase):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(TITLE)
        self.root.geometry('1440x940')
        self.root.minsize(1100,720)
        self.root.configure(bg='#102839')
        widget = tk.Canvas(self.root,bg='#102839',highlightthickness=0)
        widget.pack(fill='both',expand=True)
        self.scale = 1.
        self.offset = (0.,0.)
        self.camera = FollowCamera()
        self.canvas = CanvasPool(widget,self)
        self.world = FieldWorld()
        self.keys = set()
        self.pending_releases = {}
        self.state = 'title'
        self.paused = False
        self.panel = None
        self.blueprint = None
        self.category = 'robots'
        self.blueprint_page=0
        self.buttons = []
        self.hover = (-1,-1)
        self.quality = True
        self.real_time = 0.
        self.last = time.perf_counter()
        self.accumulator = 0.
        self.transition = None
        self.selected_level = 0
        self.closed = False
        self.hover_values = {}
        self.completed = set()
        self.fullscreen = False
        self.decor = []
        self.reset_decor()
        widget.bind('<Motion>',self.motion)
        widget.bind('<Button-1>',self.click)
        widget.bind('<Button-3>',self.cancel_blueprint)
        widget.bind('<MouseWheel>',self.wheel)
        widget.bind('<Button-4>',lambda e:self.change_zoom(.1))
        widget.bind('<Button-5>',lambda e:self.change_zoom(-.1))
        self.root.bind('<KeyPress>',self.key_down)
        self.root.bind('<KeyRelease>',self.key_up)
        self.root.bind('<FocusOut>',self.focus_out)
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.frame()

    def close(self):
        self.closed = True
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def reset_decor(self):
        rng = random.Random(910+self.world.level_id*37)
        self.decor = [(rng.random()*NX,rng.random()*NY,rng.random(),rng.random()*math.tau) for _ in range(310)]

    def logical(self,event):
        return (event.x-self.offset[0])/self.scale,(event.y-self.offset[1])/self.scale

    def motion(self,event):
        self.hover = self.logical(event)

    def point(self,pos):
        unit = TILE*self.camera.zoom
        x = LEFT+VIEW_W/2+(pos[0]-self.camera.x)*unit
        y = TOP+VIEW_H/2+(pos[1]-self.camera.y)*unit
        return x,y

    def visible(self,pos,padding=1.4):
        x,y = self.point(pos)
        pad = padding*TILE*self.camera.zoom
        return LEFT-pad<=x<=LEFT+VIEW_W+pad and TOP-pad<=y<=TOP+VIEW_H+pad

    def rect(self,x,y,w,h,fill,outline='',width=1):
        return self.canvas.create_rectangle(x,y,x+w,y+h,fill=fill,outline=outline,width=width*self.scale)

    def oval(self,x,y,w,h,fill,outline='',width=1):
        return self.canvas.create_oval(x,y,x+w,y+h,fill=fill,outline=outline,width=width*self.scale)

    def line(self,points,color,width=1,**options):
        return self.canvas.create_line(*[v for p in points for v in p],fill=color,width=width*self.scale,**options)

    def polygon(self,points,fill,outline='',width=1,smooth=False):
        return self.canvas.create_polygon(*[v for p in points for v in p],fill=fill,outline=outline,
                                          width=width*self.scale,smooth=smooth,splinesteps=8)

    def roundrect(self,x,y,w,h,fill,outline='',r=10,width=1):
        r = min(r,w/2,h/2)
        points = [(x+r,y),(x+w-r,y),(x+w,y),(x+w,y+r),(x+w,y+h-r),(x+w,y+h),
                  (x+w-r,y+h),(x+r,y+h),(x,y+h),(x,y+h-r),(x,y+r),(x,y)]
        return self.polygon(points,fill,outline,width,True)

    def gradient(self,x,y,w,h,top,bottom,steps=18):
        for i in range(steps):
            self.rect(x,y+h*i/steps,w,h/steps+1,tint(top,bottom,i/max(1,steps-1)))

    def text(self,x,y,message,size=12,color='#ebf2e9',bold=False,anchor='nw',width=None):
        options = {'text':str(message),'fill':color,'font':('Helvetica',max(8,round(size*self.scale)),'bold' if bold else 'normal'),'anchor':anchor}
        if width:
            options['width'] = width*self.scale
        return self.canvas.create_text(x,y,**options)

    def button(self,x,y,w,h,label,action,enabled=True,accent=None,size=11):
        hot=enabled and x<=self.hover[0]<=x+w and y<=self.hover[1]<=y+h
        key=str(action)
        value=self.hover_values.get(key,0)
        value+=((1 if hot else 0)-value)*.25
        self.hover_values[key]=value
        green=action[0] in ('levels','resume','close') or action[0]=='supply'
        base=('#41934e' if green else '#286da2') if enabled else '#31546c'
        top=tint(base,'#8dd7ed',.15+value*.2)
        edge=accent or ('#b2e775' if green else '#73bce5')
        lift=2*value
        self.roundrect(x-1,y+5,w+2,h,'#10334f',r=11,width=2)
        self.roundrect(x,y-lift,w,h,base,'#173d5b',r=11,width=2)
        self.roundrect(x+3,y+2-lift,w-6,max(8,h*.48),top,r=8)
        self.line([(x+11,y+4-lift),(x+w-11,y+4-lift)],edge if enabled else '#527087',1.5)
        if accent:
            self.roundrect(x+2,y+5-lift,4,h-10,accent,r=2)
        self.text(x+12,y+h/2-lift,label,size,'#fff9df' if enabled else '#a5bac7',True,anchor='w')
        self.buttons.append(((x,y,w,h),action,enabled))


    def focus_out(self,event):
        if event.widget is self.root:
            self.keys.clear()
            if self.state=='play':
                self.paused = True

    def cancel_blueprint(self,event=None):
        self.blueprint = None

    def change_zoom(self,delta):
        if self.state=='play' and not self.panel and not self.paused:
            self.camera.target_zoom = max(.75,min(1.4,self.camera.target_zoom+delta))

    def wheel(self,event):
        if LEFT<=self.hover[0]<=LEFT+VIEW_W:
            self.change_zoom(.08 if event.delta>0 else -.08)

    def key_down(self,event):
        key = event.keysym.lower()
        pending=getattr(self,'pending_releases',{})
        if key in pending:
            self.root.after_cancel(pending.pop(key))
        if key in self.keys:
            return
        self.keys.add(key)
        if self.transition:
            return
        if key=='f11':
            self.fullscreen = not self.fullscreen
            self.root.attributes('-fullscreen',self.fullscreen)
            return
        if self.state!='play':
            if key=='escape':
                self.state = 'title'
            return
        if key in ('escape','p'):
            if self.panel:
                self.panel = None
            elif self.blueprint is not None and key=='escape':
                self.blueprint = None
            else:
                self.paused = not self.paused
            self.keys.clear()
            return
        if self.paused or self.world.outcome:
            return
        if self.panel:
            if key=='e':
                self.panel=None
                self.keys.clear()
            return
        if key=='space' and 'e' in self.keys:
            self.world.precision_strike()
        elif key=='e':
            self.interact()
        elif key=='f' and self.blueprint is not None:
            self.world.start_construction(self.blueprint)
        elif key=='b':
            self.blueprint = None
        elif key=='h':
            self.panel = ('help',None)
        elif key=='tab':
            self.category = 'structures' if self.category=='robots' else 'robots'
        elif key in tuple(str(i) for i in range(1,7)):
            if self.category=='robots' and int(key)>4:return
            index = int(key)-1+(12 if self.category=='structures' else getattr(self,'blueprint_page',0)*4)
            if index<len(SPECS):
                self.choose_blueprint(index)

    def key_up(self,event):
        key=event.keysym.lower()
        def release():
            self.keys.discard(key)
            self.pending_releases.pop(key,None)
        # X11 can report a release immediately before an autorepeated press.
        # Deferring removal avoids stuttering movement or repeatedly opening E menus.
        self.pending_releases[key]=self.root.after_idle(release)

    def interact(self):
        context = self.world.local_context()
        if not context:
            self.world.say('Walk beside a deposit, construction site, robot or the core.')
            return
        kind,key = context
        if kind=='robot':
            self.panel = ('robot',key)
            self.world.opened_robot = True
            self.keys.clear()
        elif kind=='core':
            self.panel = ('core',key)
            self.keys.clear()
        # Deposits and work orders are handled continuously while E is held.

    def choose_blueprint(self,index):
        self.blueprint = index
        self.world.selected_once = self.world.selected_once or index==0
        self.category = 'robots' if index<12 else 'structures'
        if index<12:self.blueprint_page=index//4

    def click(self,event):
        self.hover = self.logical(event)
        if self.transition:
            return
        x,y = self.hover
        for rect,action,enabled in reversed(self.buttons):
            if rect[0]<=x<=rect[0]+rect[2] and rect[1]<=y<=rect[1]+rect[3]:
                if enabled:
                    self.action(action)
                return
        # World clicks deliberately do not place, mine, upgrade or attack.

    def action(self,action):
        kind = action[0]
        if kind=='supply':
            self.world.claim_supply(action[1])
        elif kind=='drill':
            self.world.buy_drill()
        elif kind=='levels':
            self.state = 'levels'
        elif kind=='title':
            self.transition_to(('title',))
        elif kind=='start':
            self.transition_to(action)
        elif kind=='shop_page':
            self.blueprint_page=action[1]
        elif kind=='category':
            self.category = action[1]
        elif kind=='blueprint':
            self.choose_blueprint(action[1])
        elif kind=='close':
            self.panel = None
            self.keys.clear()
        elif kind=='resume':
            self.paused = False
            self.keys.clear()
        elif kind=='pause':
            self.paused = True
            self.keys.clear()
        elif kind=='help':
            self.panel = ('help',None)
            self.keys.clear()
        elif kind=='quality':
            self.quality = not self.quality
        elif kind=='nextwave':
            if distance(self.world.player.pos,self.world.corepos)<=1.95:
                self.world.start_wave()
                self.panel = None
        elif kind=='auto':
            if distance(self.world.player.pos,self.world.corepos)<=1.95:
                self.world.autoplay = True
        elif kind=='upgrade':
            if self.world.request_upgrade(action[1],action[2]):
                self.panel = None
                self.keys.clear()
        elif kind=='repair':
            if self.world.request_repair(action[1]):
                self.panel = None
                self.keys.clear()
        elif kind=='gate':
            b = self.world.buildings.get(action[1])
            if b and distance(self.world.player.pos,b.pos)<=1.75:
                if b.opened and not self.world.core_routes_open(action[1]):
                    self.world.say('This gate must stay open so bugs can reach the core.')
                else:
                    b.opened = not b.opened
                    self.world.repath()
        elif kind=='sell':
            key = action[1]
            b = self.world.buildings.get(key)
            if b and distance(self.world.player.pos,b.pos)<=1.75 and key not in self.world.orders:
                self.world.sell(key)
                self.panel = None

    def transition_to(self,action):
        self.transition = {'age':0.,'action':action,'switched':False}
        self.keys.clear()

    def new_level(self,index,tutorial=False):
        self.world = FieldWorld(index,tutorial)
        self.state = 'play'
        self.paused = False
        self.panel = None
        self.blueprint = None
        self.camera = FollowCamera()
        self.camera.x,self.camera.y = self.world.player.pos
        self.accumulator = 0
        self.keys.clear()
        self.reset_decor()

    def draw_robot(self, b, x, y, scale=1):
        role = b.role
        c = b.spec['color']
        s = scale
        angle = b.angle
        t = self.real_time
        kick=getattr(b,'visual_recoil',0)
        breathe=math.sin(t*2.5+b.x)*.65

        def rr(dx, dy, w, h, color, o='', radius=3):
            if role not in ('wall','gate','generator','mine','shield') and dy<5:
                dx-=math.cos(angle)*kick*.3
                dy-=math.sin(angle)*kick*.3+breathe*.35
            return self.roundrect(x+dx*s,y+dy*s,w*s,h*s,color,o,radius*s)

        def oval(dx, dy, w, h, color, o='', width=1):
            return self.oval(x + dx * s, y + dy * s, w * s, h * s, color, o, width * s)

        def line(pts, color, width=1):
            return self.line([(x + xx * s, y + yy * s) for xx, yy in pts], color, width * s)

        def poly(pts, color, o=''):
            return self.polygon([(x + xx * s, y + yy * s) for xx, yy in pts], color, o, 0.7 * s)
        light = tint(c, '#f1fcf0', 0.5)
        dark = tint(c, '#182e3c', 0.5)
        oval(-19, 8, 39, 15, '#718569')
        oval(-14, 10, 30, 9, '#5e755f')
        if role == 'wall':
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                n = self.world.buildings.get((b.x + dx, b.y + dy))
                if n and n.role in ('wall', 'gate'):
                    rr(-9 + dx * 11, -7 + dy * 10, 18, 19, '#738898', radius=1)
            rr(-15, -12, 30, 28, '#536e7e', '#a4bdc3', 2)
            rr(-15, -15, 30, 9, '#c0cdd0', radius=2)
            rr(-12, -12, 24, 2, '#e3e8d5', radius=1)
            for yy in (-1, 7):
                line([(-13, yy), (13, yy)], '#354e5f', 1)
            for xx in (-12, 12):
                rr(xx, -9, 3, 22, '#849ba7', radius=1)
            for xx in (-7, 3):
                poly([(xx, -3), (xx + 4, -3), (xx, 4), (xx - 4, 4)], '#e6bd79')
            return
        if role == 'gate':
            for xx in (-16, 9):
                rr(xx, -17, 7, 34, '#5e7c8b', '#b0c6cc', 2)
                rr(xx + 1, -14, 5, 4, '#a9dfc1' if b.opened else '#edc487', radius=1)
            retract = 11 if b.opened else 0
            for side in (-1, 1):
                xx = (-9 if side < 0 else 0) + side * retract
                rr(xx, -11, 9, 24, '#a7b5b3', '#dfdcbd', 1)
                line([(xx + 2, 8), (xx + 7, -5)], '#eac484', 3)
            line([(-10, 17), (10, 17)], '#778e88', 2)
            return
        if role == 'generator':
            rr(-16, -5, 32, 24, '#416775', '#8eb7bc', 4)
            for xx in (-14, 10):
                rr(xx, -13, 5, 23, '#8caeb2', radius=2)
            oval(-12, -17, 24, 26, '#395669', '#bddbdb', 1)
            oval(-9, -14, 18, 20, '#81cfcc', '#d7fff0', 1)
            for i in range(3):
                a = t * 2.4 + i * math.tau / 3
                line([(0, -4), (math.cos(a) * 8, -4 + math.sin(a) * 8)], '#e2ffe5', 2)
            rr(-10, 11, 20, 4, '#9fe3b0', radius=1)
            for xx in (-10, -3, 4):
                rr(xx, 12, 3, 2, '#d8ffd8', radius=0)
            return
        if role == 'mine':
            rr(-16, -3, 32, 23, '#4e6875', radius=3)
            for xx in (-17, 11):
                rr(xx, 6, 7, 13, '#7f949c', radius=2)
            rr(-15, -7, 30, 7, c, radius=2)
            line([(-10, 1), (-4, -20), (9, -20), (12, 9)], light, 4)
            line([(-8, 1), (-3, -17), (7, -17), (10, 9)], dark, 1)
            yy = 6 + math.sin(t * 9) * 3
            poly([(6, yy), (14, yy), (10, yy + 10)], '#b7c5c0')
            for i in range(3):
                line([(6, yy + i * 2), (13, yy + i * 2 + 2)], '#526b76', 1)
            oval(-6, -9, 10, 10, '#799495', '#dccf9e')
            return
        if role == 'shield':
            rr(-12, 1, 24, 20, '#4d5f7c', '#a8b1ce', 4)
            for xx in (-10, 5):
                rr(xx, -11, 5, 18, '#8a88b6', radius=2)
            poly([(-9, -13), (0, -27), (9, -13), (0, 2)], '#a995dc', '#ddd0ff')
            poly([(0, -27), (0, 2), (9, -13)], '#8675b6')
            line([(-5, -12), (0, -21), (0, -3)], '#eee7ff', 1)
            for i in range(2):
                a = t * 2 + i * math.pi
                oval(math.cos(a) * 12 - 2, -11 + math.sin(a) * 4 - 2, 4, 4, '#dacaff')
            return
        chassis = b.spec['chassis']
        if chassis in ('tank', 'crawler', 'rover', 'rig'):
            for side in (-1, 1):
                xx = -17 if side < 0 else 10
                rr(xx, -11, 8, 31, '#293e4d', '#7d98a6', 3)
                if chassis == 'rover':
                    for yy in (-9, 9):
                        rr(xx - 1, yy, 10, 10, '#263b48', radius=3)
                        rr(xx + 1, yy + 2, 6, 5, '#92a6ae', radius=2)
                else:
                    for yy in range(-8, 18, 5):
                        line([(xx + 1, yy), (xx + 7, yy)], '#617a88', 1.5)
            poly([(-12, -10), (10, -10), (15, -3), (13, 15), (-12, 16), (-15, 4)], dark, '#bdd0d4')
            poly([(-10, -11), (8, -11), (12, -5), (9, 1), (-11, 1)], light)
            for xx in (-10, 7):
                rr(xx, 7, 4, 6, c, radius=1)
        elif chassis == 'walker':
            for side in (-1, 1):
                for yy in (-1, 1):
                    line([(side * 6, yy * 5), (side * 14, yy * 11), (side * 19, yy * 18)], '#344b5b', 5)
                    line([(side * 6, yy * 5), (side * 14, yy * 11)], light, 2)
                    oval(side * 14 - 3, yy * 11 - 3, 6, 6, '#8ba9b4')
                    rr(side * 19 - 4, yy * 18 - 2, 8, 5, '#4f6878', radius=2)
            poly([(-9, -10), (8, -10), (12, -3), (10, 10), (-10, 10), (-12, -3)], c, '#d6e2df')
            rr(-5, -7, 10, 9, dark, radius=2)
        else:
            heavy = chassis == 'heavy'
            for side in (-1, 1):
                xx = side * 7
                rr(xx - 3, 5, 6, 12, '#41596c', radius=2)
                rr(xx - 3, 10, 6, 5, c, radius=1)
                rr(xx - 5, 17, 11, 5, '#b5c8cf', radius=2)
                line([(xx - 3, 17), (xx + 4, 17)], '#e6ecde', 1)
            poly([(-12 if heavy else -9, -9), (12 if heavy else 9, -9), (14 if heavy else 10, 4), (8, 12), (-8, 12), (-14 if heavy else -10, 4)], c, '#ccdfe1')
            poly([(-9, -8), (8, -8), (6, -2), (-6, -2)], light)
            rr(-5, 1, 10, 6, dark, radius=2)
            for side in (-1, 1):
                rr(side * 14 - 4, -8, 9 if heavy else 7, 13, c, light, 2)
                rr(side * 14 - 2, 4, 5, 8, '#455e70', radius=2)
            oval(-2, 2, 4, 4, '#e2f7ca')
        rr(-4, -14, 8, 5, '#4d6577', radius=1)
        rr(-9, -24, 18, 13, '#c6d8db', '#edf4e8', 4)
        rr(-7, -20, 14, 6, '#294a60', radius=2)
        line([(-5, -18), (4, -18)], '#8aede7', 1.4)
        for xx in (-11, 8):
            rr(xx, -20, 3, 6, c, radius=1)
        line([(-5, -24), (4, -24)], '#f1f7eb', 1)
        recoil = kick+5*min(1,b.animation/.12)

        def wp(px, py):
            return (math.cos(angle) * (px - recoil) - math.sin(angle) * py, math.sin(angle) * (px - recoil) + math.cos(angle) * py)

        def gunpoly(points, cc, oo=''):
            poly([wp(*q) for q in points], cc, oo)

        def gunline(points, cc, ww=1):
            line([wp(*q) for q in points], cc, ww)
        if role == 'repair':
            arm_swing=math.sin(t*4+b.x)*7
            line([(7,3),(19,-8+arm_swing),(25,2+arm_swing)],'#496b79',4)
            line([(7,3),(19,-8+arm_swing)],'#b8d6d1',2)
            line([(25,2+arm_swing),(20,6+arm_swing),(23,10+arm_swing)],'#a1e4bc',2)
            line([(25,2+arm_swing),(30,6+arm_swing),(27,10+arm_swing)],'#a1e4bc',2)
            rr(-8, -1, 12, 10, '#4d8b80', radius=2)
            line([(-5, 4), (1, 4)], '#e0fce3', 2)
            line([(-2, 1), (-2, 7)], '#e0fce3', 2)
        elif role == 'command':
            line([(10, 1), (13, -33)], '#4c667d', 2)
            oval(4+math.sin(t*2)*3,-36,18,4+abs(math.cos(t*2))*7,'#a8bfd0','#deeddf')
            line([(13, -36), (13, -42)], '#c6dee5', 1)
            rr(-7, 0, 14, 8, '#476b96', radius=2)
            for i in range(3):
                rr(-5 + i * 4, 2, 2, 3, '#c0e7eb', radius=0)
            if math.sin(t * 3) > 0.5:
                oval(11, -43, 4, 4, '#b1eeca')
        elif role == 'rocket':
            for side in (-1, 1):
                rr(side * 10 - 5, -5, 10, 18, '#415b68', light, 2)
                for yy in (-2, 5):
                    oval(side * 10 - 3, yy, 6, 6, '#1d3545', '#e5c18b')
            rr(-5, -2, 10, 12, c, radius=2)
        elif role == 'mortar':
            line([(-10, 9), (2, -10), (12, 9)], '#3d5769', 4)
            barrel_y=-24+kick*1.2
            line([(0,2),(9,barrel_y)],'#3b5367',12)
            line([(0,2),(9,barrel_y)],'#afbac1',8)
            oval(3,barrel_y-5,13,8,'#253e50','#d1dbd4',2)
            oval(6,barrel_y-3,7,4,'#152a3c')
            rr(-8, 2, 15, 10, '#b78e8d', radius=2)
        elif role == 'cryo':
            for xx in (-11, 5):
                rr(xx, -7, 7, 19, '#365f78', '#98c9d3', 3)
                rr(xx + 1, -3, 5, 11, '#9be4e3', radius=2)
                line([(xx + 2, -1), (xx + 2, 5)], '#e5ffff', 1)
            gunpoly([(3, -5), (19, -5), (23, -8), (26, -6), (26, 6), (23, 8), (19, 5), (3, 5)], '#527b8b', '#c2eaeb')
            gunline([(22, -5), (22, 5)], '#b6f4ef', 2)
        elif role == 'flame':
            rr(-8, -4, 14, 17, '#e1a66f', '#e8d0a2', 3)
            for xx in (-6, 1):
                rr(xx, -2, 4, 12, '#a8664b', radius=2)
            gunpoly([(4, -4), (20, -4), (25, -7), (27, -6), (27, 6), (25, 7), (20, 4), (4, 4)], '#52626b', '#bdcac9')
            gunline([(21, 0), (28, 0)], '#ecb072', 3)
            tip = wp(29, 0)
            oval(tip[0] - 2, tip[1] - 2, 4, 4, '#ffce7a')
        elif role == 'rail':
            for side in (-1, 1):
                gunpoly([(0, side * 3), (27, side * 3), (30, side * 6), (0, side * 6)], '#526f85', '#b7d7de')
                gunline([(4, side * 4), (27, side * 4)], '#8fe4ed', 1.5)
            for xx in (8, 14, 20):
                gunline([(xx, -7), (xx, 7)], '#8ba8bc', 1)
        elif role == 'heavy':
            gunpoly([(1, -6), (13, -6), (19, -4), (19, 4), (13, 6), (1, 6)], '#40586b', '#b6cad1')
            for i in range(3):
                shift=math.sin(t*(40 if b.animation else 3)+i*math.tau/3)*4
                gunline([(12,shift),(27,shift)],'#546d7e',2.2)
            gunline([(23, -5), (23, 5)], '#b0c4c9', 2)
        elif role == 'sniper':
            gunpoly([(1, -4), (13, -4), (15, -2), (34, -2), (34, 2), (13, 3), (1, 4)], '#405568', '#b7c5ce')
            gunline([(10, -6), (19, -6)], '#9b82be', 3)
            gunline([(30, -3), (35, -3)], '#d5dce0', 1)
        elif role == 'air':
            for shift in (-4, 4):
                gunline([(3, shift), (26, shift)], '#526a79', 3)
            rr(-8, -3, 15, 12, c, radius=2)
            line([(-4, -18), (-2, -31), (4, -34), (8, -31)], '#b8cad3', 1)
        elif role == 'scatter':
            gunpoly([(1, -5), (12, -5), (16, -4), (23, -4), (23, 4), (16, 4), (12, 5), (1, 5)], '#4e5c70', '#c5d0d5')
            gunline([(19, -5), (19, 5)], '#e3a3c4', 2)
        else:
            gunpoly([(0, -4), (12, -4), (14, -2), (23, -2), (23, 2), (12, 4), (0, 4)], '#3d5668', '#c5d7da')
            gunline([(15, -3), (21, -3)], c, 2)
        if b.paths[0] >= 2:
            for xx in (-7, 6):
                rr(xx, 6, 3, 7, '#f3d585', radius=1)
        if b.paths[1] >= 2:
            rr(-7, 0, 14, 3, '#c0aff3', radius=1)
        for path, n in enumerate(b.paths):
            for i in range(n):
                oval(-9 + i * 7, 25 + path * 4, 4, 3, COLORS['gold'] if path == 0 else COLORS['purple'])
        if b.shield:
            rr(-23, -29, 46, 57, '', '#c4b8fa', 10)
            line([(-22, -15), (-22, -23), (-13, -28)], '#ece3ff', 1)
        if b.jam:
            line([(-10, -33), (-4, -37), (2, -33), (10, -37)], '#e1c88e', 1.5)

    def draw_bug(self, e, x, y, scale=1):
        """Anatomical silhouettes, articulated legs, shiny carapaces and wingbeats."""
        r = BUGS[e.name][3] * scale
        a = e.angle
        t = self.real_time
        walk_phase=getattr(e,'walk_phase',t*9+e.x)
        walking=getattr(e,'walk_blend',1.)
        if e.stun:walking=0.
        strike_clock=getattr(e,'attack_clock',0)
        strike_length=max(.1,getattr(e,'attack_length',.42))
        strike=math.sin((1-strike_clock/strike_length)*math.pi) if strike_clock else 0.
        stride=math.sin(walk_phase)*walking
        leap_clock=getattr(e,'leap_clock',0)
        leap=math.sin((1-leap_clock/.5)*math.pi) if leap_clock else 0.
        fly = e.flying
        bob=(math.sin(t*6+e.y)*4 if fly else abs(stride)*1.6)*scale
        y+=bob-leap*24*scale
        x+=math.cos(a)*strike*r*.42
        y+=math.sin(a)*strike*r*.42
        a+=stride*.085 if not fly else math.sin(t*3+e.x)*.035
        color = BUGS[e.name][4]
        light = tint(color, '#fff2bf', 0.38)
        dark = tint(color, '#1c312d', 0.45)

        def p(dx, dy):
            # Abdomen, thorax and head flex separately rather than sliding as one image.
            if dx<-.25:
                dy+=math.sin(walk_phase-.65)*.16*walking*(-dx)
                dx*=1+strike*.07
            elif dx>.48:
                dy+=math.sin(walk_phase+.8)*.07*walking
                dx+=strike*.19
                dy*=1+strike*.12
            return (x+(math.cos(a)*dx-math.sin(a)*dy)*r,
                    y+(math.sin(a)*dx+math.cos(a)*dy)*r)

        def poly(points, c, outline='', width=1, smooth=False):
            pts = [p(dx, dy) for dx, dy in points]
            self.canvas.create_polygon(*[v for q in pts for v in q], fill=c, outline=outline, width=width * self.scale * scale, smooth=smooth, splinesteps=6)

        def line(points, c, width=1):
            self.line([p(*q) for q in points], c, width * scale)

        def ellipse(cx, cy, rx, ry, c, outline='', smooth=True):
            poly([(cx + math.cos(i * math.tau / 12) * rx, cy + math.sin(i * math.tau / 12) * ry) for i in range(12)], c, outline, 0.7, smooth)

        def shell(cx, cy, rx, ry, c):
            ellipse(cx, cy, rx, ry, tint(c, '#172f2a', 0.4))
            ellipse(cx - 0.06, cy - 0.04, rx * 0.94, ry * 0.92, c)
            ellipse(cx - 0.16, cy - 0.16, rx * 0.65, ry * 0.52, tint(c, '#fcf3c5', 0.25))
            line([(cx - rx * 0.55, cy - ry * 0.3), (cx - rx * 0.15, cy - ry * 0.55)], tint(c, '#f7ffdf', 0.65), 0.9)
        shadow_y = y + 8 * scale + (7 * scale if fly else 0)
        self.oval(x - r * 1.05, shadow_y - r * 0.4, r * 2.1, r * 0.8, '#7e906f')
        self.oval(x - r * 0.8, shadow_y - r * 0.26, r * 1.6, r * 0.52, '#6e8267')
        for side in (-1, 1):
            for index, root in enumerate((-0.35, 0.1, 0.5)):
                if e.name == 'Mantis' and index == 2:
                    continue
                leg_angle=walk_phase+index*math.pi*.76+(0 if side==1 else math.pi)
                phase=math.sin(leg_angle)*.55*walking
                lift=max(0,math.cos(leg_angle))*.34*walking
                if e.stun:
                    phase = 0
                knee=(root-.15+phase*.55,side*((.85 if e.name!='Grasshopper' else 1.1)-lift*.5))
                foot=(root-.4-phase,side*((1.32 if e.name!='Grasshopper' else 1.65)-lift))
                if e.name == 'Grasshopper' and index == 0:
                    knee = (0.55, side * 1.05)
                    foot = (-1.05+phase*1.5,side*(1.65-lift))
                line([(root, side * 0.2), knee, foot], dark, 2.3)
                line([(root, side * 0.2), knee], light, 1.0)
                ellipse(knee[0], knee[1], 0.075, 0.075, light)
        if fly:
            flutter = .16+abs(math.sin(t*(31 if e.name=='Dragonfly' else 24)+e.y)) * 1.35
            for side in (-1, 1):
                for offset in (-0.25, 0.36) if e.name == 'Dragonfly' else (0,):
                    points = [(offset + 0.35, side * 0.12), (offset + 0.2, side * 1.05 * flutter), (offset - 0.8, side * 1.85 * flutter), (offset - 1.15, side * 1.45 * flutter), (offset - 0.35, side * 0.15)]
                    poly(points, '#cbded1', '#87b1a9', 0.6, True)
                    line([(offset + 0.2, side * 0.2), (offset - 0.6, side * 1.5 * flutter)], '#a3c1b1', 0.6)
        if e.name == 'Ant':
            shell(-0.82, 0, 0.67, 0.52, color)
            shell(0.04, 0, 0.32, 0.29, color)
            line([(-0.38, -0.12), (0.28, -0.12)], dark, 2)
            shell(0.62, 0, 0.43, 0.37, color)
        elif e.name == 'Termite':
            shell(-0.6, 0, 0.8, 0.47, '#d2bd91')
            for i in range(5):
                line([(-1 + i * 0.25, -0.38), (-1 + i * 0.25, 0.38)], '#ac966c', 0.7)
            shell(0.45, 0, 0.42, 0.36, '#ba955e')
            for side in (-1, 1):
                line([(0.72, side * 0.14), (1.07, side * 0.32), (1.18, side * 0.08)], '#6c5a3e', 1.8)
        elif e.name == 'Wasp':
            shell(-0.65, 0, 0.82, 0.42, '#edc650')
            for dx in (-1.1, -0.73, -0.35):
                line([(dx, -0.34), (dx, 0.34)], '#554c37', 2.4)
            poly([(-1.36, -0.09), (-1.72, 0), (-1.36, 0.09)], '#5b5741')
            shell(0.22, 0, 0.43, 0.35, '#b29b4d')
            shell(0.7, 0, 0.31, 0.29, '#d6b74c')
        elif e.name == 'Dragonfly':
            poly([(0.2, -0.19), (-1.9, -0.06), (-2.05, 0), (-1.9, 0.06), (0.2, 0.19)], '#4e9ca6', '#427e83')
            for i in range(7):
                line([(-0.2 - i * 0.23, -0.09), (-0.2 - i * 0.23, 0.09)], '#a3d5c4', 0.8)
            shell(0.26, 0, 0.43, 0.29, '#74b2ae')
            for side in (-1, 1):
                shell(0.73, side * 0.22, 0.29, 0.24, '#a0cf99')
        elif e.name == 'Mantis':
            shell(-0.73, 0, 0.82, 0.33, '#83ac69')
            poly([(-1.25, 0), (-0.3, -0.32), (0.25, 0), (-0.3, 0.32)], '#a3c07c', '#688956')
            poly([(-0.05, -0.15), (0.9, -0.17), (1.0, 0), (0.9, 0.17), (-0.05, 0.15)], '#7fa65f', '#577c4b')
            poly([(0.8, -0.48), (1.3, 0), (0.8, 0.48), (0.64, 0.12), (0.64, -0.12)], '#a0c57d', '#628954')
            for side in (-1, 1):
                bend = .25*math.sin(t*3)+strike*.65
                line([(0.5, side * 0.2), (1.2, side * (0.95 + bend)), (1.5+strike*.65, side*(.25-strike*.12))], '#597c47', 3)
                line([(0.5, side * 0.2), (1.2, side * (0.95 + bend))], '#acd08b', 1.7)
                for i in range(3):
                    line([(1.25 + i * 0.07, side * (0.8 - i * 0.16)), (1.15 + i * 0.07, side * (0.73 - i * 0.16))], '#d3dda5', 0.8)
        elif e.name == 'Grasshopper':
            shell(-0.65, 0, 0.9, 0.39, '#8cab59')
            poly([(-1.4, 0), (0.2, -0.34), (0.5, 0), (0.2, 0.34)], '#a5bd72', '#718e4c')
            line([(-1.25, 0), (0.4, 0)], '#d7d99a', 1)
            shell(0.55, 0, 0.42, 0.37, '#a2bb6a')
        elif e.name == 'Moth':
            flap = .24+.95*(.5+.5*math.sin(t*13+e.x))
            for side in (-1, 1):
                poly([(0.65, 0), (0.65, side * 1.5 * flap), (-0.12, side * 1.7 * flap), (-1.3, side * 0.84 * flap), (-0.45, 0)], '#bca98c', '#897c63', 0.9, True)
                poly([(0.4, side * 0.3), (0.44, side * 1.25 * flap), (-0.1, side * 1.4 * flap), (-0.95, side * 0.74)], '#d6c5a5', '', 1, True)
                ellipse(-0.15, side * 0.93 * flap, 0.29, 0.24, '#8a8168')
                ellipse(-0.15, side * 0.93 * flap, 0.16, 0.14, '#d8cba7')
                ellipse(-0.15, side * 0.93 * flap, 0.07, 0.07, '#625e4c')
                line([(0.45, side * 0.3), (-0.1, side * 1.2 * flap)], '#a7997c', 0.8)
            shell(-0.23, 0, 0.8, 0.22, '#a08c6d')
            shell(0.55, 0, 0.32, 0.3, '#c8b896')
        elif e.name == 'Cockroach':
            shell(-0.25, 0, 1.03, 0.52, '#9d754c')
            for i in range(7):
                line([(-1 + i * 0.24, -0.4), (-1 + i * 0.24, 0.4)], '#7c603e', 0.6)
            poly([(-1.1, 0), (0.45, -0.4), (0.55, 0.0), (0.45, 0.4)], '#af8b60', '#826440', 0.5, True)
            line([(-1.05, 0), (0.5, 0)], '#d0ac78', 0.8)
            shell(0.65, 0, 0.35, 0.39, '#85663f')
        else:
            c = '#d9674f' if e.name == 'Ladybug' else color
            if e.name == 'Bombardier Beetle':
                c = '#647d68'
            shell(-0.35, 0, 0.95, 0.69, c)
            line([(-1.22, 0), (0.35, 0)], dark, 1.2)
            for side in (-1, 1):
                line([(-1.05, side * 0.2), (-0.65, side * 0.47), (-0.15, side * 0.5), (0.26, side * 0.3)], tint(c, '#f4f2bc', 0.35), 0.7)
            shell(0.48, 0, 0.42, 0.46, '#c99a64' if e.name == 'Bombardier Beetle' else tint(c, '#374c38', 0.25))
            shell(0.88, 0, 0.29, 0.33, tint(c, '#253b30', 0.35))
            if e.name == 'Ladybug':
                for dx, dy in ((-0.85, -0.3), (-0.85, 0.3), (-0.3, -0.4), (-0.3, 0.4), (0.1, -0.25), (0.1, 0.25)):
                    ellipse(dx, dy, 0.15, 0.12, '#493d32')
            if e.name in ('Stag Beetle', 'Goliath Beetle'):
                for side in (-1, 1):
                    poly([(0.8,side*.25),(1.2,side*(.6+strike*.3)),(1.7,side*(.47+strike*.35)),(1.82,side*(.1+strike*.27)),(1.48,side*(.29+strike*.2)),(1.2,side*.25)], tint(c, '#554c37', 0.2), dark, 0.6, True)
                if e.name == 'Goliath Beetle':
                    for side in (-1, 1):
                        for i in range(3):
                            line([(-0.98 + i * 0.4, side * 0.48), (-0.85 + i * 0.4, side * 0.62), (-0.57 + i * 0.4, side * 0.52)], '#c4bd94', 1)
                    for i in range(4):
                        line([(-1 + i * 0.27, -0.38), (-1 + i * 0.27, 0.38)], '#aaa27a', 0.7)
        if e.name in ('Ant','Termite','Cockroach'):
            for side in (-1,1):
                jaw=.16+strike*.3
                line([(1.,side*.12),(1.23,side*jaw),(1.38,side*.08)],dark,1.5)
        head = 0.87 if e.name not in ('Mantis', 'Dragonfly') else 1.1 if e.name == 'Mantis' else 0.83
        for side in (-1, 1):
            long = 1.3 if e.name == 'Cockroach' else 0.7
            line([(head, side * 0.2), (head + 0.3, side * 0.47), (head + long, side * (0.7 + 0.08 * math.sin(t * 3)))], dark, 0.8)
            ellipse(head + 0.05, side * 0.24, 0.095, 0.095, '#252f25')
            ellipse(head + 0.07, side * 0.26, 0.03, 0.03, '#e7eec7')
        if e.slow_time:
            self.oval(x - r * 1.2, y - r * 1.2, r * 2.4, r * 2.4, '', '#a8edee', 1)
            for i in range(3):
                aa = t + i * 2.1
                px = x + math.cos(aa) * r
                py = y + math.sin(aa) * r
                self.polygon([(px, py - 3), (px + 2, py), (px, py + 3), (px - 2, py)], '#d3fbf0')
        if e.burn_time:
            for i in range(4):
                px = x + math.sin(i * 4 + t * 9) * r * 0.5
                py = y + math.cos(i * 3) * r * 0.3
                self.polygon([(px - 3, py + 2), (px - 4, py - 4), (px, py - 11 - i % 2 * 4), (px + 3, py - 3), (px + 3, py + 2)], '#efae6c')
                self.oval(px - 1, py - 5, 3, 6, '#ffdf92')
        if e.stun:
            for i in range(3):
                aa = t * 3 + i * 2.1
                px = x + math.cos(aa) * r * 0.7
                py = y - r - 5 + math.sin(aa) * 2
                self.text(px, py, '+', 10, '#e4fff0', True, anchor='center')
        if e.marked:
            rr = r + 4
            for side in (-1, 1):
                self.line([(x + side * rr, y - 4), (x + side * rr, y - rr), (x + side * (rr - 5), y - rr)], COLORS['purple'], 1)
        if e.hp < e.maxhp:
            self.roundrect(x - r, y - r - 11, r * 2, 4, '#536252', r=2)
            self.roundrect(x - r, y - r - 11, max(0.2, r * 2 * e.hp / e.maxhp), 4, '#bcf1a6', r=2)

    def draw_effect(self, f):
        kind = f['kind']
        progress = 1 - f['ttl'] / f['life']
        x, y = self.point(f['pos'])
        c = f['color']
        if not self.quality:
            if kind not in ('hit', 'muzzle', 'defeat'):
                App.draw_effect(self, f)
            return
        if kind in ('explosion', 'defeat', 'hit'):
            size = f['size'] * TILE
            if kind == 'explosion':
                r = size * (0.2 + progress)
                for i in range(5):
                    a = i * 2.4
                    rr = (8 + progress * size * 0.35) * (1 - progress * 0.65)
                    px = x + math.cos(a) * r * 0.45
                    py = y + math.sin(a) * r * 0.4 - progress * 13
                    self.oval(px - rr, py - rr, rr * 2, rr * 2, tint('#e6c388', '#a0a687', progress))
                if progress < 0.5:
                    rr = size * (0.4 - progress * 0.5)
                    self.oval(x - rr, y - rr, rr * 2, rr * 2, '#ffdc8e')
                    self.oval(x - rr * 0.5, y - rr * 0.5, rr, rr, '#fff3c2')
                self.oval(x - r, y - r * 0.65, r * 2, r * 1.3, '', tint('#fff1a4', '#b2ba8d', progress), max(0.6, 3 * (1 - progress)))
            for i in range(10 if kind == 'explosion' else 6):
                a = i * 2.399
                travel = size * (0.3 + progress * 1.3)
                px = x + math.cos(a) * travel
                py = y + math.sin(a) * travel - progress * 13 + progress * progress * 24
                length = (1 - progress) * 6
                self.line([(px, py), (px + math.cos(a) * length, py + math.sin(a) * length)], tint(c, '#f9dfaa', 0.4), 2 * (1 - progress) + 0.4)
            return
        if kind == 'build':
            r = (0.3 + progress * 0.8) * TILE
            self.oval(x - r, y - r * 0.5, 2 * r, r, '', tint(c, '#fff3ce', 0.5), 2 * (1 - progress) + 0.5)
            for i in range(6):
                a = i * math.tau / 6
                px = x + math.cos(a) * TILE * 0.5
                py = y + math.sin(a) * TILE * 0.3 - (1 - progress) * 30
                self.roundrect(px - 2, py - 2, 4, 4, tint(c, '#fff4cd', 0.5), r=1)
            return
        if kind == 'upgrade':
            for i in range(3):
                rr = (progress + i * 0.25) % 1 * 40
                self.oval(x - rr, y - rr * 0.5, rr * 2, rr, '', '#ffe4a5', 1.5)
            for i in range(8):
                a = i * 2.4
                px = x + math.cos(a) * 22
                py = y - progress * 50 + math.sin(a) * 10
                self.polygon([(px - 2, py), (px, py - 4), (px + 2, py), (px, py + 4)], '#fff0b5')
            return
        super().draw_effect(f)

    def draw_player(self):
        p = self.world.player
        x,y = self.point(p.pos)
        z = self.camera.zoom
        walk = math.sin(p.stride) if p.moving else math.sin(self.real_time*2)*.08
        bob = abs(walk)*3.2*z
        y -= bob
        def rr(dx,dy,w,h,c,o='',radius=3):
            self.roundrect(x+dx*z,y+dy*z,w*z,h*z,c,o,radius*z)
        def line(points,c,width=1):
            self.line([(x+a*z,y+b*z) for a,b in points],c,width*z)
        def oval(dx,dy,w,h,c,o=''):
            self.oval(x+dx*z,y+dy*z,w*z,h*z,c,o)
        # Visible boots, alternating knees, bobbing backpack and independent arms.
        oval(-15,8,30,13,'#6b8b70')
        oval(-10,10,22,7,'#58775e')
        for side in (-1,1):
            swing=walk*side*8
            lift=max(0,math.cos(p.stride+(0 if side==1 else math.pi)))*4 if p.moving else 0
            foot_x=side*8+math.sin(p.stride+side*.8)*3 if p.moving else side*8
            line([(side*6,5),(side*8+swing*.25,11+swing*.35),(foot_x,18+swing-lift)],'#415d6a',5)
            rr(foot_x-4,17+swing-lift,10,5,'#d7dacc',radius=2)
            line([(side*7-2,7),(side*7-2,12+swing)],'#98abb0',1)
        rr(-12,-9,24,22,'#587a83','#b8cecb',5)
        rr(-15,-7,6,18,'#76969b',radius=3)
        rr(9,-7,6,18,'#76969b',radius=3)
        rr(-10,-11,20,20,'#e4bb66','#f4dda2',4)
        rr(-7,-7,14,4,'#ffe1a0',radius=2)
        rr(-6,0,12,5,'#698e91',radius=2)
        for i in range(3):
            rr(-4+i*4,1,2,2,'#c6edda',radius=0)
        if p.working and p.tool_target:
            tx,ty = self.point(p.tool_target)
            target_angle = math.atan2(ty-y,tx-x)
            context=self.world.local_context()
            mining=context is not None and context[0]=='deposit'
            if mining:
                target_angle+=math.sin(p.tool_time*10)*.8-.2
            else:
                target_angle+=math.sin(p.tool_time*9)*.2
            arm=24+math.sin(p.tool_time*(10 if mining else 12))*5
            ax,ay = math.cos(target_angle)*arm,math.sin(target_angle)*arm
            line([(9,-3),(ax*.55,ay*.5-1),(ax,ay)],'#506f7c',5)
            line([(9,-5),(ax*.55,ay*.5-3)],'#ecd098',3)
            rr(ax-3,ay-3,7,7,'#b9d1d3',radius=2)
            line([(ax-3,ay-3),(ax+4,ay+4)],'#f7e7aa',2)
            line([(-11,-3),(-15,6)],'#d5af66',5)
            # Tool sparks are localized to resources and construction, never bugs.
            for i in range(3):
                phase=(p.tool_time*3+i*.33)%1
                px=tx+math.cos(i*2.2+p.tool_time)*phase*14*z
                py=ty-phase*16*z+phase*phase*11*z
                self.line([(px,py),(px+3*z,py-2*z)],'#ffe5a0',1.5)
        else:
            for side in (-1,1):
                swing=-walk*side*8
                line([(side*12,-5),(side*15,3+swing),(side*13,9+swing)],'#c6a360',5)
                oval(side*13-3,7+swing,6,6,'#a8c2c5')
        rr(-5,-17,10,8,'#6a8891',radius=2)
        rr(-11,-27,22,17,'#f0cc76','#fff0b2',6)
        rr(-8,-23,16,9,'#2e566b',radius=3)
        line([(-5,-20),(5,-20)],'#a4e9e8',1.6)
        rr(-8,-28,16,4,'#ffe5a0',radius=2)
        for side in (-1,1):
            rr(side*11-2,-22,4,7,'#83a3a9',radius=2)
        # A small directional light keeps facing clear for local blueprint placement.
        fx,fy = x+math.cos(p.angle)*21*z,y+math.sin(p.angle)*21*z
        self.oval(fx-2*z,fy-2*z,4*z,4*z,'#f8efb5')
        if p.stagger:
            self.text(x,y-42*z,'!',15,'#ffe2a1',True,anchor='center')
        self.text(x,y+31*z,'YOU',7,'#264e51',True,anchor='center')

    def draw_core(self):
        x,y = self.point(self.world.corepos)
        z = self.camera.zoom
        for i in range(3):
            rr=(23+i*6)*z
            self.oval(x-rr,y-rr*.35+13*z,rr*2,rr*.7,'','#a5c6b1',1)
        self.roundrect(x-25*z,y-17*z,50*z,42*z,'#416b7c','#bfd4d1',8*z,1.5)
        self.roundrect(x-20*z,y-22*z,40*z,14*z,'#91b4b7','#dce8d4',5*z)
        for side in (-1,1):
            self.roundrect(x+side*22*z-4*z,y-13*z,8*z,38*z,'#789ba4','#cfdfd7',3*z)
        self.oval(x-15*z,y-21*z,30*z,34*z,'#4e9fad','#cdf8e8',2)
        pulse=(8+math.sin(self.real_time*3)*1.5)*z
        self.oval(x-pulse,y-7*z-pulse,2*pulse,2*pulse,'#c6f2d4')
        self.oval(x-pulse*.4,y-7*z-pulse*.4,pulse*.8,pulse*.8,'#f1ffdb')
        angle=self.real_time*1.8
        self.line([(x+math.cos(angle)*12*z,y-7*z+math.sin(angle)*14*z),
                   (x-math.cos(angle)*12*z,y-7*z-math.sin(angle)*14*z)],'#a9e3da',1)
        self.text(x,y+38*z,'CORE',9,'#315655',True,anchor='center')
        if self.world.corehp<self.world.coremax:
            self.roundrect(x-30*z,y-38*z,60*z,4*z,'#5e685b',r=1)
            self.roundrect(x-30*z,y-38*z,max(.2,60*z*self.world.corehp/self.world.coremax),4*z,'#b2e4b3',r=1)

    def draw_foundation(self,b,order):
        x,y = self.point(b.pos)
        z = self.camera.zoom
        progress = order.fraction
        self.roundrect(x-18*z,y-13*z,36*z,29*z,'#7c948a','#c9d5b2',5*z)
        height = (9+progress*27)*z
        for side in (-1,1):
            xx=x+side*14*z
            self.line([(xx,y+11*z),(xx,y-height)],'#6a8590',3*z)
            self.line([(xx-2*z,y-height),(xx+3*z,y-height)],'#e4cc98',2*z)
        self.line([(x-14*z,y-height),(x+14*z,y-height)],'#adc1bd',3*z)
        self.line([(x-14*z,y+9*z),(x+14*z,y-height)],'#dac18a',1.2)
        for i in range(3):
            yy=y+(8-i*(5+progress*5))*z
            self.roundrect(x-9*z,yy,18*z,4*z,tint('#8aa6ac',SPECS[b.kind]['color'],progress),r=1)
        if progress>.6:
            self.roundrect(x-6*z,y-height-5*z,12*z,10*z,'#bed2cf',r=3)
            self.line([(x-4*z,y-height-1*z),(x+4*z,y-height-1*z)],'#76cbd4',2*z)
        self.roundrect(x-20*z,y+22*z,40*z,4*z,'#5c766e',r=1)
        self.roundrect(x-20*z,y+22*z,max(.2,40*z*progress),4*z,'#f0d093',r=1)
        self.text(x,y+33*z,f'{round(progress*100)}%',8,'#264d50',True,anchor='center')

    def draw_deposit(self,key,data):
        resource,amount = data
        x,y = self.point((key[0]+.5,key[1]+.5))
        z = self.camera.zoom
        c = RESOURCE_COLORS[resource] if amount else '#8d9e89'
        self.oval(x-22*z,y+3*z,45*z,19*z,'#7f9b76')
        for dx,dy,size in ((-11,4,12),(2,-3,17),(12,8,10)):
            points=[(x+(dx-size*.6)*z,y+dy*z),(x+(dx-size*.3)*z,y+(dy-size)*z),
                    (x+(dx+size*.35)*z,y+(dy-size*1.2)*z),(x+(dx+size*.7)*z,y+(dy-1)*z),
                    (x+dx*z,y+(dy+6)*z)]
            self.polygon(points,c,'#6d857b',.65,True)
            self.polygon([points[1],points[2],points[4]],tint(c,'#fff4cf',.45),'',.5,True)
            self.line([points[2],points[4]],tint(c,'#f8ffe5',.7),1)
        if amount:
            self.text(x,y+29*z,RESOURCE_NAMES[resource].upper(),7,'#365955',True,anchor='center')
        context = self.world.local_context()
        if context==('deposit',key):
            self.oval(x-25*z,y-20*z,50*z,43*z,'','#fff1bc',1)

    def draw_approaches(self):
        z=self.camera.zoom
        for route_id,route in enumerate(self.world.approach_routes):
            points=[(x+.5,y+.5) for x,y in route]
            if len(points)>1:
                outside,inside=points[-2],points[-1]
                low,high=0.,1.
                for _ in range(16):
                    t=(low+high)/2
                    p=(outside[0]+(inside[0]-outside[0])*t,outside[1]+(inside[1]-outside[1])*t)
                    if self.world.in_core_area(p):high=t
                    else:low=t
                points[-1]=(outside[0]+(inside[0]-outside[0])*high,outside[1]+(inside[1]-outside[1])*high)
            screen=[self.point(p) for p in points]
            self.line(screen,tint(self.world.level.ground_dark,'#697a59',.2),41*z,joinstyle='round',capstyle='round')
            self.line(screen,'#c7b68a',34*z,joinstyle='round',capstyle='round')
            self.line(screen,'#d6c69e',25*z,joinstyle='round',capstyle='round')
            for i in range(1,len(route)-1,3):
                cell=route[i]
                next_cell=route[i+1]
                if self.world.in_core_area((cell[0]+.5,cell[1]+.5)):
                    continue
                x,y=self.point((cell[0]+.5,cell[1]+.5))
                a=math.atan2(next_cell[1]-cell[1],next_cell[0]-cell[0])
                pulse=.35+.12*math.sin(self.real_time*2-route_id)
                color=tint('#9a936e','#f7edc4',pulse)
                dx,dy=math.cos(a)*5*z,math.sin(a)*5*z
                sx,sy=-math.sin(a)*4*z,math.cos(a)*4*z
                self.line([(x-dx+sx,y-dy+sy),(x+dx*.5,y+dy*.5),(x-dx-sx,y-dy-sy)],color,1.5)
            x,y=self.point((route[0][0]+.5,route[0][1]+.5))
            initial=1 if self.world.level_id<3 else 2 if self.world.level_id<6 else 3
            unlock=1 if route_id<initial else 1+(route_id-initial+1)*5
            label=f'Trail {route_id+1}' if self.world.wave>=unlock else f'Trail {route_id+1} / Wave {unlock}'
            self.text(x,y-28*z,label,7,'#69734f',True,anchor='center')

    def draw_core_ring(self):
        x,y=self.point(self.world.corepos)
        r=self.world.core_build_radius*TILE*self.camera.zoom
        self.oval(x-r,y-r,2*r,2*r,'','#6c8f6a',4)
        self.oval(x-r,y-r,2*r,2*r,'','#e7edb7',1.5)
        # Fence-like ticks make the area readable as a defended camp perimeter.
        for i in range(28):
            a=i*math.tau/28
            c=(self.world.corepos[0]+math.cos(a)*7,self.world.corepos[1]+math.sin(a)*7)
            if any(distance(c,(p[0]+.5,p[1]+.5))<.9 for p in self.world.path_tiles):
                continue
            px,py=self.point(c)
            self.line([(px-math.cos(a)*3,py-math.sin(a)*3),(px+math.cos(a)*3,py+math.sin(a)*3)],'#f0efc5',1.3)
        lx,ly=self.point((self.world.corepos[0],self.world.corepos[1]+6.25))
        self.roundrect(lx-91,ly-11,182,25,'#557a5f','#d2dfa8',r=9)
        self.text(lx,ly+2,'CORE BUILD AREA',8,'#edf0cf',True,anchor='center')
        if self.blueprint is not None and SPECS[self.blueprint]['role'] in ('wall','gate'):
            rr=2.5*TILE*self.camera.zoom
            self.oval(x-rr,y-rr,2*rr,2*rr,'','#edbd93',1.5)
        if self.blueprint is not None:
            for gx,gy in self.world.connected_relays():
                cx,cy=self.point((gx+.5,gy+.5))
                rr=5*TILE*self.camera.zoom
                self.oval(cx-rr,cy-rr,2*rr,2*rr,'','#aecba1',.8)

    def terrain(self):
        w = self.world
        level = w.level
        self.canvas.set_layer('terrain')
        self.rect(LEFT,TOP,VIEW_W,VIEW_H,'#59786e')
        x,y = self.point((0,0))
        unit = TILE*self.camera.zoom
        self.rect(x,y,NX*unit,NY*unit,level.ground)
        # Overlapping soft organic patches, no checkerboard or baked scenery.
        for gx,gy,seed,phase in self.decor[::4]:
            if not self.visible((gx,gy),1):
                continue
            px,py = self.point((gx,gy))
            radius=(17+seed*34)*self.camera.zoom
            self.oval(px-radius,py-radius*.5,radius*2,radius,tint(level.ground,level.ground_dark,.18+seed*.2))
        self.draw_approaches()
        self.draw_core_ring()
        for gx,gy,seed,phase in self.decor:
            if not self.visible((gx,gy),.5) or (int(gx),int(gy)) in w.terrain:
                continue
            px,py = self.point((gx,gy))
            z = self.camera.zoom
            if seed<.64:
                sway=math.sin(self.real_time*1.6+phase)*2*z
                c=tint(level.ground_dark,'#577b61',.35)
                self.line([(px-2*z,py+4*z),(px-4*z+sway,py-3*z)],c,.8)
                self.line([(px+1*z,py+4*z),(px+4*z+sway,py-1*z)],c,.8)
                if seed<.09 and level.weather not in ('dust','rain'):
                    self.oval(px-5*z+sway,py-6*z,4*z,4*z,'#f2e6b7')
            else:
                self.oval(px,py,3*z,2*z,tint(level.ground_dark,'#dcc6a4',.5))
        for gx,gy in sorted(w.terrain):
            if not self.visible((gx,gy),1):
                continue
            px,py = self.point((gx+.5,gy+.5))
            z = self.camera.zoom
            if level.terrain_style in ('river','wetland','storm'):
                self.rect(px-unit/2,py-unit/2,unit+1,unit+1,'#71a9b4')
                for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
                    if (gx+dx,gy+dy) not in w.terrain:
                        if dx:
                            self.rect(px+(-unit/2 if dx<0 else unit/2-3*z),py-unit/2,3*z,unit,'#c0c6a3')
                        else:
                            self.rect(px-unit/2,py+(-unit/2 if dy<0 else unit/2-3*z),unit,3*z,'#c0c6a3')
                drift=math.sin(self.real_time*1.7+gx+gy)*3*z
                self.line([(px-12*z+drift,py),(px+3*z+drift,py),(px+10*z+drift,py-2*z)],'#acd5d4',.9)
            elif level.terrain_style=='grove':
                self.oval(px-25*z,py+3*z,56*z,25*z,'#739772')
                self.roundrect(px-5*z,py-19*z,10*z,39*z,'#8e805d',r=3*z)
                sway=math.sin(self.real_time+gx)*1.4*z
                for dx,dy,r,c in ((0,-21,25,'#587e64'),(-11,-30,20,'#6d946e'),(10,-31,21,'#7da374'),(0,-43,18,'#91b77d')):
                    self.oval(px+(dx-r)*z+sway,py+(dy-r)*z,r*2*z,r*2*z,c)
            else:
                rock='#82957e' if level.difficulty=='Easy' else '#a08d73' if level.weather=='dust' else '#839894'
                self.oval(px-23*z,py+4*z,51*z,24*z,tint(level.ground_dark,'#546f61',.25))
                points=[(px-23*z,py+11*z),(px-16*z,py-12*z),(px-4*z,py-23*z),
                        (px+17*z,py-14*z),(px+24*z,py+10*z),(px+9*z,py+19*z),(px-12*z,py+18*z)]
                self.polygon(points,rock,'',1,True)
                self.polygon([points[1],points[2],points[3],(px+1*z,py-1*z)],tint(rock,'#f2e3bc',.35),'',1,True)
                self.polygon([points[3],points[4],points[5],(px+1*z,py-1*z)],tint(rock,'#445d55',.28),'',1,True)
                self.line([(px-12*z,py+8*z),(px-1*z,py+4*z),(px+7*z,py+9*z)],tint(rock,'#364f46',.25),1)
        for key,data in w.deposits.items():
            if self.visible((key[0]+.5,key[1]+.5)):
                self.draw_deposit(key,data)
        for gx,gy in w.spawns:
            if self.visible((gx+.5,gy+.5)):
                px,py=self.point((gx+.5,gy+.5))
                self.oval(px-19*self.camera.zoom,py-11*self.camera.zoom,38*self.camera.zoom,23*self.camera.zoom,'#766d51','#baa879',1)
                self.oval(px-12*self.camera.zoom,py-7*self.camera.zoom,24*self.camera.zoom,14*self.camera.zoom,'#4a5d47')

    def actors(self):
        self.canvas.set_layer('actors')
        objects=[(self.world.corepos[1],0,None),(self.world.player.y,1,None)]
        for b in self.world.buildings.values():
            if self.visible(b.pos):
                objects.append((b.y+.5,2,b))
        for e in self.world.enemies:
            if self.visible(e.pos,2):
                objects.append((e.y+(50 if e.flying else 0),3,e))
        for _,kind,obj in sorted(objects,key=lambda item:item[0]):
            if kind==0:
                self.draw_core()
            elif kind==1:
                self.draw_player()
            elif kind==2:
                key=(obj.x,obj.y)
                if isinstance(obj,Foundation):
                    order=self.world.orders.get(key)
                    if order:
                        self.draw_foundation(obj,order)
                else:
                    self.draw_robot(obj,*self.point(obj.pos),self.camera.zoom)
                    if key in self.world.orders:
                        order=self.world.orders[key]
                        x,y=self.point(obj.pos)
                        self.roundrect(x-22,y+29,44,4,'#536e6b',r=1)
                        self.roundrect(x-22,y+29,max(.2,44*order.fraction),4,'#eacb88',r=1)
                    if obj.hp<obj.stats()['hp']:
                        x,y=self.point(obj.pos)
                        self.roundrect(x-18,y-36*self.camera.zoom,36,3,'#6e7461',r=1)
                        self.roundrect(x-18,y-36*self.camera.zoom,max(.2,36*obj.hp/obj.stats()['hp']),3,'#b3e5b5',r=1)
            else:
                self.draw_bug(obj,*self.point(obj.pos),self.camera.zoom*1.1)

    def effects(self):
        self.canvas.set_layer('effects')
        for projectile in self.world.projectiles:
            if projectile['age']<0:
                continue
            pos=(projectile['x'],projectile['y'])
            if not self.visible(pos):
                continue
            x,y=self.point(pos)
            dx,dy=projectile['dest'][0]-pos[0],projectile['dest'][1]-pos[1]
            a=math.atan2(dy,dx)
            if projectile['role']=='mortar':
                total=max(.1,distance(projectile['origin'],projectile['dest']))
                progress=min(1,distance(projectile['origin'],pos)/total)
                self.oval(x-4,y-2,8,4,'#779075')
                y-=math.sin(progress*math.pi)*65*self.camera.zoom
            self.line([(x-math.cos(a)*12*self.camera.zoom,y-math.sin(a)*12*self.camera.zoom),(x,y)],'#ffe4a4',2)
            self.oval(x-2,y-2,4,4,'#fff5cd')
        for effect in self.world.effects[-180 if self.quality else -60:]:
            if self.visible(effect['pos'],3):
                adjusted=dict(effect)
                adjusted['size']*=self.camera.zoom
                self.draw_effect(adjusted)
        for hazard in self.world.hazards:
            if self.visible(hazard['pos']):
                x,y=self.point(hazard['pos'])
                r=hazard['radius']*TILE*self.camera.zoom
                self.oval(x-r,y-r*.6,r*2,r*1.2,'','#cadc8a' if hazard.get('enemy') else '#ecc28b',1.5)
        if self.quality:
            for i in range(18):
                xx=LEFT+(i*67+self.real_time*(13 if self.world.level.weather=='rain' else 3))%VIEW_W
                yy=TOP+(i*83+self.real_time*(190 if self.world.level.weather=='rain' else -5))%VIEW_H
                if self.world.level.weather=='rain':
                    self.line([(xx,yy),(xx-4,yy+13)],'#b7d2cd',.6)
                else:
                    self.oval(xx,yy,1.8,1.8,'#e4e9bd')
        if self.blueprint is not None:
            self.blueprint_preview()

    def blueprint_preview(self):
        gx,gy=self.world.blueprint_tile()
        if not(0<=gx<NX and 0<=gy<NY):
            return
        x,y=self.point((gx+.5,gy+.5))
        z=self.camera.zoom
        error=self.world.site_error(gx,gy,self.blueprint)
        color='#efad98' if error else '#f0f9bc'
        self.roundrect(x-20*z,y-18*z,40*z,36*z,'',color,r=5*z,width=1.6)
        phase=(self.real_time*1.5)%1
        for side in (-1,1):
            self.line([(x+side*17*z,y+10*z),(x+side*17*z,y-16*z-phase*6*z)],color,1)
        self.text(x,y-37*z,'F  BUILD HERE' if not error else 'KEEP TRAIL CLEAR' if 'Enemy trail' in error else 'CANNOT BUILD',8,color,True,anchor='center')

    def masks(self):
        self.canvas.set_layer('masks')
        self.rect(0,0,WIDTH,TOP-5,'#122d3d')
        self.rect(0,TOP-5,LEFT-5,HEIGHT,'#122d3d')
        self.rect(LEFT+VIEW_W+5,TOP-5,WIDTH,HEIGHT,'#122d3d')
        self.rect(0,TOP+VIEW_H+5,WIDTH,HEIGHT,'#122d3d')

    def header(self):
        w=self.world
        self.canvas.set_layer('hud')
        self.gradient(0,0,WIDTH,88,'#2d6e98','#17496b',14)
        self.text(22,12,'PROJECT-SWARMFALL',17,'#f1edce',True)
        self.text(24,46,f'LEVEL {w.level_id+1}  •  {w.level.name}',11,'#bdd3c6',True)
        items=[('$',f'{w.money:,}','#f3d590'),('M',str(w.materials['metal']),'#c7dadc'),
               ('C',str(w.materials['circuits']),'#e4bb85'),('◆',str(w.materials['crystal']),'#c6b3ed')]
        labels=('Dollars','Metal','Parts','Crystals')
        for i,(icon,value,color) in enumerate(items):
            xx=324+i*126
            self.roundrect(xx,13,117,59,'#24567b','#5f99b9',r=13)
            self.oval(xx+9,26,27,27,tint('#36504d',color,.35),color,.8)
            self.polygon([(xx+22,32),(xx+29,40),(xx+22,48),(xx+15,40)],color) if icon=='◆' else self.text(xx+22,40,icon,12,color,True,anchor='center')
            self.text(xx+45,22,value,17,color,True)
            self.text(xx+45,49,labels[i],8,'#adc5bf')
        self.text(846,14,'Core health',10,'#c3d7c7',True)
        self.roundrect(846,37,198,12,'#4b6255',r=5)
        self.roundrect(846,37,max(.1,198*w.corehp/w.coremax),12,'#bcdca3',r=5)
        self.text(846,56,f'{int(w.corehp):,} / {w.coremax:,}',8,'#a9c8bd')
        self.roundrect(1066,13,187,59,'#284a48','#72977d',r=13)
        self.text(1081,22,f'Wave {w.wave} / 40' if w.active else f'Next: wave {min(40,w.wave+1)}',17,'#ece3ba',True)
        seconds=max(0,math.ceil(w.intermission))
        status='Defend the core!' if w.active else 'Tutorial: timer paused' if w.tutorial and w.tutorial_step<7 else ('Supplies ready • ' if w.supply_pending is not None else 'Starts in ')+f'{seconds//60}:{seconds%60:02d}'
        self.text(1081,51,status,8,'#b9d2bd')
        self.button(1280,23,138,37,'Pause  [P]',('pause',),size=11)


    def sidebar(self):
        x=PANEL_X
        self.roundrect(x-2,TOP-1,288,VIEW_H+2,'#245d83','#75acc8',r=13)
        self.text(x+13,111,'Build your defense',16,'#ece5c5',True)
        self.text(x+13,140,'Pick a blueprint. Build it in the field.',8,'#b0c9c2')
        self.button(x+10,162,127,30,'Robots',('category','robots'),accent='#c5dda5' if self.category=='robots' else None,size=10)
        self.button(x+146,162,127,30,'Buildings',('category','structures'),accent='#c5dda5' if self.category=='structures' else None,size=10)
        page=getattr(self,'blueprint_page',0)
        indices=range(page*4,page*4+4) if self.category=='robots' else range(12,len(SPECS))
        for row,index in enumerate(indices):
            spec=SPECS[index]
            by=204+row*(66 if self.category=='robots' else 54)
            height=59 if self.category=='robots' else 48
            active=self.blueprint==index
            self.button(x+10,by,263,height,'',('blueprint',index),accent=spec['color'] if active else None)
            b=Building(0,0,index)
            b.angle=-.4
            self.draw_robot(b,x+34,by+height*.57,.65 if index<12 else .54)
            self.text(x+60,by+9,spec['name'],11,'#e9eedc',True,width=197)
            enough=self.world.money>=spec['price'] and all(self.world.materials[r]>=spec.get(r,0) for r in self.world.materials)
            self.text(x+60,by+32,f'${spec["price"]}  ·  '+('Ready to build' if enough else 'Need supplies'),8,'#bfd5b0' if enough else '#d9bb91')
        if self.category=='robots':
            for i in range(3):
                self.button(x+10+i*89,473,82,25,f'{i*4+1}–{i*4+4}',('shop_page',i),accent='#d7cd99' if i==page else None,size=8)
        y=517
        if self.blueprint is not None:
            spec=SPECS[self.blueprint]
            subtitle,description=DESCRIPTIONS[spec['role']]
            self.text(x+13,y,spec['name'],16,spec['color'],True,width=253)
            self.text(x+13,y+34,subtitle,10,'#ddd5ad',True,width=251)
            self.text(x+13,y+60,description,10,'#bed1ca',width=250)
            self.line([(x+13,y+138),(x+268,y+138)],'#52716e',1)
            self.text(x+13,y+153,f'${spec["price"]}   •   {spec["metal"]} Metal',12,'#eed297',True)
            self.text(x+13,y+182,f'{spec["circuits"]} Parts   •   {spec.get("crystal",0)} Crystals',10,'#c0cfc6')
            duration=2.5 if spec['role']=='wall' else 3 if spec['role']=='gate' else 5 if self.blueprint<12 else 4
            self.text(x+13,y+211,f'{duration:g}s to build  ·  Hold E at the site',9,'#b9d8b4')
            self.roundrect(x+11,y+244,264,42,'#35584f','#b0c59d',r=9)
            self.text(x+23,y+256,'F  Set site in front of you',10,'#e7e9c9',True)
        else:
            self.text(x+13,y+10,'Your camp. Your plan.',16,'#e7dfba',True)
            self.text(x+13,y+57,'Choose a robot above to see what it does. Build beside the enemy trails, never on them.',12,'#bfd2cb',width=252)
            self.text(x+13,y+158,'The bright ring marks the core building area. Bugs leave the trails when they enter it.',11,'#bdd2c2',width=249)
            self.text(x+13,y+247,'Walk to robots and press E to upgrade.',10,'#e6d8a9',width=249)
        supply,used=self.world.power()
        self.text(x+13,827,f'Power {used}/{supply}  •  Walls {self.world.barrier_count()}/{self.world.barrier_limit}',8,'#e3bb8c' if used>supply else '#adc8bd')


    def action_bar(self):
        w=self.world
        self.roundrect(18,859,1100,65,'#245d80','#81b4c6',r=13,width=1.5)
        context=w.local_context()
        primary='WASD  Move    SHIFT  Run    E  Interact'
        secondary='Mine materials, build robots, and protect the core.'
        progress=None;mining=False
        if context:
            kind,key=context
            if kind=='deposit':
                resource,remaining=w.deposits[key]
                duration=w.mining_duration(resource,key)
                primary=('Tool overheated! Release E to cool.' if w.overheated else f'Hold E to mine {RESOURCE_NAMES[resource]}')
                secondary=f'{remaining} left  •  {duration:.1f}s per chunk  •  '+('Good hit! Finish this chunk.' if w.precision_used else 'Space in the green = bonus materials')
                progress=w.mine_progress/duration;mining=True
            elif kind=='order':
                order=w.orders[key]
                primary=f'Hold E to {"build" if order.task=="build" else "install" if order.task=="upgrade" else "repair"}: {order.name}'
                secondary=f'{max(0,order.duration-order.progress):.1f}s left. Stay nearby to work.'
                progress=order.fraction
            elif kind=='robot':
                b=w.buildings[key];primary=f'E  {b.spec["name"]}'
                secondary='Upgrades, repairs and selling. The battle keeps going.'
            elif kind=='core':
                primary='E  Core'
                secondary='Pick up supplies, upgrade your drill, or check the next wave.'
                if w.supply_pending is not None:secondary='Supply pack ready! Press E and pick one.'
        self.text(35,870,primary,12,'#fff1c9',True,width=771)
        self.text(35,894,secondary,9,'#c1e0e7',width=775)
        if progress is not None:
            bx,by,bw=36,915,750
            self.roundrect(bx,by,bw,4,'#17455f',r=1)
            if mining:
                self.rect(bx+bw*.52,by-1,bw*.26,6,'#668a92' if w.precision_used else '#9bdb83')
                marker=bx+bw*min(1,max(0,progress))
                self.rect(marker-2,by-3,4,10,'#fff6c5')
            else:self.roundrect(bx,by,max(.1,bw*min(1,progress)),4,'#f2d372',r=1)
        heat_color='#f5a36f' if w.tool_heat>.75 else '#f1d06f' if w.tool_heat>.4 else '#90d7da'
        self.text(839,871,'TOOL HEAT' if not w.overheated else 'COOLING DOWN',8,heat_color,True)
        self.text(1095,871,f'{round(w.tool_heat*100)}%',9,heat_color,True,anchor='ne')
        self.roundrect(839,892,258,11,'#153f59',r=5)
        self.roundrect(839,892,max(.1,258*w.tool_heat),11,heat_color,r=5)
        self.text(839,910,f'Drill {w.drill_level}/3  •  Release E to cool',7,'#b5d4df')
        self.button(1136,860,138,63,'Help  [H]',('help',),size=11)
        self.button(1285,860,138,63,'Pause  [P]',('pause',),size=11)


    def tutorial_card(self):
        w=self.world
        if not w.tutorial or w.tutorial_complete:
            return
        title,description=TUTORIAL_STEPS[w.tutorial_step]
        self.roundrect(34,111,431,110,'#264a50','#d0dba8',r=12)
        self.text(50,124,f'TUTORIAL  {w.tutorial_step+1} / {len(TUTORIAL_STEPS)}',8,'#bfdfb4',True)
        self.text(50,145,title,15,'#f1e9c6',True)
        self.text(50,176,description,10,'#d1e0d5',width=396)
        if w.tutorial_step==1:
            target=(12.5,14.5)
        elif w.tutorial_step in (5,6):
            robots=[b for b in w.buildings.values() if b.kind<12 and not isinstance(b,Foundation)]
            target=robots[0].pos if robots else w.player.pos
        elif w.tutorial_step==7:
            target=w.corepos
        else:
            target=None
        if target:
            x,y=self.point(target)
            bob=math.sin(self.real_time*3)*4
            self.text(x,y-52+bob,'▼',19,'#fff0b8',True,anchor='center')

    def notices(self):
        notices=self.world.feedback[-2:]
        for i,notice in enumerate(reversed(notices)):
            progress=min(ease(notice['age']/.25),ease(notice['life']/.3))
            x=LEFT+VIEW_W-335+(1-progress)*70
            y=TOP+16+i*72
            self.roundrect(x,y,317,62,'#26484f',notice['color'],r=10)
            self.text(x+13,y+10,notice['title'],10,notice['color'],True,width=290)
            self.text(x+13,y+32,notice['body'],8,'#bfd7ce',width=290)
        if self.world.message_time and self.world.message:
            self.text(37,TOP+VIEW_H-20,self.world.message,9,'#2f5652',True,width=1040)

    def radar(self):
        x,y=LEFT+16,TOP+VIEW_H-123
        self.roundrect(x,y,147,99,'#33554f','#a2bc9f',r=7)
        for gx,gy in self.world.terrain:
            self.rect(x+9+gx*4.6,y+9+gy*3.5,4.6,3.5,'#738f79')
        for e in self.world.enemies:
            self.oval(x+9+e.x*4.6,y+9+e.y*3.5,2.5,2.5,'#f2bb96')
        self.oval(x+9+self.world.corepos[0]*4.6-2,y+9+self.world.corepos[1]*3.5-2,4,4,'#e9eab3')
        p=self.world.player
        self.oval(x+9+p.x*4.6-2,y+9+p.y*3.5-2,4,4,'#fcdf89')
        self.text(x+11,y+86,'YOU  ●   CORE  ●',6,'#d9e3c6')

    def scrim(self):
        self.canvas.create_rectangle(0,0,WIDTH,HEIGHT,fill='#0b2532',outline='',stipple='gray50')
        self.buttons=[]

    def robot_panel(self,key):
        b=self.world.buildings.get(key)
        if not b or distance(self.world.player.pos,b.pos)>1.75:
            self.panel=None
            return
        self.scrim()
        x,y=300,88
        self.roundrect(x+7,y+9,840,762,'#122d34',r=22)
        self.roundrect(x,y,840,762,'#245d83','#74adc6',r=22)
        self.text(x+28,y+23,b.spec['name']+' upgrades',25,b.spec['color'],True)
        self.text(x+28,y+65,'Choose an upgrade, then hold E beside your robot to install it.',11,'#c6d8c9')
        self.button(x+704,y+24,110,33,'Back [Esc]',('close',),size=9)
        if b.kind<12:
            if max(b.paths)>=2:
                main=0 if b.paths[0]>=2 else 1
                guide=f'Main path: {b.spec["paths"][main][0]}. The other side can only take its first upgrade.'
            else:
                guide='Pick one main path. You may still buy the first upgrade on BOTH sides.'
            self.roundrect(x+28,y+104,784,45,'#3a7392','#91b6ba',r=10)
            self.text(x+43,y+119,guide,10,'#eadfb7',width=753)
            for path,(name,upgrades) in enumerate(b.spec['paths']):
                xx=x+28+path*400
                color='#edd08e' if path==0 else '#b8d7de'
                self.text(xx,y+170,name,15,color,True)
                for tier in range(3):
                    self.oval(xx+278+tier*27,y+173,13,13,color if b.paths[path]>tier else '#496b65',color,.7)
                for tier,u in enumerate(upgrades):
                    yy=y+206+tier*128
                    bought=b.paths[path]>tier
                    next_tier=b.paths[path]==tier
                    locked=b.paths[1-path]>=2 and tier>=1
                    self.roundrect(xx,yy,384,120,'#2d7099','#b8da8b' if bought else '#5795b5',r=10)
                    self.text(xx+12,yy+10,f'{tier+1}. {u["name"]}',11,'#cee0b9' if bought else '#eef0d8',True,width=357)
                    description=plain_upgrade(u)
                    self.text(xx+12,yy+35,description,9,'#bfd4ca',width=357)
                    if next_tier and not locked and len(description)<112:
                        self.text(xx+12,yy+67,upgrade_comparison(b,path),8,'#e0d6ae',width=355)
                    if bought:label='Installed'
                    elif locked:label='Other path is limited to upgrade 1'
                    elif not next_tier:label=f'Get upgrade {tier} first'
                    elif self.world.money<u['price']:label=f'Need ${u["price"]-self.world.money} more'
                    else:label=f'Prepare upgrade  ·  ${u["price"]}'
                    self.button(xx+10,yy+91,363,24,label,('upgrade',key,path),enabled=next_tier and not locked and self.world.money>=u['price'] and key not in self.world.orders,accent=color if next_tier and not locked else None,size=9)
        else:
            subtitle,description=DESCRIPTIONS[b.role]
            self.text(x+28,y+131,subtitle,19,'#e5d7ab',True)
            self.text(x+28,y+180,description,15,'#c2d6ca',width=772)
            if b.role=='gate':
                self.button(x+28,y+286,784,48,'Close gate' if b.opened else 'Open gate',('gate',key),accent='#d7c28f')
            self.text(x+28,y+403,'Your engineer does the work here in the camp.\nRobots do the fighting.',16,'#bfd4c8')
        missing=b.stats()['hp']-b.hp
        cost,metal=math.ceil(missing*.08),math.ceil(missing*.02)
        self.text(x+28,y+615,f'Health {int(b.hp)} / {int(b.stats()["hp"])}  ·  Uses {b.spec["power"]} power',11,'#c4d5c5')
        self.button(x+28,y+652,383,44,f'Repair  ·  ${cost} + {metal} Metal',('repair',key),enabled=missing>=1 and key not in self.world.orders,size=11)
        self.button(x+429,y+652,383,44,f'Sell  ·  +${int(b.invested*.7)}',('sell',key),enabled=key not in self.world.orders,size=11)
        self.text(x+28,y+723,'The battle continues. Choose, then hold E beside the robot to install.',10,'#9cbdb5')


    def core_panel(self):
        w=self.world
        if distance(w.player.pos,w.corepos)>1.95:
            self.panel=None;return
        self.scrim()
        x,y=360,91
        self.roundrect(x+7,y+9,720,758,'#12334e',r=24)
        self.roundrect(x,y,720,758,'#24658d','#79bed8',r=24,width=2)
        self.text(x+29,y+23,'Core & Supplies',28,'#fff0c0',True)
        self.text(x+30,y+76,f'Health {int(w.corehp):,} / {w.coremax:,}',12,'#d2e8dc',True)
        self.button(x+568,y+29,124,34,'Back [Esc]',('close',),size=10)
        self.roundrect(x+28,y+112,664,121,'#174d74','#6fa9bd',r=15)
        if w.active:
            self.text(x+46,y+128,f'Wave {w.wave} / 40',24,'#fff2c6',True)
            self.text(x+46,y+175,f'{len(w.enemies)} bugs fighting  •  {len(w.queue)} still coming',12,'#c0dce6')
        else:
            seconds=max(0,math.ceil(w.intermission))
            clock=f'{seconds//60}:{seconds%60:02d}'
            self.text(x+46,y+127,f'Wave {w.wave+1} in {clock}',25,'#fff1b8',True)
            self.text(x+46,y+174,'Timer starts after the first tutorial steps.' if w.tutorial and w.tutorial_step<7 else 'Waves start automatically. Use this time to mine and build.',11,'#c5e1e9')
        self.text(x+30,y+258,'Choose supplies' if w.supply_pending is not None else 'Next supply drop',18,'#ffe4a1',True)
        if w.supply_pending is not None:
            choices=(('materials','Materials','48 Metal + 16 Parts + 3 Crystals'),
                     ('repair','Repairs','900 core health + 35% building repairs'),
                     ('money','Dollars',f'${250+w.wave*10} for robots and upgrades'))
            for i,(choice,title,description) in enumerate(choices):
                yy=y+300+i*73
                self.button(x+28,yy,664,62,'',('supply',choice),accent='#d8df8a')
                self.text(x+45,yy+10,title,14,'#fff3c4',True)
                self.text(x+45,yy+36,description,10,'#d5e6cc')
            self.text(x+31,y+528,'Pick one before the next wave starts.',9,'#c6dce3')
        else:
            next_drop=(w.wave//5+1)*5
            self.text(x+30,y+300,f'Supplies arrive after wave {min(40,next_drop)}.',14,'#d0e3e4')
            self.text(x+30,y+339,'Every fifth wave gives you a one-minute break and a choice of supplies.',12,'#bddce6',width=655)
            self.text(x+30,y+399,'Keep the core untouched for a bonus.\nMore trails open as the waves get harder.',12,'#e1dfba')
        rank=w.drill_level+1
        if w.drill_level<3:
            money,metal,parts=220*rank,20*rank,8*rank
            enabled=w.money>=money and w.materials['metal']>=metal and w.materials['circuits']>=parts
            self.button(x+28,y+567,664,54,f'Upgrade drill to {rank}  •  ${money} + {metal} Metal + {parts} Parts',('drill',),enabled=enabled,accent='#9ad7dc',size=11)
            self.text(x+31,y+637,'Each drill upgrade improves mining speed and cooling.',10,'#c3dde5')
        else:self.text(x+31,y+592,'Drill fully upgraded!',17,'#c7e8a8',True)
        self.button(x+28,y+679,664,49,'Back to the field',('close',),size=14)


    def help_panel(self):
        self.scrim()
        self.roundrect(320,111,800,718,'#1c3c49','#8eb5b7',r=20)
        self.text(354,142,'FIELD ENGINEER GUIDE',27,'#efdfb7',True)
        sections=(
            ('MOVE / WASD','Walk your engineer around the world. Hold Shift to run. Scroll to zoom. There are no remote building controls.'),
            ('MINE / HOLD E','Hold E beside a deposit. Release E to cool your tool. Press Space while the marker is green for extra materials.'),
            ('BUILD / F, THEN HOLD E','Choose a sidebar blueprint. Face a nearby green tile and press F. Hold E beside the site to construct it. Work pauses when you leave.'),
            ('UPGRADE / WALK UP AND PRESS E','Stand beside a robot and press E. Choose a path upgrade, close the panel, and hold E beside the robot to install it.'),
            ('DEFEND THE CORE','Robots fight automatically. Bugs still damage structures and the core. Touching a bug knocks your engineer back; you have no attack.'),
            ('WAVES / USE THE CORE','Waves start automatically: 60 seconds before wave 1, then 15-second breaks. Every fifth wave gives a minute and supplies.'),
        )
        for i,(title,description) in enumerate(sections):
            yy=207+i*82
            self.text(354,yy,title,11,'#c2dfb5',True)
            self.text(354,yy+24,description,11,'#bed4d2',width=725)
        self.button(354,747,732,45,'BACK',('close',),size=12)

    def pause_panel(self):
        self.scrim()
        self.roundrect(470,205,500,520,'#1b3d49','#91b7b6',r=22)
        self.text(505,244,'PAUSED',34,'#ead7a7',True)
        self.text(506,300,f'{self.world.level.name} / Wave {self.world.wave}',13,'#b6d0cd')
        self.button(505,354,430,49,'Resume game',('resume',),accent='#b7dda9',size=13)
        self.button(505,420,430,42,'ANIMATION DETAIL: '+('FULL' if self.quality else 'REDUCED'),('quality',),size=10)
        self.button(505,478,430,42,'Restart level',('start',self.world.level_id,False),size=11)
        self.button(505,536,430,42,'Choose a level',('levels',),size=11)
        self.button(505,594,430,42,'Main menu',('title',),size=11)
        self.text(506,676,'WASD movement  •  E work / interact  •  F construction',9,'#98bdc1')

    def outcome_panel(self):
        self.scrim()
        won=self.world.outcome=='won'
        if won:
            self.completed.add(self.world.level_id)
        self.roundrect(400,194,640,545,'#1b3d49','#b3c99f' if won else '#c99d88',r=20)
        self.text(437,231,'CORE PROTECTED' if won else 'CORE LOST',31,'#d9e8bd' if won else '#e9b39a',True)
        self.text(438,293,self.world.level.name,18,'#d9ddd0',True)
        self.text(438,338,f'Wave {self.world.wave} / 40  •  {self.world.kills} bugs defeated',13,'#b9d2cf')
        self.text(438,380,'Your engineer built the defense. Your robots held the line.' if won else 'Try different robot positions, stronger upgrades, and connected power.',12,'#b5cfcd',width=565)
        if won and self.world.level_id<8:
            self.button(438,460,564,47,'NEXT LEVEL',('start',self.world.level_id+1,False),accent='#bfdca7',size=13)
        else:
            self.button(438,460,564,47,'TRY THIS LEVEL AGAIN',('start',self.world.level_id,False),size=12)
        self.button(438,526,564,43,'CHOOSE A LEVEL',('levels',),size=12)
        self.button(438,586,564,43,'Main menu',('title',),size=12)

    def title_screen(self):
        self.gradient(0,0,WIDTH,HEIGHT,'#244b53','#102c3c',32)
        # All characters in this diorama are the same live articulated rigs as play.
        for i in range(14):
            x=700+(i*139)%740
            y=170+(i*91)%720
            r=35+i%3*16
            self.oval(x-r,y-r*.4,r*2,r*.8,'#355e5c')
        for i,kind in enumerate((0,3,7,9)):
            b=Building(0,0,kind)
            b.angle=math.sin(self.real_time*.6+i)*.4
            b.animation=.1 if math.sin(self.real_time*5+i)>.8 else 0
            self.draw_robot(b,870+(i%2)*330,380+(i//2)*310,2.5)
        for i,name in enumerate(('Ant','Beetle','Wasp','Mantis')):
            e=Enemy(name,1+i,2+i,1)
            e.angle=math.pi+.2*math.sin(self.real_time*.5+i)
            self.draw_bug(e,1020+(i%2)*290+math.sin(self.real_time*.7+i)*20,200+(i//2)*340,2.6)
        for i in range(27):
            px=670+(i*73+self.real_time*5)%770
            py=(i*111-self.real_time*8)%HEIGHT
            self.oval(px,py,2,2,'#b6d2b2')
        self.rect(0,0,630,HEIGHT,'#143342')
        for i in range(10):
            self.rect(630+i*5,0,6,HEIGHT,tint('#143342','#244b53',i/20))
        self.text(62,106,'PROJECT-',34,'#a9cbc9',True)
        self.text(57,157,'SWARMFALL',58,'#eff0d1',True)
        self.line([(64,255),(395,255)],'#e1c58e',3)
        self.text(64,292,'BUILD A BASE. STOP THE SWARM.',18,'#e9cf98',True)
        self.text(64,342,'Mine, build and upgrade.\nKeep the core safe.',19,'#b4d0cf')
        self.button(64,470,467,76,'Play',('levels',),accent='#b9e67d',size=24)
        self.text(67,577,'Choose a level to get started.',13,'#b9d8df')
        self.text(66,649,'3 EASY  /  3 MEDIUM  /  3 HARD',12,'#c3d6c4',True)
        self.text(66,697,'You gather and build.\nYour robots do the fighting.',13,'#a6c7c9')
        self.text(66,842,'12 robots  •  72 upgrades  •  40 waves per level',11,'#88b4bb')

    def level_screen(self):
        self.gradient(0,0,WIDTH,HEIGHT,'#254d56','#112d3e',24)
        self.text(62,43,'Choose a level',30,'#eee8c9',True)
        self.text(64,94,'Survive 40 waves and protect your core.',13,'#aecdcf')
        groups=('Easy','Medium','Hard')
        for column,group in enumerate(groups):
            xx=63+column*448
            color=('#bbdda6','#ebce94','#e6b097')[column]
            self.text(xx,151,group.upper(),19,color,True)
            for row in range(3):
                index=column*3+row
                level=LEVELS[index]
                yy=197+row*217
                self.roundrect(xx,yy,418,195,'#1d3f4c','#456c73',r=13)
                self.rect(xx+15,yy+15,7,43,level.ground)
                self.text(xx+35,yy+19,f'{index+1}. {level.name}',19,'#e6e9d4',True)
                self.text(xx+20,yy+69,level.description,11,'#b1cdcd',width=377)
                label='PLAY AGAIN' if index in self.completed else 'DEPLOY ENGINEER'
                self.button(xx+20,yy+136,378,40,label,('start',index,False),accent=color,size=11)
        self.button(63,874,248,40,'BACK TO TITLE',('title',),size=11)
        self.button(328,874,330,40,'Tutorial',('start',0,True),size=11)

    def transition_screen(self):
        if not self.transition:
            return
        t=self.transition['age']
        fraction=ease(t/.36) if t<.36 else 1-ease((t-.36)/.4)
        width=WIDTH*.5*fraction+2
        self.rect(0,0,width,HEIGHT,'#102c3b')
        self.rect(WIDTH-width,0,width,HEIGHT,'#102c3b')
        self.line([(width,0),(width,HEIGHT)],'#a6d0ba',2)
        self.line([(WIDTH-width,0),(WIDTH-width,HEIGHT)],'#a6d0ba',2)
        if fraction>.94:
            self.text(WIDTH/2,HEIGHT/2,TITLE,23,'#e7e7c9',True,anchor='center')

    def frame(self):
        if self.closed:
            return
        start=time.perf_counter()
        dt=min(.08,start-self.last)
        self.last=start
        self.real_time+=dt
        if self.transition:
            self.transition['age']+=dt
            if self.transition['age']>=.36 and not self.transition['switched']:
                self.transition['switched']=True
                action=self.transition['action']
                if action[0]=='start':
                    self.new_level(action[1],action[2])
                else:
                    self.state='title'
                    self.panel=None
                    self.paused=False
            if self.transition['age']>=.76:
                self.transition=None
        running=self.state=='play' and not self.paused and not (self.panel and self.panel[0]=='help') and not self.world.outcome and not self.transition
        if running:
            self.accumulator+=dt
            axis=(0,0) if self.panel else (int('d' in self.keys)-int('a' in self.keys),int('s' in self.keys)-int('w' in self.keys))
            steps=0
            while self.accumulator>=1/60 and steps<6:
                self.world.update_field(1/60,axis,not self.panel and 'e' in self.keys,not self.panel and ('shift_l' in self.keys or 'shift_r' in self.keys))
                self.accumulator-=1/60
                steps+=1
            if steps==6:
                self.accumulator=min(self.accumulator,1/60)
        else:
            self.accumulator=0
        self.camera.follow(self.world.player.pos,dt)
        cw,ch=max(1,self.canvas.winfo_width()),max(1,self.canvas.winfo_height())
        self.scale=min(cw/WIDTH,ch/HEIGHT)
        self.offset=((cw-WIDTH*self.scale)/2,(ch-HEIGHT*self.scale)/2)
        self.canvas.begin()
        self.buttons=[]
        if self.state=='title':
            self.canvas.set_layer('hud')
            self.title_screen()
        elif self.state=='levels':
            self.canvas.set_layer('hud')
            self.level_screen()
        else:
            ui_clock=self.real_time
            self.real_time=self.world.elapsed
            self.terrain()
            self.actors()
            self.effects()
            self.real_time=ui_clock
            self.masks()
            self.canvas.set_layer('hud')
            self.header()
            self.sidebar()
            self.action_bar()
            self.radar()
            self.tutorial_card()
            self.notices()
            if self.paused or self.panel or self.world.outcome:
                self.canvas.set_layer('modal')
                if self.world.outcome:
                    self.outcome_panel()
                elif self.paused:
                    self.pause_panel()
                elif self.panel[0]=='robot':
                    self.robot_panel(self.panel[1])
                elif self.panel[0]=='core':
                    self.core_panel()
                else:
                    self.help_panel()
        self.canvas.set_layer('transition')
        self.transition_screen()
        self.canvas.end()
        elapsed=time.perf_counter()-start
        self.root.after(max(1,round((1/60-elapsed)*1000)),self.frame)


if __name__ == '__main__':
    EngineerGame().run()
