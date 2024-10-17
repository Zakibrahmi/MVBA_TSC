# MVBA_TSC
This repository contains code source of our paper MVBA_TSC: Majority Voting and Bayesian Average-Based Trustful Service Composition in Cloud and Edge Environments.

### Citation
Please cite the following reference when using this code:
```bibtex
@inproceedings{sebri2024mvba,
  title={MVBA$\backslash$\_TSC: Majority Voting and Bayesian Average-Based Trustful Service Composition in Cloud and Edge Environments},
  author={Sebri, Faten and De Prado, Roc{\'\i}o P{\'e}rez and Brahmi, Zaki},
  booktitle={2024 IEEE Congress on Evolutionary Computation (CEC)},
  pages={1--8},
  year={2024},
  organization={IEEE}
}
```
# How to use the code
1. Generate the dataset, which is a set of services and their service providers stored in MongoDB database.
2. Run the file app.py, which contains an example of execution. A user request is defined by its input and output (e.g., 'A', 'L'), and a service class is similarly defined by its input and output. Based on these inputs and outputs, we can create a dependency graph that illustrates the relationships between the service classes.

