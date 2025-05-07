from uuid import uuid4 as uid
from random import randint, sample
import re


class PokeBase():
    def __init__(self):
        self.pokes = []
    
    def add_poke(self, poke):
        if poke not in self.pokes:
            self.pokes.append(poke)
             

class Stat():
    def __init__(self, is_31=False, braced=False):
        self.is_31 = False
        self.is_braced = False

    def str_to_stat(self, stat_str):
        is_braced = stat_str == '*'
        is_31 = (stat_str == '+') or is_braced
        self.is_31 = is_31
        self.is_braced = is_braced

    def __str__(self):
        if self.is_braced:
            return '*'
        elif self.is_31:
            return '+'
        else:
            return '-'


class Nature():
    def __init__(self, has_nature=False):
        self.has_nature = has_nature

    def __str__(self):
        return "[Nat]" if self.has_nature else ""


class Gender():
    def __init__(self, is_male=True):
        self.is_male = is_male

    def str_to_gender(self, gender_code):
        gender_code.replace('(','')
        gender_code.replace(')','')
        gender_code.replace(' ','')
        if gender_code == 'm':
            self.is_male = True
        elif gender_code == 'f':
            self.is_male = False
        else:
            self.is_male = None

    def __str__(self):
        g = '?'
        if self.is_male == True:
            g = 'm'
        elif self.is_male == False:
            g = 'f'
        elif self.is_genderless == None:
            g = '*'
        return f"({g})"


class Poke():
    def __init__(self, stats=None):
        self.id = uid().hex[:7]
        self.stats = [Stat() for i in range(6)]
        self.gender = Gender(None)
        self.nature = Nature()
        self.parent_male = None
        self.parent_female = None
        self.offspring = None
        if stats:
            self.str_to_stats(stats)

    def str_to_stats(self, stats_code):
        stats_code = stats_code.replace(' ','').strip()
        new_stats = []
        for i in range(6):
            s = Stat()
            s.str_to_stat(stats_code[i])
            new_stats.append(s)
        self.stats = new_stats
        # getting the gender
        pattern = r'\((.)\)'
        match = re.search(pattern, stats_code)
        if match:
            g = match.group(1)
            gender = Gender()
            gender.str_to_gender(g)
            self.gender = gender
        # getting the nature
        if "[Nat]" in stats_code:
            self.nature = True

    def get_stats(self):
        return ' '.join([str(s) for s in self.stats])

    def generate_random_parents(self, recursive=False):
        # checking if there is not parents already
        assert (self.parent_male == None) and (self.parent_female == None), "pkmn already has parents"
        # check if the pokemon has 1 or less IV in 31
        if sum([int(s.is_31) for s in self.stats])<=1:
            print("this pkmn doesnt need a parent")
            return None, None
        # make a list of stats that needs to be inherited (save only the index, ex: [0,5] is to save HP and Speed
        stats_to_inherit = []
        for i, stat in enumerate(self.stats):
            if stat.is_31:
                stats_to_inherit.append(i)
        # now, randomly select 2 of those stats to pass on
        stats_to_brace = sample(stats_to_inherit, min(len(stats_to_inherit),2))
        # now select the stats that both mom and dad should have in commom, so neither should brace
        stats_to_inherit = [v for v in stats_to_inherit if v not in stats_to_brace]
        # creates the instances of both parents
        p1, p2 = Poke(), Poke()
        # apply to both mom and dad the stats that both should have in commom
        for stat in stats_to_inherit:
            p1.stats[stat].is_31 = True
            p2.stats[stat].is_31 = True
        # also apply one stat to be braced in one of the parents
        p1.stats[stats_to_brace[0]].is_braced = True
        p1.stats[stats_to_brace[0]].is_31 = True
        # if there's 2 stats to brace, also apply it to the other parent
        if len(stats_to_brace) == 2:
            p2.stats[stats_to_brace[1]].is_braced = True
            p2.stats[stats_to_brace[1]].is_31 = True
        # randomize the gender for each parent (assuring one is opposite of the other)
        gender_seed = bool(randint(0,1))
        gender_pair = [gender_seed, not gender_seed]
        p1.gender.is_male = gender_pair[0]
        p2.gender.is_male = gender_pair[1]
        p_male, p_female = [p1,p2] if p1.gender.is_male else [p2,p1]
        # make a temporary variable for storing the male and female parent
        self.parent_male = p_male
        self.parent_female = p_female
        # add the address of the son on each parent "offspring" attribute
        p_male.offspring = self
        p_female.offspring = self
        # now the magic, apply this same code recursively on each parent
        if recursive:
            p_male.generate_random_parents(recursive=True)
            p_female.generate_random_parents(recursive=True)
        return p1, p2

    def __str__(self):
        s = self.get_stats()
        g = str(self.gender)
        n = str(self.nature)
        if self.gender == True:
            g = 'm'
        if self.gender == False:
            g = 'f'
        return f"{self.id}: {s} {g} {n}"

def breed(p1, p2):
    p1, p2 = (p1,p2) if p1.gender.is_male else (p2,p1)

    p1t = str(p1)
    p1o = p1

    p2t = str(p2)
    p2o = p2
    
    nature = "[Nat]" if "[Nat]" in p1t or "[Nat]" in p2t else ""
    p1_stats = p1t.split(':')[-1].split('(')[0].replace(' ','').strip()
    p2_stats = p2t.split(':')[-1].split('(')[0].replace(' ','').strip()
    new_stats = list('------')

    new_gender = ['m','f'][randint(0,1)]
    for i in range(6):
        p1_stat = p1_stats[i]
        p2_stat = p2_stats[i]
        
        if p1_stat == p2_stat:
            new_stats[i] = p1_stat

        if (p1_stat == '*') or (p2_stat == '*'):
            new_stats[i] = '+'
    offspring = Poke()
    s = f"{' '.join(new_stats)} ({new_gender}) {hold_nature}"
    print(s)
    offspring.str_to_stats(s)
    offspring.parent_male = p1o
    offspring.parent_female = p2o
    p1o.offspring = offspring
    p2o.offspring = offspring
    return offspring

if __name__=="__main__":
    p1 = Poke()
    p2 = Poke()
    print(p1)
    p1.str_to_stats('* + - - - - (m)')
    p2.str_to_stats('- + - * - - (f)')
    print("\np1")
    print(p1)
    print("\np2")
    print(p2)
    o = breed(p1, p2)
    print("\no")
    print(o)
    print(f"---")
    c = Poke()
    c.str_to_stats('+ + - - + - (f)')
    a,b = c.generate_random_parents(recursive=True)
    print(f"a: {a}\nb: {b}")

