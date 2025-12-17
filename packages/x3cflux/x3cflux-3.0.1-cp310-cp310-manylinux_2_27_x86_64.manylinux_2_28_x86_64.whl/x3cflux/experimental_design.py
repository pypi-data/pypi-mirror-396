import itertools
import xml.etree.ElementTree as ET
from typing import List, Dict, Union, Callable, Any

import numpy as np

from .lib.core import create_simulator_from_data, NetworkData, MeasurementConfiguration, ConstantSubstrate, Substrate
from .statistics import _compute_stable_fisher_inverse


class TracerMixtureSpace:
    r"""
    Space of labeled species (or even sets thereof) that can be combined into a tracer mixture.
    """

    def __init__(self, metabolite_name: str, species: List[Dict[str, float]], costs: List[float]):
        r"""
        Create tracer mixture space.

        :param metabolite_name:
            Name of the metabolite that is labeled
        :param species:
            List of labeled species, given as Dict mapping binary labeling strings to fractional content.
        :param costs:
            Costs of each set of species.
        """
        self.metabolite_name = metabolite_name
        self.species = species
        self.costs = costs

    def compute_mix_and_costs(self, relative_abundances: np.ndarray):
        r"""
        Compute tracer mixture and its costs given relative abundance of the species.

        :param relative_abundances:
            Fraction with which each mixture is contained in the final mixture. All fractions must sum up to one and
            each fraction must be between 0 and 1.
        :return:
            Final tracer mixture and its costs
        """
        mix = {}
        costs = 0.0

        num_species = len(self.species)
        assert len(relative_abundances) == num_species and np.allclose(relative_abundances.sum(), 1.0)

        for k in range(num_species):
            assert 0.0 <= relative_abundances[k] <= 1.0

            mixture_fraction = self.species[k]
            for labeling in mixture_fraction:
                if labeling not in mix:
                    mix.update({labeling: 0})
                mix[labeling] += relative_abundances[k] * mixture_fraction[labeling]
                costs += relative_abundances[k] * self.costs[k]

        return mix, costs


def parse_tracer_mixtures(file_name: str):
    r"""
    Parse spaces of possible tracer mixtures from XML file. The file is specified by the FluxML standard. Labeled
    compounds taken up by the metabolic network are labeled "input" and for each compound possible labeled species are
    specified.

    :param file_name:
        Absolute path to the file
    :return:
        List of TracerMixtureSpace, containing possible species for each input
    """
    ns = {"fml": "http://www.13cflux.net/fluxml"}
    tree = ET.parse(file_name)
    root = tree.getroot()

    assert root.tag == ("{" + ns["fml"] + "}mixture")
    assert root.find("fml:input", ns) is not None

    labeling_configs = {}
    for input_elem in root.findall("fml:input", ns):
        name = input_elem.attrib["pool"]

        configs = []
        for labeling in input_elem.findall("fml:label", ns):
            costs = 0.0
            if "costs" in labeling.attrib:
                costs = labeling.attrib["costs"]
            if not np.allclose(float(labeling.text), 0.0):
                configs.append((labeling.attrib["cfg"], float(labeling.text), float(costs)))

        if name not in labeling_configs:
            labeling_configs.update({name: []})
        labeling_configs[name].append(configs)

    tracer_mixture_spaces = []
    for name in labeling_configs:
        species = []
        costs = []

        for i, labeling_config in enumerate(labeling_configs[name]):
            species.append({labeling[0]: labeling[1] for labeling in labeling_config})
            costs.append(sum(map(lambda config: config[1] * config[2], labeling_config)))

        tracer_mixture_spaces.append(TracerMixtureSpace(name, species, costs))

    return tracer_mixture_spaces


def create_mixed_substrate(mixture_space: TracerMixtureSpace, relative_abundances: np.ndarray, name: str = None):
    r"""
    Create constant substrate input from a set of tracer species.

    :param mixture_space:
        Set of tracer species from which a final composition is generated.
    :param relative_abundances:
        Fraction with which each species is contained in the final mixture. All relative abundances must sum up to one
        and be between 0 and 1.
    :param name:
        Optional identifier used for the substrate pool.
    :return:
        x3cflux.ConstantSubstrate object
    """
    mix, costs = mixture_space.compute_mix_and_costs(relative_abundances)
    return ConstantSubstrate(name if name else "", mixture_space.metabolite_name, costs, mix)


def next_relative_abundances(num_species: int, num_ticks: int):
    r"""
    Generator of relative abundances by using equidistant steps for each component.

    :param num_species:
        Number of species in the mixtures
    :param num_ticks:
        Number of equidistant steps (between 0 and 1)
    :return:
        Mixture weight generator
    """
    assert num_species >= 2 and num_ticks >= 2

    dim_simplex = num_species - 1
    step_width = 1.0 / (num_ticks - 1)
    state = np.zeros(dim_simplex)
    end = False
    bary_coords = np.zeros(num_species)

    while not end:
        output = False
        bary_sum = 0.0
        while not output:
            coord_index = 0
            for coord_index in range(dim_simplex):
                bary_coords[coord_index] = step_width * state[coord_index]
                bary_sum += bary_coords[coord_index]
                if bary_sum > 1.0:
                    break

            bary_coords[-1] = 1.0 - bary_sum
            if bary_sum > 1.0:
                state[coord_index:] = num_ticks
            else:
                output = True

            occurrences = np.where(state != num_ticks)[0]
            if len(occurrences) == 0:
                end = True
                break
            coord_index = occurrences[-1]
            state[coord_index] += 1

            state[coord_index + 1 :] = 0

        if not end:
            yield bary_coords.copy()


def compute_mixture_samples(mixture_spaces: List[TracerMixtureSpace], num_ticks: Union[int, List[int]]):
    r"""
    Compute tracer mixture samples from a simplex according to given granularity.

    :param mixture_spaces:
        List of TracerMixtureSpace objects defining what species are possible for each mixture.
    :param num_ticks:
        The number of ticks used to sample relative abundances of the available labeled species. If given as
        int, the same number of ticks will be used for every tracer. Otherwise, a list containing number of ticks for
        each input must be specified.
    :return:
        Samples and associated fractional content of all mixture components
    """
    mix_substrates = []
    if isinstance(num_ticks, list):
        assert len(mixture_spaces) == len(num_ticks)
        mix_weights_combs = [
            [weight for weight in next_relative_abundances(len(mixture.mixtures), num_ticks_mix)]
            for mixture, num_ticks_mix in zip(mixture_spaces, num_ticks)
        ]
    else:
        mix_weights_combs = [
            [weight for weight in next_relative_abundances(len(mixture.species), num_ticks)]
            for mixture in mixture_spaces
        ]
    for weights in itertools.product(*mix_weights_combs):
        mix_substrates.append([create_mixed_substrate(mixture_spaces[i], weights[i]) for i in range(len(weights))])

    return mix_substrates, list(itertools.product(*mix_weights_combs))


def create_simulator_from_inputs(
    network_data: NetworkData,
    meas_config: MeasurementConfiguration,
    multi_substrates: List[List[Substrate]],
    fixed_substrates: List[Substrate] = None,
):
    r"""
    Creates simulator for multiple labeling experiments from given measurement configuration, replacing inputs according
    to given substrates. This is predominantly interesting for experimental design, where trying multiple substrate
    mixtures can be reframed as massive set of labeling experiments.

    :param network_data:
        Structural data of underlying metabolic network
    :param meas_config:
        Structural data of 13C measurements:
    :param multi_substrates:
        Substrates, for which different realizations should be simulated, e.g. in their labeling patterns. The inner
        list contains the different inputs to the metabolic network, whereas the outer list contains the different
        realizations.
    :param fixed_substrates:
        Substrates that have identical labeling.
    :return:
        Simulator object for all simultaneous substrates.
    """

    fixed_substrates = fixed_substrates if fixed_substrates is not None else []
    multi_meas_configs = [
        MeasurementConfiguration(
            "",
            meas_config.comment,
            meas_config.stationary,
            substrates + fixed_substrates,
            meas_config.measurements,
            meas_config.net_flux_constraints,
            meas_config.exchange_flux_constraints,
            meas_config.pool_size_constraints,
            meas_config.parameter_entries,
        )
        for substrates in multi_substrates
    ]

    return create_simulator_from_data(network_data, multi_meas_configs)


def _compute_d_criterion(jac, stddev):
    cov, nonident_idx = _compute_stable_fisher_inverse(np.diagflat(1.0 / stddev) @ jac)
    return np.linalg.det(np.delete(np.delete(cov, nonident_idx, axis=0), nonident_idx, axis=1))


def _compute_a_criterion(jac, stddevs):
    cov, nonident_idx = _compute_stable_fisher_inverse(np.diagflat(1.0 / stddevs) @ jac)
    return np.trace(np.delete(np.delete(cov, nonident_idx, axis=0), nonident_idx, axis=1))


def _compute_c_criterion(jac, stddevs):
    cov, nonident_idx = _compute_stable_fisher_inverse(np.diagflat(1.0 / stddevs) @ jac)
    return np.diag(np.delete(np.delete(cov, nonident_idx, axis=0), nonident_idx, axis=1)).max()


def _compute_e_criterion(jac, stddevs):
    cov, nonident_idx = _compute_stable_fisher_inverse(np.diagflat(1.0 / stddevs) @ jac)
    _, sv, _ = np.linalg.svd(np.delete(np.delete(cov, nonident_idx, axis=0), nonident_idx, axis=1))
    return sv[sv > 0.0].min() ** 2


def compute_ed_criteria(
        simulator,
        free_parameters: np.ndarray,
        substrate_mixtures: List[List[ConstantSubstrate]],
        criterion: Union[str, Callable] = "D",
        batch_size: int = 1,
) -> List[Any]:
    r"""
    Compute experimental design statistics on a grid of tracer mixtures, potentially from different substrates.

    :param simulator:
        Simulator for labeling experiments (supports only one configuration)
    :param free_parameters:
        A vector of valid free parameters.
    :param substrate_mixtures:
        Grid of mixed tracer species, generated by `compute_mixture_samples`.
    :param criterion:
        Criterion to be computed upon the Fisher information matrix (FIM), either as string
        (supported: "D", "A", "C" and "E"). Alternatively, a custom function can be specified taking the jacobian of the
        measurements and standard deviations.
    :param batch_size:
        Number of mixtures for which criteria are computed simultaneously. The actual batch size used might slightly
        deviate if batch_size does not divide num_ticks.
    :return:
        List of tuples that associates fractional content of all mixture components (according to the specified order)
        with the criteria values.
    """
    assert len(simulator.configurations) == 1

    fixed_substrates = []
    mix_substrate_names = [substr.metabolite_name for substr in substrate_mixtures[0]]
    for substrate in simulator.configurations[0].substrates:
        if substrate.metabolite_name not in mix_substrate_names:
            fixed_substrates.append(substrate)

    if not isinstance(criterion, Callable):
        if isinstance(criterion, str):
            if criterion == "D":
                criterion = _compute_d_criterion
            elif criterion == "A":
                criterion = _compute_a_criterion
            elif criterion == "C":
                criterion = _compute_c_criterion
            elif criterion == "E":
                criterion = _compute_e_criterion
            else:
                raise ValueError(f'"criterion" {criterion} is not supported')
        else:
            raise ValueError(f'{type(criterion)} is not a valid type for "criterion"')

    criteria_values = []
    batch_idx = np.linspace(0, len(substrate_mixtures), len(substrate_mixtures) // batch_size + 1)
    for i in range(len(batch_idx) - 1):
        lower_idx = int(batch_idx[i])
        upper_idx = int(batch_idx[i + 1])

        simulator = create_simulator_from_inputs(
            simulator.network_data, simulator.configurations[0],
            substrate_mixtures[lower_idx:upper_idx], fixed_substrates
        )
        jacobians = simulator.compute_multi_jacobians(free_parameters)
        stddevs = simulator.measurement_standard_deviations  # todo: if available, use measurement
        stddevs_flat = np.concatenate(
            (
                np.concatenate(stddevs[0][: (len(stddevs[0]) // (upper_idx - lower_idx))]),
                stddevs[1][: (len(stddevs[1]) // (upper_idx - lower_idx))],
            )
        )

        for i, jac in enumerate(jacobians):
            criteria_values.append(criterion(jac, stddevs_flat))

    return criteria_values
