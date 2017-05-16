from simple_environment import Environment

if __name__ == '__main__':
    env = Environment()
    obs = env.reset()
    print obs
    print env.checkpoints
    for pod in env.pods:
        print pod

    print "START"
    for i in range(100):
        next_checkpoint_angle = obs['checkpoint'][1]
        current_angle = obs['pod'][1]
        control = {
            'thrust': 100,
            'rotation': (next_checkpoint_angle - current_angle) * 0.5,
        }
        obs, reward, done, _ = env.step(control)
        print i, reward, obs