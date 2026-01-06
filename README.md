# Tegame

Tegame is an experimental Python project for simulating and analyzing *The Game*, with the goal of studying gameplay strategies and developing an automated agent. The repository is designed as a small research pipeline, starting from statistical analysis and progressing toward a machine-learning-based solution.

## Contributors

I developed this code together with my friend and colleague Piermarco Saraceno (https://github.com/saracenopiermarco) during the hot Italian summer days of August 2025.

## Goals

- Implement the rules and core logic of *The Game*
- Analyze the performance of non-ML strategies through win-rate statistics
- Build a machine learning pipeline to learn gameplay policies

## Notebooks

The notebooks are organized into two main phases:

1. **Statistical analysis**
   - Notebooks focused on studying the game behavior without machine learning
   - Analysis win-rate statistics and effect of thresholds which regulate the players gamestyle

2. **Machine Learning pipeline**
   - Numbered notebooks representing the different steps of the pipeline:
     - dataset generation
     - model training
     - testing and evaluation

## Installation

Requires **Python 3.10+**.  
Dependencies are defined in `pyproject.toml` and `requirements.txt`.

## Running the game

To run a game using the provided scripts:

**Unix**
```bash
script/run_game.sh
```

**Windows**
```bat
script/run_game.bat
```

Alternatively, the main interaction with the project happens through the notebooks.

## Project status

This project is experimental. Internal APIs and structure may change as analyses and models evolve.

## Possible future work

- Implement more advance moves in the non-ML code
- Implement a Reinforcement Learning (RL) version

## Contributing

Contributions are welcome!  
If you’d like to improve the bot, fix a bug, or propose a new feature, feel free to:

- open an issue  
- submit a pull request  
- suggest enhancements or improvements to the monitoring logic  

Please keep the code clean, documented, and consistent with the existing structure.

---

## Support

If you find this project interesting, consider giving it a ⭐ on GitHub.  
You can also share ideas, report issues, or suggest new features through the repository’s issue tracker.