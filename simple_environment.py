import random
import math
import numpy as np

WIDTH = 16000
HEIGHT = 9000
CHECKPOINT_RADIUS = 600
POD_RADIUS = 400
ROTATION_LIMITS = (-math.pi * 0.1, math.pi * 0.1)
ACCELERATION_LIMITS = (0, 100)
SIMPLE_FRICTION_COEFFICIENT = 0.85


def normalize_angle(angle):
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi

    return angle

class Pod:
    def __init__(self, position, environment):
        self.position = position.copy()
        self.velocity = np.array([0, 0])
        # acceleration vector rotation is inertial
        self.angle = 0
        self.current_checkpoint_index = 1
        self.lap = 0
        self.environment = environment

    def normalize_control(self, control):
        for control_key, limits in [
            ('rotation', ROTATION_LIMITS),
            ('thrust', ACCELERATION_LIMITS),
        ]:
            control[control_key] = np.clip(
                control.get(control_key, 0),
                *limits
            )
        return control

    def rotation(self, rotation):
        self.angle += rotation

    def acceleration(self, thrust):
        acceleration_direction = np.array([
            math.cos(self.angle),
            math.sin(self.angle),
        ])
        acceleration = acceleration_direction * thrust
        self.velocity += acceleration

    def movement(self):
        self.position += self.velocity

    def friction(self):
        self.velocity *= SIMPLE_FRICTION_COEFFICIENT

    def rounding(self):
        self.position = np.around(self.position)
        self.velocity = self.velocity.astype(int)
        self.angle = normalize_angle(self.angle)

    def checkpoint(self):
        if self.environment.checkpoints[self.current_checkpoint_index].passed(self.position):
            self.current_checkpoint_index = self.environment.next_checkpoint_index(
                self.current_checkpoint_index
            )
            self.lap = self.environment.next_lap(self.current_checkpoint_index, self.lap)


    def iteration(self, control):
        control = self.normalize_control(control)

        self.rotation(control['rotation'])
        self.acceleration(control['thrust'])
        self.movement()
        self.friction()
        self.rounding()
        self.checkpoint()

    def observation(self):
        current_checkpoint = self.environment.checkpoints[self.current_checkpoint_index]
        next_checkpoint_index = self.environment.next_checkpoint_index(
            self.current_checkpoint_index
        )
        next_checkpoint = self.environment.checkpoints[next_checkpoint_index]
        observation = {
            'pod' : (
                self.velocity,
                self.angle,
            ),
            'checkpoint' : current_checkpoint.observation(self.position, self.angle),
            'next_checkpoint': next_checkpoint.observation(self.position, self.angle),
        }

        return observation

    def __repr__(self):
        s = 'POS=%s, VEL=%s, A=%.3f' % (
            self.position,
            self.velocity,
            self.angle
        )
        return s


class Checkpoint:
    def __init__(self):
        self.position = np.array([
            random.randint(CHECKPOINT_RADIUS, WIDTH - CHECKPOINT_RADIUS),
            random.randint(CHECKPOINT_RADIUS, HEIGHT - CHECKPOINT_RADIUS),
        ])

    def distance_to(self, position):
        return np.linalg.norm(self.position - position)

    def direction_to(self, position):
        return (self.position - position) / self.distance_to(position)

    def angle_to(self, position):
        direction = self.direction_to(position)
        #print direction
        return math.atan2(direction[1], direction[0])

    def observation(self, position, angle):
        return self.distance_to(position), self.angle_to(position)

    def passed(self, position):
        checkpoint_distance = self.distance_to(position)
        return checkpoint_distance < CHECKPOINT_RADIUS

    def __repr__(self):
        return '%s' % self.position


class Environment:
    """Simple environment for one pod without collisions, shields and boost"""
    def reset(self):
        self.checkpoints = [
            Checkpoint()
            for i in range(random.randint(3, 8))
        ]
        self.pods = [Pod(self.checkpoints[0].position, self)]
        self.laps_count = random.randint(3, 5)
        self.done = False

        return self.pods[0].observation()

    def __init__(self):
        self.checkpoints = []
        self.pods = []
        self.laps_count = 0
        self.done = False
        self.previous_observation = None


    def next_checkpoint_index(self, checkpoint_index):
        assert 0 <= checkpoint_index < len(self.checkpoints)

        next_checkpoint_index = (checkpoint_index + 1) % len(self.checkpoints)
        return next_checkpoint_index

    def next_lap(self, next_checkpoint_index, current_lap):
        lap_finished = next_checkpoint_index == 1
        lap = current_lap + lap_finished
        if lap == self.laps_count:
            self.done = True
        return lap

    def step(self, control):
        "Works with single pod"
        pod = self.pods[0]
        pod.iteration(control)

        observation = pod.observation()
        if self.previous_observation is not None:
            # Positive reward for moving closer to a checkpoint
            reward = self.previous_observation['checkpoint'][0] - observation['checkpoint'][0]

            # TODO
            if reward < -1000:
                reward = self.previous_observation['checkpoint'][0]
        else:
            reward = 0

        self.previous_observation = observation
        # Negative reward for every move spent
        reward -= 10

        return observation, reward, self.done, {}