
import streamlit as st
import lib
from graphviz import Digraph
import json
import os

# Global variables
POKE_BANK_FILE = "poke_bank.json"
poke_bank = []

# Load Poké Bank from JSON
def load_poke_bank():
    if os.path.exists(POKE_BANK_FILE):
        with open(POKE_BANK_FILE, "r") as file:
            data = json.load(file)
            pokes = []
            for entry in data:
                poke = lib.Poke()
                poke.id = entry["id"]
                poke.str_to_stats(entry["stats"])
                # Ensure gender is properly set
                if "(m)" in entry["gender"].lower():
                    poke.gender.is_male = True
                elif "(f)" in entry["gender"].lower():
                    poke.gender.is_male = False
                else:
                    poke.gender.is_male = None
                pokes.append(poke)
            return pokes
    return []

# Save Poké Bank to JSON
def save_poke_bank():
    with open(POKE_BANK_FILE, "w") as file:
        json.dump(
            [
                {
                    "id": poke.id,
                    "stats": poke.get_stats(),
                    "gender": "(m)" if poke.gender.is_male else "(f)" if poke.gender.is_male is False else "(?)"
                }
                for poke in poke_bank
            ],
            file,
            indent=4
        )

# Reset parents recursively
def reset_parents(poke):
    """Recursively reset parents for a Pokémon."""
    if poke.parent_male:
        reset_parents(poke.parent_male)
    if poke.parent_female:
        reset_parents(poke.parent_female)
    poke.parent_male = None
    poke.parent_female = None

# Similarity score calculation remains the same
def similarity_score(poke_base, root_parents):
    """
    Calculate the percentage of Pokémon in the tree that are present in the Poké Bank.
    """
    def collect_tree_pokemon(poke, collected):
        """Recursively collect all Pokémon in the tree."""
        if poke is None or poke in collected:
            return
        collected.add(poke)
        collect_tree_pokemon(poke.parent_male, collected)
        collect_tree_pokemon(poke.parent_female, collected)

    # Collect all Pokémon in the breeding tree
    tree_pokemon = set()
    for parent in root_parents:
        collect_tree_pokemon(parent, tree_pokemon)

    # Compare with Poké Bank
    matching_count = 0
    for poke in tree_pokemon:
        if any(
            poke.get_stats() == pb_poke.get_stats() and poke.gender.is_male == pb_poke.gender.is_male
            for pb_poke in poke_base
        ):
            matching_count += 1

    # Calculate percentage
    if not tree_pokemon:
        return 0  # Avoid division by zero
    return (matching_count / len(tree_pokemon)) * 100

# Function to match the breeding tree with the Poké Bank
def match_tree_with_pokebank(poke, pokebank):
    """Traverse the tree and match Pokémon with those in the Poké Bank."""
    # Create a copy of the Poké Bank to remove used Pokémon
    pokebank_copy = pokebank.copy()

    def normalize_stats(stats_str):
        """Normalize stats string by replacing '*' with '+' and stripping extra spaces."""
        return ' '.join(stats_str.replace('*', '+').split())

    def traverse_and_match(poke):
        if poke is None:
            return

        # Attempt to match this Pokémon with one in the Poké Bank
        poke_stats = normalize_stats(poke.get_stats())
        poke_gender = poke.gender.is_male

        matched_poke = None
        for pb_poke in pokebank_copy:
            pb_poke_stats = normalize_stats(pb_poke.get_stats())
            pb_poke_gender = pb_poke.gender.is_male

            if poke_stats == pb_poke_stats and poke_gender == pb_poke_gender:
                # Found a match
                matched_poke = pb_poke
                break

        if matched_poke:
            # Update the Pokémon's ID to match the Poké Bank Pokémon's ID
            poke.id = matched_poke.id
            # Remove the matched Pokémon from the Poké Bank copy to prevent reuse
            pokebank_copy.remove(matched_poke)

        # Recursively process parents
        traverse_and_match(poke.parent_male)
        traverse_and_match(poke.parent_female)

    traverse_and_match(poke)

# Visualization function updated to reflect IDs from the Poké Bank
def visualize_breeding_tree(poke, graph=None, wild_pokes=None, poke_bank=None):
    if graph is None:
        graph = Digraph(format="png", graph_attr={"rankdir": "TB"})
        wild_pokes = set()
        # Create a set of Poké Bank IDs for quick lookup
        pokebank_ids = set(pb_poke.id for pb_poke in poke_bank) if poke_bank else set()

    def traverse(poke):
        if poke is None:
            return

        # Check if the Pokémon's ID is in the Poké Bank IDs
        in_bank = poke.id in pokebank_ids

        # Create a label for the node
        poke_label = f"{poke.id}\\nStats: {poke.get_stats()}\\nGender: {poke.gender}"
        #if in_bank:
        #    poke_label += f"\\nIn Bank: {poke.id}"

        # Set node border color based on presence in Poké Bank
        node_color = "green" if in_bank else "black"
        node_style = "filled" if in_bank else "solid"
        fill_color = "lightblue" if in_bank else "white"

        graph.node(poke.id, poke_label, style=node_style, fillcolor=fill_color, color=node_color)

        if poke.parent_male and poke.parent_female:
            # Recursively process parents
            traverse(poke.parent_male)
            traverse(poke.parent_female)
            # Add edges after ensuring parents are processed
            graph.edge(poke.parent_male.id, poke.id)
            graph.edge(poke.parent_female.id, poke.id)
        else:
            # Wild Pokémon (no parents)
            wild_pokes.add((poke, in_bank))

    traverse(poke)
    return graph, wild_pokes

# Page 1: Manage the Poke Bank
def page_manage_poke_bank():
    st.title("Poke Bank Management")

    # Add Pokémon
    st.subheader("Add Pokémon")

    # Row of 6 toggles for stats and gender
    cols = st.columns(7)
    stat_labels = ["HP", "Atk", "Def", "Sp.Atk", "Sp.Def", "Spe"]
    stats = [cols[i].toggle(stat_labels[i], key=f"add_stat_{i}") for i in range(6)]
    gender = cols[6].selectbox("Gender", ["Male", "Female"], key="add_gender", label_visibility="collapsed")

    stats = ["+" if stat else "-" for stat in stats]
    gender_code = "(m)" if gender == "Male" else "(f)"

    if st.button("Add Pokémon to Bank"):
        poke_stats = " ".join(stats) + f" {gender_code}"
        try:
            new_poke = lib.Poke()
            new_poke.str_to_stats(poke_stats)
            poke_bank.append(new_poke)
            save_poke_bank()  # Persist the bank
            st.success(f"Added Pokémon: {poke_stats}")
        except Exception as e:
            st.error(f"Error: {e}")

    # Display current Pokémon in the bank
    st.subheader("Current Poke Bank")
    for poke in poke_bank:
        st.write(f"ID: {poke.id}")
        cols = st.columns(7)
        for i, stat in enumerate(poke.stats):
            cols[i].button(
                stat_labels[i],
                key=f"bank_{poke.id}_stat_{i}",
                disabled=not stat.is_31,
                use_container_width=True,
            )
        cols[6].write(f"Gender: {'Male' if poke.gender.is_male else 'Female'}")

    # Remove Pokémon
    if poke_bank:
        poke_to_remove = st.selectbox("Select Pokémon to Remove", options=[poke.id for poke in poke_bank])
        if st.button("Remove Pokémon"):
            poke_bank[:] = [poke for poke in poke_bank if poke.id != poke_to_remove]
            save_poke_bank()  # Persist the bank
            st.success(f"Removed Pokémon with ID: {poke_to_remove}")

# Page 2: Find Best Tree for a Target Pokémon
def page_find_best_tree():
    st.title("Find Best Breeding Tree")

    # Target Pokémon settings
    st.subheader("Target Pokémon Stats")
    cols = st.columns(7)
    stat_labels = ["HP", "Atk", "Def", "Sp.Atk", "Sp.Def", "Spe"]
    target_stats = [
        "+" if cols[i].toggle(stat_labels[i], key=f"target_stat_{i}") else "-"
        for i in range(6)
    ]
    target_gender = cols[6].selectbox("Gender", ["Male", "Female"], key="target_gender", label_visibility="collapsed")
    target_gender_code = "(m)" if target_gender == "Male" else "(f)"

    if st.button("Generate Best Tree"):
        target_poke_stats = " ".join(target_stats) + f" {target_gender_code}"
        try:
            target_poke = lib.Poke()
            target_poke.str_to_stats(target_poke_stats)

            # Reset parents before generating new ones
            reset_parents(target_poke)

            best_trees = []

            for _ in range(100):
                # Ensure a clean state for each attempt
                reset_parents(target_poke)
                target_poke.generate_random_parents(recursive=True)

                # After generating the tree, match with Poké Bank
                match_tree_with_pokebank(target_poke, poke_bank)

                # Root parents
                root_parents = [target_poke.parent_male, target_poke.parent_female]
                score = similarity_score(poke_bank, root_parents)

                # Save the tree and score
                tree_data = {
                    "poke": target_poke,
                    "score": score,
                    "graph": None
                }
                best_trees.append(tree_data)
                best_trees = sorted(best_trees, key=lambda x: x['score'], reverse=True)[:20]

            # Display the best tree
            best_tree = best_trees[0]
            best_graph, wild_pokes = visualize_breeding_tree(best_tree["poke"], poke_bank=poke_bank)
            best_graph.render("breeding_tree", format="png", cleanup=True)
            st.image("breeding_tree.png")
            st.write(f"Best Tree Similarity Score: {best_tree['score']}%")

            st.subheader("Wild Pokémon Required:")
            for wild_poke, in_bank in wild_pokes:
                bank_status = "[in Poké Bank]" if in_bank else ""
                st.write(f"ID: {wild_poke.id}, Stats: {wild_poke.get_stats()}, Gender: {wild_poke.gender} {bank_status}")
            
        except Exception as e:
            st.error(f"Error: {e}")

# Main Application
poke_bank = load_poke_bank()  # Load the bank at startup
st.sidebar.title("Poke Breeding Simulator")
page = st.sidebar.radio("Navigate", ["Manage Poke Bank", "Find Best Tree for Target Pokémon"])

if page == "Manage Poke Bank":
    page_manage_poke_bank()
elif page == "Find Best Tree for Target Pokémon":
    page_find_best_tree()