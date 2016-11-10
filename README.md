# Land Of Love

Un cube à l'ouverture de Blender,ici des cubes ...

![Land of Love](https://github.com/sergeLabo/lol/blob/master/Lol_1.png?raw=true)

###  Installation:
Sur Debian Jessie 8.5:

* Blender 2.72
* Python 3.4

#### Blender
En terminal:
 sudo apt-get install blender


#### Installation de twisted pour python 3.x
Les sources de twisted comprennent les versions pour python2 et python3.

##### Avec Git
Dans votre dossier projets, ouvrir un terminal:

 git clone https://github.com/twisted/twisted.git
 cd twisted
 sudo python3 setup.py install

#####En téléchargeant le zip
 https://github.com/twisted/twisted/archive/trunk.zip
 
Décompresser, dans le dossier:

 sudo python3 setup.py install

### Documentation

[Le wiki de ce projet sur Github](https://github.com/sergeLabo/lol/wiki)


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

 ./lol_public.sh
ou
 ./lol_optimus_public.sh

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
#### FSAA
##### Documentation

* [Bumblebee-Project Nvidia antialiasing 272](https://github.com/Bumblebee-Project/Bumblebee/issues/272)
* [Bumblebee-Project Nvidia antialiasing 296](https://github.com/Bumblebee-Project/Bumblebee/issues/296)
* [Primusrun sur Arch wiki](https://wiki.archlinux.org/index.php/bumblebee)

#### Anti Aliasing
optirun est capricieux, utiliser primusrun pour lancer le blenderplayer

Dans le *.blend, le moteur de rendu doit être Blender Game, puis dans la fenêtre Properties, Render Panel, Standalone Player, sélectionner:

* AA Samples = 8x

#### Primusrun vs optirun

* [Primusrun sur Arch wiki](https://wiki.archlinux.org/index.php/bumblebee#Primusrun)

### Bug

### Bonus: vérification de la prise en charge de l'AA par la carte Nvidia
Réglage de l'AA dans le .blend à 0 puis:
* export FSAA_MODE=7
* primusrun blender

Pas d'AA !! La carte Nvidia ne prends pas en charge l'AA avec bumblebee

### Valeur maximum pour l'AA
####SAA_MODE=14
    pierre@PC01:~$ export FSAA_MODE=14
    pierre@PC01:~$ primusrun blender
    ...
    /build/blender-5_gB1L/blender-.b+dfsg0/intern/ghost/intern/GHOST_WindowX11.cpp:253: oversampling requested 16 but using 8 samples
    ...

#### FSAA_MODE=7
    pierre@PC01:~$ export FSAA_MODE=7
    pierre@PC01:~$ primusrun blender
    ...
    /build/blender-5_gB1L/blender-.b+dfsg0/intern/ghost/intern/GHOST_WindowX11.cpp:253: oversampling requested 16 but using 8 samples
    ...

La valeur

    oversampling requested 16 but using 8 samples

vient de blender. Avec:
* AA Samples = 8x
il n'y a plus d'erreur !


### Merci à
* Labomedia
* Olivier B pour la première version en réseau
