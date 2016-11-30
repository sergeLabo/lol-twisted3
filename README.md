# Land Of Love

Un cube à l'ouverture de Blender,ici des cubes ...

![Land of Love](https://raw.githubusercontent.com/sergeLabo/lol-twisted3/master/Lol_1.png)

### TODO

* irc avec twisted 3 sur server

### Testé sur

Debian Jessie 8.3 avec Blender 2.72

### Installation
#### Blender

~~~text
sudo apt-get install blender
~~~

#### Installation de twisted pour python 3
##### Dépendances

~~~text
sudo apt-get install python3-dev python3-setuptools
~~~

##### Install

Les sources de twisted comprennent les versions pour python2 et python3.

Télécharger les sources à https://github.com/twisted/twisted

Dans le dossier, ouvrir un terminal:

~~~text
sudo python3 setup.py install
~~~

ou

Dans votre dossier projets, ouvrir un terminal:

~~~text
git clone https://github.com/twisted/twisted.git
cd twisted
sudo python3 setup.py install
~~~

### Documentation

[Le wiki de ce projet sur Github](https://github.com/sergeLabo/lol-twisted3/wiki)


### License

Land Of Love  is licensed under the Creative Commons Attribution 3.0 Unported License.

To view a copy of this license, visit: http://creativecommons.org/licenses/by/3.0/

or send a letter to

Creative Commons
444 Castro Street
Suite 900
Mountain View
California, 94041
USA.

All sripts are under GNU General Public License Version 2

### Comment lancer LandOfLove ?
Ouvrir un terminal dans le dossier lol
~~~text
 ./lol_public.sh
~~~
ou
~~~text
 ./lol_optimus_public.sh
~~~

### Help

* Vue FPS: NumPad 8
* Déplacement dans la scène: déplacement de la souris et molette pour avancer reculer
* Désactivation de la vue FPS: NumPad 2
* Ajout d'un cube: Clic Gauche
* Suppression d'un cube: Clic droit
* Déplacement du curseur: Flèches gauche droite haut bas
* Déplacement du curseur vers le haut et le bas: recul et avance de la souris
* Destruction d'une pile entière: X
* Vue de dessus: activation NumPad 4, désactivation NumPad 6

### Anti Aliasing avec Optimus
#### Documentation

* [Bumblebee-Project Nvidia antialiasing 272](https://github.com/Bumblebee-Project/Bumblebee/issues/272)
* [Bumblebee-Project Nvidia antialiasing 296](https://github.com/Bumblebee-Project/Bumblebee/issues/296)
* [Primusrun sur Arch wiki](https://wiki.archlinux.org/index.php/bumblebee)

#### Anti Aliasing
optirun est capricieux, utiliser primusrun pour lancer le blenderplayer

Dans le *.blend, le moteur de rendu doit être Blender Game, puis dans la fenêtre Properties, Render Panel, Standalone Player, sélectionner:

* AA Samples = 8x

#### Primusrun vs optirun

* [Primusrun sur Arch wiki](https://wiki.archlinux.org/index.php/bumblebee#Primusrun)


### Merci à
* Labomedia
* Olivier B pour la première version en réseau
