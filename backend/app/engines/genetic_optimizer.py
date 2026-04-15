"""
SmartLogistics – Genetic Algorithm Optimizer
Optimizes item placement ORDER for bin packing.
Population: 50 | Generations: 100 | Mutation: 0.1 | Selection: Tournament k=3 | Crossover: OX
"""
import random
from typing import List, Dict, Any
from app.engines.packing_engine import PackingEngine, Item
from app.core.constants import (
    GA_POPULATION_SIZE, GA_GENERATIONS, GA_MUTATION_RATE, GA_TOURNAMENT_K
)


def _heuristic_fitness(order: List[int], items: List[Item], box_volume: float) -> float:
    """Fast volume compatibility score without full pack."""
    # Estimate fillability: sum volumes + sort compat
    item_vols = [items[i].volume() for i in order]
    total_vol = sum(item_vols)
    if total_vol > box_volume * 0.95:
        return 0.0
    # Bonus for large-first order
    compat_score = 1.0
    for i in range(1, len(item_vols)):
        if item_vols[i] > item_vols[i-1]:
            compat_score -= 0.1
    return min(total_vol / box_volume * compat_score, 1.0)


def _full_fitness(order: List[int], items: List[Item], box: Dict[str, Any]) -> float:
    """Full accurate fitness."""
    ordered_items = [items[i] for i in order]
    engine = PackingEngine(box["length"], box["width"], box["height"])
    result = engine.pack_items(ordered_items)
    utilization = result["utilization"] / 100.0
    cost = float(box["base_cost"])
    epsilon = 1e-6
    return utilization / (cost + epsilon)


def _fitness(order: List[int], items: List[Item], box: Dict[str, Any], elite_eval: bool = False) -> float:
    box_vol = box["length"] * box["width"] * box["height"]
    if elite_eval:
        return _full_fitness(order, items, box)
    return _heuristic_fitness(order, items, box_vol) * (box["base_cost"] / 100.0) ** -0.5


def _tournament_select(population: List[List[int]], fitnesses: List[float], k: int) -> List[int]:
    """Tournament selection: pick k individuals, return best."""
    contestants_idx = random.sample(range(len(population)), k)
    best_idx = max(contestants_idx, key=lambda i: fitnesses[i])
    return population[best_idx][:]


def _order_crossover(parent1: List[int], parent2: List[int]) -> List[int]:
    """OX crossover: preserves relative order of parent2's elements."""
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [-1] * size
    child[start:end] = parent1[start:end]
    remaining = [x for x in parent2 if x not in child[start:end]]
    ptr = 0
    for i in range(size):
        if child[i] == -1:
            child[i] = remaining[ptr]
            ptr += 1
    return child


def _mutate(chromosome: List[int], rate: float) -> List[int]:
    """Swap mutation: randomly swap two genes."""
    if random.random() < rate:
        i, j = random.sample(range(len(chromosome)), 2)
        chromosome[i], chromosome[j] = chromosome[j], chromosome[i]
    return chromosome


def optimize_packing_order(
    items: List[Item],
    box: Dict[str, Any],
) -> List[Item]:
    """
    Run GA to find the optimal item placement order.
    Returns reordered list of Items.
    """
    if len(items) <= 2:
        return items  # GA not needed for trivial cases

    n = len(items)
    # Dynamic scaling
    pop_size = max(10, min(GA_POPULATION_SIZE, n * 3))
    gens = max(20, min(GA_GENERATIONS, n * 8))
    population = [random.sample(range(n), n) for _ in range(pop_size)]

    best_chromosome = None
    best_fitness = -1.0
    stagnant_gens = 0

    for generation in range(gens):
        # Hybrid fitness: heuristic for most, full for elites
        fitnesses = []
        for chrom in population:
            elite = chrom == population[0]  # top heuristic elite gets full eval
            fitnesses.append(_fitness(chrom, items, box, elite_eval=elite))
        
        # Early stop
        gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        gen_best_fit = fitnesses[gen_best_idx]
        if gen_best_fit > best_fitness:
            best_fitness = gen_best_fit
            best_chromosome = population[gen_best_idx][:]
            stagnant_gens = 0
        else:
            stagnant_gens += 1
            if stagnant_gens > 5:
                break

        # Elitism top 2
        sorted_idx = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
        next_population = [population[i] for i in sorted_idx[:2]]

        # Fill rest with crossover + mutation
        while len(next_population) < pop_size:
            p1 = _tournament_select(population, fitnesses, GA_TOURNAMENT_K)
            p2 = _tournament_select(population, fitnesses, GA_TOURNAMENT_K)
            child = _order_crossover(p1, p2)
            child = _mutate(child, GA_MUTATION_RATE)
            next_population.append(child)

        population = next_population

    if best_chromosome is None:
        return sort_items_by_volume(items)  # FFD fallback

    from app.engines.packing_engine import sort_items_by_volume
    return [items[i] for i in best_chromosome]
