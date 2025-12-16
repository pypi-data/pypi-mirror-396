import logging

from prettytable import PrettyTable

from messthaler_wulff.additive_simulation import OmniSimulation, SimpleNeighborhood
from messthaler_wulff.explorative_simulation import ExplorativeSimulation, crystal_data

log = logging.getLogger("messthaler_wulff")


def run_mode(goal, lattice, dimension):
    omni_simulation = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (dimension + 1)))
    explorative_simulation = ExplorativeSimulation(omni_simulation)

    energies, counts = crystal_data(omni_simulation, goal)
    table = PrettyTable(["nr atoms", "nr crystals", "min energy"], align='r')

    for i in counts.keys():
        table.add_row([i, counts[i], energies[i]])

    print(table)

    # plt.plot(energies.keys(), energies.values())
    # plt.plot(counts.keys(), counts.values())
    # plt.show()
