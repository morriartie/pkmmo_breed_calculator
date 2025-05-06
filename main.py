from graphviz import Digraph
import lib
import random


def similarity_score(poke_base, root_parents):
    score = 0
    for parent in root_parents:
        for pb_poke in poke_base:
            # Compare stats
            for stat1, stat2 in zip(parent.stats, pb_poke.stats):
                if stat1.is_31 and stat2.is_31:
                    score += 1
            # Compare gender
            if parent.gender.is_male == pb_poke.gender.is_male:
                score += 1
    return score

def visualize_breeding_tree(poke, graph=None, wild_pokes=None):
    if graph is None:
        graph = Digraph(format='png', graph_attr={'rankdir': 'TB'})
        wild_pokes = set()

    poke_label = f"{poke.id}\\nStats: {poke.get_stats()}\\nGender: {poke.gender}"
    if poke.parent_male and poke.parent_female:
        graph.node(poke.id, poke_label)
        graph.node(poke.parent_male.id, f"{poke.parent_male.id}\\nStats: {poke.parent_male.get_stats()}\\nGender: {poke.parent_male.gender}")
        graph.node(poke.parent_female.id, f"{poke.parent_female.id}\\nStats: {poke.parent_female.get_stats()}\\nGender: {poke.parent_female.gender}")
        graph.edge(poke.parent_male.id, poke.id)
        graph.edge(poke.parent_female.id, poke.id)
        visualize_breeding_tree(poke.parent_male, graph, wild_pokes)
        visualize_breeding_tree(poke.parent_female, graph, wild_pokes)
    else:
        graph.node(poke.id, poke_label, style='dotted')
        wild_pokes.add(poke)

    return graph, wild_pokes

if __name__ == "__main__":
    target = '+ + - - + - (f)'
    pb = lib.PokeBase()
    pb.add_poke(lib.Poke('- - - - + - (m)'))
    pb.add_poke(lib.Poke('- - - + - - (f)'))
    pb.add_poke(lib.Poke('- - + - - - (m)'))
    pb.add_poke(lib.Poke('- - - - - + (f)'))

    poke_base = pb.pokes  # Assuming PokeBase has a list of pokemons
    best_trees = []

    for _ in range(100):  # Iterate to generate 20 trees, repeatedly replacing the worst
        target_poke = lib.Poke(target)  # Generate a random target Pokémon
        target_poke.generate_random_parents(recursive=True)

        # Root parents
        root_parents = [target_poke.parent_male, target_poke.parent_female]
        score = similarity_score(poke_base, root_parents)

        # Save the tree and score
        tree_data = {
            "poke": target_poke,
            "score": score,
            "graph": None  # Graphviz tree will be generated when needed
        }
        best_trees.append(tree_data)
        best_trees = sorted(best_trees, key=lambda x: x['score'], reverse=True)[:20]

        # Replace the worst tree if necessary
        if len(best_trees) > 20:
            best_trees.pop()

    # Visualize the best tree
    best_tree = best_trees[0]
    best_graph, wild_pokes = visualize_breeding_tree(best_tree["poke"])
    best_graph.render("best_breeding_tree")

    print("\nBest tree similarity score:", best_tree["score"])
    print("\nWild Pokémon required for the best tree:")
    for wild_poke in wild_pokes:
        print(f"ID: {wild_poke.id}, Stats: {wild_poke.get_stats()}, Gender: {wild_poke.gender}")