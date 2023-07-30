import numpy as np

import gym
from collections import deque
import torch
import torch.nn as nn
import pandas as pd
import time
from torch.utils.tensorboard import SummaryWriter
import argparse
import plotly.express as px
from agent import Agent
from simple_agent import SimpleAgent
from utils_sac import plot_reward
import plotly.graph_objects as go
import numpy as np

import gymnasium as gym
from importlib import reload
import copy
import datetime
import laserhockey.hockey_env as hock_env
from utils_sac import  moving_mean, save_network, load_model, plot_reward
import random
np.set_printoptions(suppress=True)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
actor_losses, critic_losses, critic2_losses, alpha_losses, scores = [], [], [], [], []
def SAC(n_episodes=500, max_t=500, print_every=500, agent_type="new", mode: int=0):
    print(f"Playing {n_episodes} episodes with max_t={max_t} with mode {mode}")
    env=hock_env.HockeyEnv(mode=mode)
    str_oppponent_cnt = 0
    p=1000
    opponent = hock_env.BasicOpponent(weak=True)
    agent_support = hock_env.BasicOpponent(weak=False)
    total_my=0
    s = -0.5  # reward for closeness to puck init
    for i_episode in range(1, n_episodes+1):
        state, _ = env.reset()
        obs_agent2 = env.obs_agent_two()
        score = 0
        # if i_episode % 1000 == 0:
        #    p = 0.8
        for t in range(max_t):
            if random.random() < p:
                p = p/2
                action_ag_1 = agent_support.act(state) 
                str_oppponent_cnt += 1   
            else:
                action_ag_1 = agent.act(state)
            action_ag_2 = opponent.act(obs_agent2)
            if i_episode > 1000 and comp_flag == False:
                env.render()
            next_state, reward, done,_, info = env.step(np.hstack([action_ag_1,action_ag_2]))
            if s<info['reward_closeness_to_puck']:
                s = info['reward_closeness_to_puck']
                reward= reward + 5
            else: 
                reward = reward - 1
            
            losses=agent.step(state, action_ag_1, reward, next_state, done, t)
            if losses != None:
                actor_losses.append(losses[0])
                critic_losses.append(losses[1])
                critic2_losses.append(losses[2])
                alpha_losses.append(losses[3])
            state = next_state
            obs_agent2 = env.obs_agent_two()
            score += reward
            total_my = t
            if done:
                break 
        if p<0.01:
            if i_episode<100:
                p=100
            else: 
                p=10
        
        print(f"\r Moves made by STRONG opponent {str_oppponent_cnt}, by total {total_my} ({str(str_oppponent_cnt/total_my)}%) ", end="") if total_my != 0 else print(f"\r 0 moves made ", end="")
        str_oppponent_cnt = 0
        scores.append(score)
            

        print('- Episode {} Reward: {:.2f}  Average100 Score: {:.2f} '.format(i_episode, score, np.mean(scores)), end="")
    
    env.close()
    if agent_type=="new" : save_network(agent.actor_local, "sac_hockey") 
    
    
    





def play():
    env=hock_env.HockeyEnv()
    agent.actor_local.eval()
    opponent = hock_env.BasicOpponent(weak=False)
    epis = []
    for i_episode in range(20):
        state,_ = env.reset()
        obs_opponent = env.obs_agent_two()
        while True:
            env.render()
            action_ag_1 = opponent.act(state)
            action_ag_2 = opponent.act(obs_opponent)
            next_state, reward, done,_, info = env.step(np.hstack([action_ag_1,action_ag_2]))
            state = next_state
            epis.append(reward)
            if done:
                print(len(epis))
                break 
                


parser = argparse.ArgumentParser(description="")
parser.add_argument("-env", type=str,default="Pendulum-v0", help="Environment name")
parser.add_argument("-ep", type=int, default=500, help="The amount of training episodes, default is 100")
parser.add_argument("-seed", type=int, default=0, help="Seed for the env and torch network weights, default is 0")
parser.add_argument("-lr", type=float, default=1e-4, help="Learning rate of adapting the network weights, default is 5e-4")
parser.add_argument("-a", "--alpha", type=float, help="entropy alpha value, if not choosen the value is leaned by the agent")
parser.add_argument("-layer_size", type=int, default=256, help="Number of nodes per neural network layer, default is 256")
parser.add_argument("-repm", "--replay_memory", type=int, default=int(1e6), help="Size of the Replay memory, default is 1e6")
parser.add_argument("--print_every", type=int, default=500, help="Prints every x episodes the average reward over x episodes")
parser.add_argument("-bs", "--batch_size", type=int, default=128, help="Batch size, default is 256")
parser.add_argument("-t", "--tau", type=float, default=1e-2, help="Softupdate factor tau, default is 1e-2")
parser.add_argument("-g", "--gamma", type=float, default=0.95, help="discount factor gamma, default is 0.99")
parser.add_argument("-saved_model", type=str, default=None, help="Load a saved model to perform a test run!")
parser.add_argument("--agent_type", type=str, default="new", help="If new, then double q is used. Use given old, then simple version is executed")
parser.add_argument("--compare", type=bool, default=False, help="If true, compare the two agents")

args = parser.parse_args()
reload(hock_env)

if __name__ == "__main__":
    env_name = args.env
    seed = args.seed
    n_episodes = args.ep
    GAMMA = args.gamma
    TAU = args.tau
    HIDDEN_SIZE = args.layer_size
    BUFFER_SIZE = int(args.replay_memory)
    BATCH_SIZE = args.batch_size        # minibatch size
    LR_ACTOR = args.lr         # learning rate of the actor 
    LR_CRITIC = args.lr        # learning rate of the critic
    FIXED_ALPHA = args.alpha
    saved_model = args.saved_model
    agent_type = args.agent_type
    comp_flag = args.compare

    t0 = time.time()
    env_for_shape = hock_env.HockeyEnv()
    action_high = env_for_shape.action_space.high[0]
    action_low = env_for_shape.action_space.low[0]
    torch.manual_seed(seed)
    env_for_shape.seed(seed)
    np.random.seed(seed)
    state_size = env_for_shape.observation_space.shape[0]
    action_size = env_for_shape.action_space.shape[0]
    agent = Agent(state_size=state_size, action_size=4, random_seed=seed,hidden_size=HIDDEN_SIZE, action_prior="uniform") #"normal"
    if saved_model != None:
        load_model(agent.actor_local, saved_model)
        play()
    else:
        load_model(agent.actor_local, saved_model)
        
        SAC(n_episodes=1010, max_t=800, print_every=args.print_every, agent_type=args.agent_type, mode=1)
        SAC(n_episodes=500, max_t=800, print_every=args.print_every, agent_type=args.agent_type, mode=0)
        SAC(n_episodes=1010, max_t=800, print_every=args.print_every, agent_type=args.agent_type, mode=2)
        SAC(n_episodes=500, max_t=800, print_every=args.print_every, agent_type=args.agent_type, mode=0)
        moving_mean((actor_losses, critic_losses, critic2_losses, alpha_losses))
        window_size = 200
        num_segments = len(scores) // window_size
        segments = np.array_split(scores, num_segments)
        averages = [segment.mean() for segment in segments]
        plot_reward(averages)
    t1=time.time()
    env_for_shape.close()
    print("training took {} min!".format((t1-t0)/60))
