#last updated: 4/16/21
import json
import os
import sys


#----------------------------------------------
#MAIN

#JSON file of all the recipes
recipe_file = "2021-01-09_14-14-16.json"
#a dictionary of Items
item_fluid_dict = {}
recipe_dict = 0

#read file
print("Starting to read from file...", recipe_file)
with open(recipe_file,'r', errors = 'replace') as json_file:
    recipe_dict = json.load(json_file)
print("Completed file reading.")


#Item/Fluid Class
class item_fluid_class:
    def __init__ (self, uN, lN):
        self.uN = uN
        self.lN = lN
        self.output_in = {}
        self.input_in = {}
    

#Adds a recipe to a dictionary with key item local name
#type 0 means input, type 1 means output
def add_item_fluid(item, recipe, machine_name, is_used):#FIX:add shapped crafting

    if (item != None):#some shapeless recipes have no input type
        if (item['lN'] in item_fluid_dict):#if the item is in the dictionary
            if is_used:
                if machine_name in item_fluid_dict[item['lN']].input_in:
                    item_fluid_dict[item['lN']].input_in[machine_name].append(recipe)
                else:
                    item_fluid_dict[item['lN']].input_in[machine_name] = [recipe]
            else:
                if machine_name in item_fluid_dict[item['lN']].output_in:
                    item_fluid_dict[item['lN']].output_in[machine_name].append(recipe)
                else: 
                    item_fluid_dict[item['lN']].output_in[machine_name] = [recipe]
        else: #if the item is not in the dictionary yet
            item_holder = item_fluid_class(item['uN'], item['lN'])#unseen before items wont have a machine yet
            if is_used:
                item_holder.input_in[machine_name] = [recipe]
            else:
                item_holder.output_in[machine_name] = [recipe]

            item_fluid_dict[item['lN']] = item_holder#make a new dictionary entry

def index():
    #itterate through recipes
    print("Starting to index...")
    for recipeType in recipe_dict['sources']:
        if (recipeType['type'] == 'shaped' or recipeType['type'] == 'shapeless'):
            for rec in recipeType['recipes']:
                add_item_fluid(rec['o'], rec, recipeType['type'], 0)#item out
                for item in rec['iI']:
                    add_item_fluid(item, rec, recipeType['type'], 0)#item in

        if (recipeType['type'] == 'gregtech'):#HARDCODED: gregtech like recipies due to iI, fI, iO, fO constraints
            for machine in recipeType['machines']:
                for rec in machine['recs']:
                    for item in rec['iI']:#item in
                        add_item_fluid(item, rec, machine['n'], 0)
                    for item in rec['fI']:#fluid in
                        add_item_fluid(item, rec, machine['n'], 0)
                    for item in rec['iO']:#item out
                        add_item_fluid(item, rec, machine['n'], 1)
                    for item in rec['fO']:#fluid out
                        add_item_fluid(item, rec, machine['n'], 1)

    print("Completed Indexing.")#that'll do pig
    return(item_fluid_dict)