import numpy as np
import math

from simple_environment import Environment

def observation_vector(observation):
    return np.array(
        list(observation['pod'][0]) +
        [observation['pod'][1]] +
        list(observation['checkpoint']) +
        list(observation['next_checkpoint'])
    ) / np.array([500, 500, math.pi, 10000, math.pi, 10000, math.pi])


class SimpleControl:
    def __init__(self, alpha, beta):
        self.alpha = alpha
        self.beta = beta

    def control(self, obs):
        checkpoint_angle = obs['checkpoint'][1]
        distance_to_checkpoint = obs['checkpoint'][0]
        next_checkpoint_angle = obs['next_checkpoint'][1]
        current_angle = obs['pod'][1]
        goto_next_checkpoint = distance_to_checkpoint < self.beta
        if goto_next_checkpoint:
            rotation = next_checkpoint_angle - current_angle
        else:
            rotation = checkpoint_angle - current_angle

        control = {
            'thrust': 100,
            'rotation': (
                rotation
            ),
        }
        return control


def estimate_reward(episodes_count, model):
    env = Environment()
    episode_rewards = []
    total_steps = []
    for i in range(episodes_count):
        obs = env.reset(i)

        done = False
        total_reward = 0
        observations = []
        steps = 0
        while not done:
            control = model.control(obs)
            obs, reward, done, _ = env.step(control)
            v = observation_vector(obs)
            observations.append(v)
            total_reward += reward
            steps += 1
        #print i, total_reward
        episode_rewards.append(total_reward)
        total_steps.append(steps)

    return np.mean(total_steps)


if __name__ == '__main__':
    with open('optimization.log', 'w') as out_file:
        for beta in np.linspace(600, 2500, 20): #[::-1]:
            for alpha in [1.0]: # np.linspace(0.05, 1, 20)[::-1]:
                steps = estimate_reward(20, model = SimpleControl(alpha, beta))
                print >>out_file, alpha, beta, steps
                print alpha, beta, steps

