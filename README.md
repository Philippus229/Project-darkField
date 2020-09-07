# Project Dark Field
VR version discontinued due to difficulties with DIY production of suitable microlens arrays.
Follow-up project with hopefully better results: https://github.com/Philippus229/Blurred-Reality

## Microlens Arrays
### Materials
- <a href="https://drive.google.com/file/d/1PlxRQuGCLu4TIZ7XadgTyJTzmsP_d1dS/view?usp=sharing">3D model</a> (print at 1.005x scale due to resin shrinkage)
- 1014pcs 1/16" metal spheres
- mold-making silicone
- some clear resin (f.e. Anycubic Clear UV Resin)

### Procedure
Print the model on a resin printer of your choice, insert the metal spheres and slowly pour in the silicone. Cover the mold with something theat the silicone will stick to and let it cure. Then just remove the 3D printed mold and metal spheres (maybe also remove excessive silicone) and you're left with a nice MLA mold. Now you can use this mold to make four identical microlens arrays which you can later assemble into a single big MLA.

## Hardware
- 2K LCD (LS055R1SX04) with driver board from AliExpress (~60$) (there's also a 4K version for >100$)
- Raspberry Pi 4 Model B (2GB RAM) (just had to use this because my PC doesn't have an HDMI ouput)

## Software
**TODO:** program descriptions

### Screenshots, etc.
**Raymarcher demo scene #2**
![demo_scene_1](/software/python/render.png)

**MPI2DF (test000)**
![test000-out](/software/python/test000-out.png)

## TODO
- proper tutorial with pictures
- better and more useful software
