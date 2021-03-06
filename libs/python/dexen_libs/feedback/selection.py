# ==================================================================================================
#
#    Copyright (c) 2008, Patrick Janssen (patrick@janssen.name)
#
#    This file is part of Dexen.
#
#    Dexen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Dexen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================

"""
A library of selection functions. Assumes that ind objects have an attribute called 'fitness'.

These selection functions return the selected individuals. The list of inds are not affected. 
(i.e. The order of these lists remains the same.)
"""

import random

#constants
RANDOMLY = 0
OLDEST = 1
YOUNGEST = 2
BEST = 3
WORST = 4
ROULETTE_BEST = 5
ROULETTE_WORST = 6
TOURNAMENT_BEST = 7
TOURNAMENT_WORST = 8
TOURNAMENT_RTS_BEST = 9
TOURNAMENT_RTS_WORST = 10

# select 
def select(inds, num, selection_type, *args):
    #================================================
    if selection_type == RANDOMLY:
        return randomly(inds, num)
    #================================================
    elif selection_type == OLDEST:
        return oldest(inds, num)
    elif selection_type == YOUNGEST:
        return youngest(inds, num)
    #================================================
    elif selection_type == BEST:
        return best(inds, num)
    elif selection_type == WORST:
        return worst(inds, num)
    #================================================
    elif selection_type == ROULETTE_BEST:
        return roulette(inds, num)
    elif selection_type == ROULETTE_WORST:
        return roulette(inds, num, select_best=False)
    #================================================
    elif selection_type == TOURNAMENT_BEST:
        if len(args) != 1:
            print "ERROR: Args for TOURNAMENT_BEST are incorrect."
            raise Exception()
        tournament_size = int(args[0])
        return tournament(inds, num, tournament_size)
    elif selection_type == TOURNAMENT_WORST:
        if len(args) != 1:
            print "ERROR: Args for TOURNAMENT_WORST are incorrect."
            raise Exception()
        tournament_size = int(args[0])
        return tournament(inds, num, tournament_size, select_best=False)
    #================================================
    elif selection_type == TOURNAMENT_RTS_BEST:
        if len(args) != 2:
            print "ERROR: Args for TOURNAMENT_RTS_BEST are incorrect."
            raise Exception()
        window_size = int(args[0])
        tournament_size = int(args[1])
        return tournament_rts(inds, num, window_size, tournament_size)
    elif selection_type == TOURNAMENT_RTS_WORST:
        if len(args) != 2:
            print "ERROR: Args for TOURNAMENT_RTS_WORST are incorrect."
            raise Exception()
        window_size = int(args[0])
        tournament_size = int(args[1])
        return tournament_rts(inds, num, window_size, tournament_size, select_best=False)
    #================================================
    else:
        print "ERROR: Selection type is not recognised: "+ selection_type
        raise Exception()

# select oldest individuals
def oldest(inds, num):
    inds = list(inds) #shallow copy
    inds.sort(key=lambda ind: ind.get_id(), reverse=True)
    return inds[:num]

# select youngest individuals
def youngest(inds, num):
    inds = list(inds)
    inds.sort(key=lambda ind: ind.get_id())
    return inds[:num]

# select randomly individuals
def randomly(inds, num):
    inds = list(inds) #shallow copy
    random.shuffle(inds)
    return inds[:num]

# select best individuals
def best(inds, num):
    inds = list(inds) #shallow copy
    inds.sort(key=lambda ind: ind.fitness, reverse=True)
    return inds[:num]
    
# select worst individuals
def worst(inds, num):
    inds = list(inds) #shallow copy
    inds.sort(key=lambda ind: ind.fitness)
    return inds[:num] 
    
# select using roulette 
def roulette(inds, num,  select_best=True):
    """Roulette Wheel selection. Also know as 'fitness proportionate selection'.
    Selected inds may include duplicates.
    """
    inds = list(inds) #shallow copy
    fits = [ind.fitness for ind in inds]
    min_fit = min(fits)
    max_fit = max(fits)
    fit_range = max_fit - min_fit
    if select_best:
        normalised_fits = [(fit - min_fit)/float(fit_range) for fit in fits]
    else:
        normalised_fits = [1 - ((fit - min_fit)/float(fit_range)) for fit in fits] 
    sum_normalised_fits = sum(normalised_fits)
    wheel_spins = [random.random() * sum_normalised_fits for _ in range(num)]
    selected = []
    for wheel_spin in wheel_spins:
        for ind, normalised_fit in zip(inds, normalised_fits):
            wheel_spin -= normalised_fit
            if wheel_spin <= 0:
                selected.append(ind)
                break
    if len(selected) != num:
        print "ERROR: Wrong number of inds selected. Total selected =  ", len(selected)
        raise Exception()
    return selected

# select using tournament
def tournament(inds, num, tournament_size, select_best=True):
    """Deterministic tournament selection. The best individual in each tournament is selected. 
    Selected inds may include duplicates. 

    If the tournament size == number if inds, then you are seelcting the best ind each time. 
    (Note that if there is more than one best ind, this may result in different best inds being 
    selected.)
    """
    inds = list(inds) #shallow copy
    selected = []
    for _ in range(num):
        random.shuffle(inds)
        tournament = inds[:tournament_size]
        tournament.sort(key=lambda ind: ind.fitness, reverse=True)
        if select_best:
            selected.append(tournament[0])
        else:
            selected.append(tournament[-1])
    if len(selected) != num:
        print "ERROR: Wrong number of inds selected. Total selected =  ", len(selected)
        raise Exception()
    return selected

# select using tournament with restricted tournament selection
# TODO : fix the distance metric
def tournament_rts(inds, num, window_size, tournament_size, select_best=True):
    inds = list(inds) #shallow copy
    assert(window_size > tournament_size)
    # divide into new and old
    inds.sort(key=lambda ind: ind._get_id())
    new_inds = inds[-num:]
    old_inds = inds[:-num]
    # select inds
    selected = []
    for new_ind in new_inds:
        # window - sort based on distance
        random.shuffle(old_inds)
        window = old_inds[:window_size]
        for old_ind in window:
            new_genotype = [gene.value for gene in new_ind.genotype]
            old_genotype = [gene.value for gene in old_ind.genotype]
            # TODO: this distance metric only works in some cases
            old_ind.dist = sum([abs(pair[0]-pair[1]) for pair in zip(old_genotype, new_genotype)])
        window.sort(key=lambda ind: ind.dist)
        # tournament - sort based on fitness
        tournament = old_inds[:tournament_size] + [new_ind]
        tournament.sort(key=lambda ind: ind.fitness, reverse=True)
        if select_best:
            selected_ind = tournament[0]
        else:
            selected_ind = tournament[-1]
        # add the ind to the list and remove it so that it is not selected twice
        selected.append(selected_ind)
        try:
            old_inds.remove(selected_ind)
        except:
            pass
    if len(selected) != num:
        print "ERROR: Wrong number of inds selected. Total selected =  ", len(selected)
        raise Exception()
    return selected

#===============================================================================
# Testing
#===============================================================================

def main():

    class Ind(object):
        def __init__(self, id, scoreA, scoreB):
            self.id = id
            self.scoreA = scoreA
            self.scoreB = scoreB

        def get_id(self):
            return self.id

        def get_evaluation_score(self, name):
            return getattr(self, name)

        def __repr__(self, *args, **kwargs):
            return "id=" + str(self.id) + \
                " (" + str(self.scoreA) + "," + str(self.scoreB) + ") f=" + str(self.fitness)

    print "Starting testing"

    inds = [
        Ind(0,11,28),
        Ind(1,24,37),
        Ind(2,94,10),
        Ind(3,25,29),
        Ind(4,79,34),
        Ind(5,43,22),
        Ind(6,66,98),
        Ind(7,90,33),
        Ind(8,25,60),
        Ind(9,54,34)
    ] 

    print "=== MINIMIZE ==="
    from ranking import ScoreMeta, ScoresMeta, MIN, MAX
    scores_meta = ScoresMeta()
    scores_meta.append(ScoreMeta("scoreA", MIN))
    scores_meta.append(ScoreMeta("scoreB", MIN))

    from fitness import fitness, PARETO_GOLDBERG_RANKING
    fitness(inds, scores_meta, PARETO_GOLDBERG_RANKING, normalize=True)

    print "RANDOMLY"
    print select(inds, 4, RANDOMLY)

    print "OLDEST"
    print select(inds, 4, OLDEST)

    print "YOUNGEST"
    print select(inds, 4, YOUNGEST)

    print "BEST"
    print select(inds, 4, BEST)

    print "WORST"
    print select(inds, 4, WORST)

    print "ROULETTE_BEST"
    print select(inds, 4, ROULETTE_BEST)

    print "ROULETTE_WORST"
    print select(inds, 4, ROULETTE_WORST)

    print "TOURNAMENT_BEST"
    print select(inds, 4, TOURNAMENT_BEST, 10)

    print "TOURNAMENT_WORST"
    print select(inds, 4, TOURNAMENT_WORST, 10)


# TOURNAMENT_RTS_BEST = "tournament_rts_best"
# TOURNAMENT_RTS_WORST = "tournament_rts_worst"

if __name__ == "__main__":
    main()