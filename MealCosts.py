#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classes to hold ingredients, recipes and recipe contents and the methods
to manipulate, create and remove them.
"""
import json #Read/write files with json structure
import os #Check path/directory existance and creation

class MealList:
    """
    Main class that holds a list of ingredients and a list of recipes
    and the methods to interact with them.
    """
    def __init__(self):
        """
        Starts with empty ingredients and recipes.
        """
        self.ingredients = []
        self.recipes = []

    def addIng(self, aI):
        """
        Adds an ingredient aI [string, double] to ingredients.
        """
        if len(aI)==2 and isInstance(aI, list):
            if isInstance(aI[0],string) and isInstance(aI[1],double):
                        self.ingredients.update(aI)
                        return True
        return False

    def removeIng(self, keys):
        """
        Removes ingredients with their name contained in keys.
        """
        if isInstance(keys, list):
            self.ingredients = [i for i in self.ingredients if i[0] not in keys]
            return True
        return False

    def printIng(self):
        """
        Prints current ingredients to console.
        """
        if len(self.ingredients) == 0:
            print("Empty")
        [print("%s: %.2f (per kg or l)" %(i,p)  )
            for i,p in self.ingredients]

    def readIngredients(self):
        """
        Reads ingredients from 'ingredients.txt' contained in same directory.
        """
        try:
            with open('ingredients.txt', 'r') as f:
                self.ingredients = json.load(f)
        except:
            print("File \'ingredients.txt\' not present or has errors.")
        return

    def writeIngredients(self):
        """
        Writes ingredients to 'ingredients' in same directory.
        """
        with open('ingredients.txt', 'w') as f:
            json.dump(self.ingredients, f)
        return

    def addRecipe(self, rec):
        """
        Adds a recipe to MealList's recipes if not already present.
        """
        if rec.name not in [rn.name for rn in self.recipes ]:
            self.recipes.append(rec)
            return True
        else:
            print('%s already present' %rec.name)
            return False

    def readRecipes(self):
        """
        Reads recipes from the '/Recipes/' directory.
        """
        if not os.path.exists("Recipes"):
            os.mkdir("Recipes")
        for fn in os.listdir("./Recipes"):
            with open('./Recipes/%s'%fn,'r') as f:
                tD = json.load(f)
                r = Recipe(tD['Name'], self, tD['Contents'], tD['Serv'],
                    tD['Instructions'])
                self.addRecipe(r)
        return

    def writeRecipes(self):
        """
        Writes all recipes using writeRecipe().
        """
        for r in self.recipes:
            r.writeRecipe()
        return

    def printRecipes(self):
        """
        Prints all recipes.
        """
        print('-----')
        for r in self.recipes:
            r.printRecipe()
            print('-----')
        return

    def getRecipe(self, name):
        """
        Returns a recipe object with same name given if present.
        """
        for r in self.recipes:
            if r.name == name:
                return r
        return None

    def removeRecipe(self, name):
        """
        Removes a recipe with given name from MealList's recipes if present.
        """
        r = self.getRecipe(name)
        if not r is None:
            del self.recipes[self.recipes.index(r)]
            return True
        return False

class Recipe:
    """
    A class to hold recipe contents
    """
    def __init__(self, name, mList, cont, serv, instr):
        """
        Creates a recipe with name, parent, contents, servings and instructions.
        """
        self.name = name
        self.mList = mList
        self.contents = cont
        self.cost = 0.0
        self.serv = serv
        self.instr = instr

    def recSubIng(self):
        """
        Determines if recipe ingredients are a subset of MealList's ingredients.
        """
        if set([i for i,a in self.contents]) <= set([i for i,c in self.mList.ingredients]):
            return True
        else:
            return False

    def calcRecipeCost(self):
        """
        Calculates the cost of the recipe if recipe is possible.
        """
        lacking = []
        if not (self.recSubIng()):
            for item in [i for i,a in self.contents]:
                if item not in [i for i,c in self.mList.ingredients]:
                    lacking.append(item)
            return lacking
        total = 0
        for item,amount in self.contents:
            ind = [y[0] for y in self.mList.ingredients].index(item)
            per = self.mList.ingredients[ind][1]
            total += per*amount
        self.cost = total
        return lacking

    def addToRecipe(self, cont):
        """
        Adds an ingredient to recipe
        """
        self.contents.append(cont)
        self.calcRecCost()
        return

    def editRecipe(self, ind, val):
        """
        Sets the value of a recipe index to the given value.
        """
        self.contents[ind] = val
        self.calcRecCost()
        return

    def removeFromRecipe(self, ind):
        """
        Removes the ingredient at given index from recipe.
        """
        del self.contents[ind]
        self.calcRecCost()
        return

    def printRecipe(self):
        """
        Prints the recipe contents to console.
        """
        print("Recipe: %s  - Cost: %f " % (self.name, self.cost))
        print(self.contents)
        print(self.instr)
        return

    def toJson(self):
        """
        Converts Recipe to .json string format.
        """
        jsonified = {'Name':self.name, 'Contents':self.contents,
         'Serv':self.serv, 'Instructions':self.instr}
        return jsonified

    def writeRecipe(self):
        """
        Writes the recipe to the recipe directory in .json format
        """
        with open('./Recipes/%s.txt' % self.name, 'w') as f:
            json.dump(self.toJson(), f)
        return
