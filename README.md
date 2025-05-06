# A breeding calculator for PokeMMO

## Usage and setup
```shell
docker build -t pkmn .
docker run -p 8501:8501 pkmn
```

## How to use
![main page](https://raw.githubusercontent.com/morriartie/pkmmo_breed_calculator/refs/heads/main/images/main_page1.jpeg "Main page")

* Add the pokes you already have into the tab "Manage Poke Bank"

* On the tab "Find Best Tree for Target Poke" add the one you desire. The marked buttons means that this poke has 31 in this specific IV

## How to read the IV code:

On the the line "- + - - * -" each "-" means an IV that's not 31, while "+" means it has value 31.
The "*" symbol means it has value 31 and this poke should have an item equiped for preserving this IV.
The sequence is the same as in the game. That means: HP, Atk, Def, Sp.Atk, Sp.Def and Speed.
So in the example "+ * - - - +" , this poke has 31 iv in HP, Atk and Speed. And it has an item for preserving Atk when bred. 

Another example:

"+ + + + + -": this poke has 31 on all IVs but speed.
"* + + + + +": this has 31 in all IVs and an item held to preserve HP.
