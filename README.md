# Play hockey via Reinforcement Learning (Soft Actor Critic)
The soft actor critic algorithm is implemented in order to train an agent for the provided hockey environment. 
This project was done as part of my Reinforcement Learning course at the University of Tübingen.

## Played environments
As the hockey environment was completely new and a little more challenging, a more easy environment was chosen at the beginning.

### Pendulum
Firstly, the agent was trained to handle the pendulum environment. It is considered a relatively easy environment which helped me to see if the approaches and implementations I did were legitimate.
For more information about this game, have a look at the official [gym documentation](https://www.gymlibrary.dev/environments/classic_control/pendulum/).

### Hockey
After establishing a good foundation and successfully managing the pendulum environment, the hockey game provided by our professor was then targeted.
The hockey environment is a game between two players, where we can control the left player

## Using SAC
Soft Actor-Critic (SAC) is an off-policy algorithm. Unlike other off-policy algorithms (e.g. TD3), its exploration comes from its emphasis on maximizing the entropy, which represents the uncertainty in the agent’s actions. By maximizing entropy, SAC encourages exploration and prevents the agent from prematurely converging to maybe suboptimal policies. For further information about SAC, my approach and results, please take a closer at my [paper](./sac_okan.pdf).

## Results

<table>
  <tr>
    <td>
        <a href="https://github.com/okihnjo/reinforcementLearning/assets/50614363/03045774-9a67-49b1-83a1-1f47f327b92e">
        <img src="https://github.com/okihnjo/reinforcementLearning/assets/50614363/03045774-9a67-49b1-83a1-1f47f327b92e" width="100%" alt="Hockey environment">
      </a>
    </td>
    <td>
      <a href="https://github.com/okihnjo/reinforcementLearning/assets/50614363/49d72605-855a-4496-9b49-c42f774d89a1">
        <img src="https://github.com/okihnjo/reinforcementLearning/assets/50614363/49d72605-855a-4496-9b49-c42f774d89a1" width="400px" alt="Pendulum environment">
      </a>
    </td>
  </tr>
</table>
