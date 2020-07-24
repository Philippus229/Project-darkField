# Project darkField
VR version discontinued due to difficulties with DIY production of suitable microlens arrays.
Follow-up project with hopefully better results: https://github.com/Philippus229/Blurred-Reality

## Microlens Arrays
While experimenting around I realized that, while unsuitable for VR, the microlens arrays worked pretty well for making normal (not near-eye) light field displays.<br/>
**How I made them:** I used 1000 1/16" steel balls from ebay along with a 3D printed <a href="https://www.tinkercad.com/things/1YWJrtPxQ6g-terrific-hango-jofo">hexagonal container</a> (printed with ELEGOO Mars) to make a silicone mold that could then be used to make the actual microlens arrays (clear resin from ELEGOO, 1mm thickness (in this case you'll have to adjust it using some clear plastic film))

**Notes:** First put in the steel balls, then slap some silicone on top that will stick to whatever you decide to use to cover it up but not to the metal spheres or the 3D printed part. I just used some clear silicone that we had at home and the transparent part of a CD case which I roughened on one side with some sandpaper to help the silicone stick. Then I just put it in a bench vice over night and removed the steel balls from the finished mold by rubbing the exposed side with my thumb (bad idea, should've probably used something like an eraser instead) to losen them and to remove some of the silicone covering them (they'll just fall out at some point and you can clip off the unwanted silicone with some pliers (f.e. the ones that come with the ELEGOO Mars))

## Hardware
- 2K LCD (LS055R1SX04) with driver board from AliExpress (~60$) (there's also a 4K version for >100$)
- Raspberry Pi 4 Model B (2GB RAM) (just had to use this because my PC doesn't have an HDMI ouput)

## Software
Probably gonna fix the Minecraft thing at some point, but for now I wrote a raymarcher for the display and it works much better than expected (pictures coming soon). The raymarcher was just meant for testing purposes, I'm probably going to make a Unity plugin similar to the one for The Looking Glass next (or a depth media viewer).

### Screenshots, etc.
**Raymarcher demo scene #2**
![demo_scene_1](/software/python/render.png)

## TODO
- proper tutorial with photos
- better and more useful software
