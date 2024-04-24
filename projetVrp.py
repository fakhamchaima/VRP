from docplex.mp.model import Model
import matplotlib.pyplot as plt
from tkinter import Frame
import numpy as np
from tkinter import Tk, Label, Entry, Button
from PIL import Image, ImageTk

nbVille = None
nbVehicules = None

def get_values():
    global nbVille1, nbVehicules
    nbVille1 = int(entry_clients.get())
    nbVehicules = int(entry_vehicules.get())
    # Ferme la fenêtre et continue avec le reste du code en utilisant les valeurs entrées par l'utilisateur
    root.destroy()

# Crée la fenêtre principale
root = Tk()
root.title("Entrée des valeurs")


image = Image.open("images/camio.jpg")
photo = ImageTk.PhotoImage(image)

# Crée un widget Label pour afficher l'image en arrière-plan
background_label = Label(root, image=photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

window_width = 300
window_height = 200
root.geometry(f"{window_width}x{window_height}")

# Crée un cadre pour contenir les éléments
frame = Frame(root)
frame.place(relx=0.5, rely=0, anchor='center')


# Crée les libellés et les champs de saisie pour les clients et les véhicules
label_clients = Label(root, text="Nombre de clients :")
label_clients.pack()
entry_clients = Entry(root)
entry_clients.pack()

label_vehicules = Label(root, text="Nombre de véhicules :")
label_vehicules.pack()
entry_vehicules = Entry(root)
entry_vehicules.pack()

# Crée le bouton pour valider les valeurs entrées
button_valider = Button(root, text="Valider", command=get_values)
button_valider.pack()

# Lance la boucle principale de l'interface
root.mainloop()



rnd = np.random
rnd.seed(0)

# Index Range ville
nbVille = nbVille1 + 1
ville = range(nbVille)

vehicules = range(nbVehicules)

# Coût entre les nœuds i et j
cij = rnd.rand(nbVille, nbVille)

# Demande de chaque client i
di = rnd.randint(1, 10, nbVille)
di[0] = 0

# Capacité de chaque véhicule k
qk = rnd.randint(0, 200, nbVehicules)

#qk = [10.1 , 80.1 , 110.1, 50]

print(qk)

# Coordonnées des villes
loc_x = rnd.rand(len(ville)) * 200 #[100,155,25,13,25,96,162] 
loc_y = rnd.rand(len(ville)) * 100 #[60,94,79,50,11,17,17]

for i in ville:
    plt.annotate('$D_%d=%.4f$' % (i, di[i]), (loc_x[i] + 2, loc_y[i]))

image = plt.imread("images/map.jpg")  
plt.imshow(image, extent=[0, 200, 0, 100]) 

plt.axis('equal')

model = Model('CVRP')

# Variables de décision
x = model.binary_var_cube(keys1=ville, keys2=ville, keys3=vehicules, name='x')
u = model.integer_var_matrix(keys1=ville, keys2=vehicules, lb=0, ub=nbVille, name='u')

# Fonction objectif
model.minimize(model.sum(cij[i, j] * x[i, j, k] for i in ville for j in ville for k in vehicules))

# Contraintes
for j in ville:
    if j > 0:
         model.add_constraint(model.sum(x[i, j, k] for i in ville for k in vehicules) == 1, ctname='cnt1')

for j in ville:
    for k in vehicules:
        model.add_constraint(model.sum(x[i, j, k] for i in ville) == model.sum(x[j, i, k] for i in ville), ctname='c2')

for k in vehicules:
    model.add_constraint(model.sum(x[0, j, k] for j in ville if j > 0) == 1, ctname='c3')

for k in vehicules:
    model.add_constraint(model.sum(di[j] * x[i, j, k] for i in ville for j in ville if j > 0) <= qk[k], ctname='c4')
   
for i in ville:
    for j in ville:
        if j > 0:
            for k in vehicules:
                model.add_constraint(u[i, k] - u[j, k] + (nbVille - nbVehicules) * x[i, j, k] <= (nbVille - nbVehicules - 1),
                                     ctname='c5')
print('solution')
solution = model.solve(log_output=True)

solution.display()
solution.get_objective_value()

A = [(i, j, k) for i in ville for j in ville for k in vehicules if i != j]
arcs_trajet = [a for a in A if x[a].solution_value > 0.9]

# Afficher le depot avec leurs images
img = plt.imread("images/depot.jpg")
img_width = 15 
img_height = 10
plt.imshow(img, extent=[loc_x[0] - img_width / 2, loc_x[0] + img_width / 2, loc_y[0] - img_height / 2, loc_y[0] + img_height / 2])

# Charger les images des clients
client_images = [plt.imread(f"images/client_{i}.jpg") for i in ville[1:]]

# Afficher les clients avec leurs images
for i in ville:
    if i > 0:
        img = client_images[i - 1]
        img_width = 6  # Largeur de l'image en unité de coordonnées
        img_height = 6  # Hauteur de l'image en unité de coordonnées
        plt.imshow(img, extent=[loc_x[i] - img_width / 2, loc_x[i] + img_width / 2, loc_y[i] - img_height / 2, loc_y[i] + img_height / 2])

colors = ['b', 'g', 'r', 'c', 'm', 'y']  # Liste des couleurs disponibles
# linestyle=[':','--',':','-.']    , linestyle = linestyle[k  % len(linestyle)]

for i, j, k in arcs_trajet:
    plt.plot([loc_x[i], loc_x[j]], [loc_y[i], loc_y[j]], c=colors[k  % len(colors)], alpha = 0.65 , linewidth=2.5 )


plt.axis('equal')

print('Numéro de véhicule')
for k in vehicules:
    for a in A:
        if x[a].solution_value > 0.9:
            if k == a[-1]:
                print(a[-1], '             ', a[0], '             ', a[1])
                
cout = f"Coût total du VRP : {solution.get_objective_value():.3f}"
plt.scatter(loc_x, loc_y, label=f"Clients : {nbVille1}")
#plt.scatter(loc_x, loc_y, label=f"Véhicules : {nbVehicules}")
for k in vehicules :
    plt.scatter(loc_x, loc_y, label=f"Quantité du véhicules {k+1}: {qk[k]}")
plt.scatter(loc_x, loc_y, label= cout)
plt.legend()
plt.show()