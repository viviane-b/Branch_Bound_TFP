# Implementation of a Branch & Bound algorithm to solve the Team Formation Problem

Implementation of the algorithm presented in *A Branch-and-Bound Algorithm for Team Formation on Social Networks* by 
Berktaş and Yaman.

Nihal Berktaş , Hande Yaman  (2021) A Branch-and-Bound Algorithm for Team Formation on Social Networks.
INFORMS Journal on Computing 33(3):1162-1176. https://doi.org/10.1287/ijoc.2020.1000

The dataset is available at https://github.com/nihalberktas/TFP-data/tree/master

## How to run

```bash
# go in directory Branch_Bound_TFP
python main.py
```
A prompt will appear to ask the number of required skills, m: from the 27 existing skills of the IMDb
dataset, it will choose m skills at random based on the seed in the second prompt.  
**Warning**: The higher the number of required skills, the more time it will take to 
solve the instance. See *results/results_mean.csv* for an idea of the time needed for solving 
the instances.

A second prompt will appear to ask for a seed, which is used in the generation of the set
of required skills.

The instance will be solved using a simplified Gurobi model, then using the branch & bound implementation.
The optimal team and its cost found with both solvers will be displayed, along with the running times.

