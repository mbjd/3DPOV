3DPOV
=====

Arduino sketch for my 3-dimensional persistence of vision display (runs on a Teensy 3.1). It does rotational sync using a hall sensor. Every time the hall sensor passes the magnet, an interrupt is triggered and the rotational period is measured. A timer is started that runs 100x faster than the rotational period, so that the LEDs are updated 100 times per full revolution. At each update, the program figures out where each LED row is and provides them with the image data for that location using SPI.

There's also a python program (mkmodel.py) that automates the creation of images. You can draw lines, spheres, cuboids, surfaces or connect an arbitrary amount of points. Then the whole image is converted to a program that can be uploaded on the teensy 3.1.

[Matura paper (German)](http://tiny.cc/3DPOV)

[Matura paper (English, WIP)](https://github.com/mbjd/english-paper/blob/master/paper.pdf)

[Shorter version in English](https://github.com/mbjd/english-paper/blob/master/paper-short.pdf)

[Other english stuff](https://github.com/mbjd/english-paper)

Videos of it in action: [1](https://www.youtube.com/watch?v=bCETWNgBxbI) [2](https://www.youtube.com/watch?v=-gFsKhf5J-I)


Some links to discussion: [1](http://www.reddit.com/r/electronics/comments/2m6apx/finally_my_led_board_works_had_to_make_a_little/) [2](http://www.reddit.com/r/electronics/comments/2nrek4/almost_working_3d_pov_display/) [3](http://www.reddit.com/r/electronics/comments/2q9sg6/my_3d_pov_in_action_as_promised/)

![Photo of it in action](http://imgur.com/weyXNIT.jpg)

![Photo of it standing still](http://imgur.com/SMb0HIS.jpg)
