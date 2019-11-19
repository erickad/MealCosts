# MealCosts
A GUI to calculate an approximation of the cost of making a recipe
using a list of ingredients and their costs with the recipe in question,
with the capability to dynamically add and edit the contents.

##Ingredients:
	Loads on start the file 'ingredients.txt' if present in same directory.
	Can be loaded and saved using the respective menu items.

##Recipes:
	Loads on start the files in directory '/Recipes/' if present in same directory
	but creates directory if not present.
	Can be loaded and saved using the respective menu items.
	New recipes are added using the 'New Recipe' menu item
	which opens a dialog to create the recipe with the values
	Name, Servings, Instructions
	Removal is done by the respective menu item and will also delete the
	file it is linked to in '/Recipes/'.

##Both Ingredient Contents and Recipe Contents:
	Can add items and remove items at the rownumber given in spinbox.
	They can be sorted in ascending or descending order.
	Edited dynamically using the table, however saving any contents
	to file for another time is done using the respective menu items.
