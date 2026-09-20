# Adding food photos

You export, I process. Steps:

1. **Open Photos** on your Mac. Tip: the search bar understands **“food”** — type it to surface most food shots fast. (Or make an album.)
2. **Select** the keepers, then **drag them into** this folder:
   `discountculinary/assets/img/incoming/`  (or File ▸ Export ▸ Export Unmodified Original).
3. **Name each file after the recipe** — the dish name is enough (HEIC is fine):
   e.g. `saag chicken.heic`, `Mexican Cottage Pie.jpg`. One photo per recipe (the best one).
4. Tell me, or run: `python3 add_photos.py` — it converts, resizes, places each on the right
   recipe, updates the SEO schema, and rebuilds. It reports anything it couldn’t match.

Multiple shots of one dish? Keep your favorite; name extras `saag chicken 2.heic` and I’ll pick.

## Recipe → filename to use
| Recipe | Name the file |
|---|---|
| Air Fryer Molten Lava Cakes | `Air Fryer Molten Lava Cakes` |
| Beef and Broccoli Stir Fry | `Beef and Broccoli Stir Fry` |
| Birria Chili | `Birria Chili` |
| Breakfast Tacos | `Breakfast Tacos` |
| Butter Chicken (WIP) | `Butter Chicken (WIP)` |
| Calzones | `Calzones` |
| Chipotle Feta Tuna Peppers | `Chipotle Feta Tuna Peppers` |
| Creamed Spinach Saag Pasta | `Creamed Spinach Saag Pasta` |
| Espagueti Verde | `Espagueti Verde` |
| Fond-Rescue Black Bean Soup | `Fond-Rescue Black Bean Soup` |
| Garlic-Herb Flatbreads | `Garlic-Herb Flatbreads` |
| Greek Yogurt Bagels | `Greek Yogurt Bagels` |
| Guanciale Carbonara with Fresh Fettuccine | `Guanciale Carbonara with Fresh Fettuccine` |
| High-Protein Calabrian Chicken Pasta | `High-Protein Calabrian Chicken Pasta` |
| High-Protein Pizza Dough | `High-Protein Pizza Dough` |
| Homemade Alfredo | `Homemade Alfredo` |
| Lasagna Soup | `Lasagna Soup` |
| Lime Sesame Toom Vinaigrette | `Lime Sesame Toom Vinaigrette` |
| Mexican Chicken Salad Bowl | `Mexican Chicken Salad Bowl` |
| Mexican Cottage Pie | `Mexican Cottage Pie` |
| Pan-Fried Turkey Dumplings | `Pan-Fried Turkey Dumplings` |
| Potato Wedge Taco Bowl | `Potato Wedge Taco Bowl` |
| Queso Fundido | `Queso Fundido` |
| Red Salsa | `Red Salsa` |
| Saag Chicken | `Saag Chicken` |
| Skyr Chipotle Crema | `Skyr Chipotle Crema` |
| Spaghetti alla Carbonara | `Spaghetti alla Carbonara` |
| Spicy Marinara / Pizza Sauce | `Spicy Marinara / Pizza Sauce` |
| Sushi Bake Tuna Handrolls | `Sushi Bake Tuna Handrolls` |
| Turkey Breakfast Sausages | `Turkey Breakfast Sausages` |
| Turkey Ragu | `Turkey Ragu` |
| White Bean Ragù Soup | `White Bean Ragù Soup` |
| Wisconsin-Style Onion Smash Sliders | `Wisconsin-Style Onion Smash Sliders` |
| Zucchini Bread | `Zucchini Bread` |

The photos on the site right now are stock shots (see `assets/img/SOURCES.md`). Each one is replaced the moment you add your own with the same recipe name.
