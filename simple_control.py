from simple_environment import Environment

episodes_count = 10
if __name__ == '__main__':
    env = Environment()
    for i in range(episodes_count):
        obs = env.reset(i)
        print env.checkpoints
        for pod in env.pods:
            print pod

        print "START"
        done = False
        total_reward = 0
        while not done:
            next_checkpoint_angle = obs['checkpoint'][1]
            current_angle = obs['pod'][1]
            control = {
                'thrust': 100,
                'rotation': (next_checkpoint_angle - current_angle) * 0.5,
            }
            obs, reward, done, _ = env.step(control)
            total_reward += reward
        print i, total_reward