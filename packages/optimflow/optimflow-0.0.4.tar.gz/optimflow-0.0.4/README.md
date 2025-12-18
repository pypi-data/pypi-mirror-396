# Parameter Space Exploration and CMA-ES Optimisation

This package might be useful if you have a model taking as input a set of parameters.

Start simulations from any sample(s) drown from the parameter space. Sampling may be analytical (like ParameterSpaceExploration with param iterators) or unknown (like ParameterSpaceAsk for CMA-ES).

The simulation parameters are the main model parameters. Optimisation parameters define a subset of simu params and spawn the parameter space. This package basically builds SimulationParameters for any sample of the parameter space, allowing to easily start simulations, and optimisation.

## Install

```bash
pip install optimflow
```

## Run parameters exploration

```python
out_path = Path(__file__).parent / "out"

# Declare parameters of interest
class Params(OptimParams):
    p1 = param.Number(1, bounds=(0, 1), doc="Parameter 1")
    p2 = param.Number(1, bounds=(0.9, 1.1), doc="Parameter 2")

# Create simulation and exploration parameters
simulation_params = SimulationParams()
optim_params = Params()

# Define your simulation worker
def worker(dname: str):
    # Load parameters from the directory (prepared by dump_params)
    params = SimulationParams.load_from(dname)

    # mock the model's result
    t = np.linspace(0, 1, 100)
    res = params.p1 * np.sin(params.p2 * 2 * np.pi * t)
    np.savetxt(params.out_dir / "result.txt", res)

# Main class to start exploring the parameter space
explo = ParameterSpaceExploration(out_path)
explo.dump_params(simulation_params, optim_params)  # linear iterator
explo.run(worker, parallel=True)  # start all models
explo.gather_results()  # build a big pandas dataframe
explo.plot_results()  # plot model results for each varying optim param
```
