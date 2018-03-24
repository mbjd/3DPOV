# 3DPOV


This is the github repo for my 3D persistence of vision display. Here you
can find the arduino/teensy source code (`./code/`), eagle schematic and
board files (`./Eagle/`), and the python program I wrote to simplify the
creation of images containing simple shapes (`./image_creation/`).

### Summary

This was my Matura project (the end of (the equivalent of) high school in
Switzerland), and I did most of the work in the second half of 2014. You
can find various more detailed reports below, but here's a quick summary:

The display itself consists of 10 LED rows mounted in a double-helix
arrangement. Each of them contains 16 RGB LEDs driven by three shift
registers, for a total of 480 LEDs or 160 Pixels.

The shift registers are controlled by a Teensy 3.1 microcontroller board
using an SPI bus (All 30 shift registers are daisy chained together). The
controller is mounted on a wooden disc below the ten LED boards.

All of this is mounted on a 4mm steel shaft, supplied with 3.3V DC using
two copper slip rings, and spun up to 60 Hz by a brushed DC motor. A hall
sensor and a magnet enable the controller to measure the rotational speed
and to adjust its timing, so that the image always stays still despite the
speed not being quite constant. The image is updated 100 times per
revolution, or 6000 times a second.

Currently there's no way to supply images at runtime, the display has to be
stopped so that a new program can be uploaded using the Teensy's USB port.

### Various versions of the paper

[Original in German](http://tiny.cc/3DPOV)

[English long version, not quite finished](https://github.com/mbjd/english-paper/blob/master/paper.pdf)

[English short version](https://github.com/mbjd/english-paper/blob/master/paper-short.pdf)

[Other english stuff](https://github.com/mbjd/english-paper)

### Videos

[one](https://www.youtube.com/watch?v=bCETWNgBxbI) [two](https://www.youtube.com/watch?v=-gFsKhf5J-I)

### Press etc

[Hackaday article](http://hackaday.com/2016/11/16/spinning-3d-pov-display-as-a-high-school-term-project/)

[ETHZ D-ITET in German](https://www.ee.ethz.ch/de/news-und-veranstaltungen/d-itet-news-channel/2016/09/d-itet-student-gewinnt-forschungs-preis-.html) or [English](https://www.ee.ethz.ch/news-and-events/d-itet-news-channel/2016/09/d-itet-student-wins-research-award.html)

[Swiss Youth in Science article](http://web.archive.org/web/20161117130814/http://sjf.ch/eucys-2016-eth-student-gewinnt-forschungs-preis-am-ersten-studientag/)

[EUCYS 2016 link](http://eucys2016.eu/development-of-a-3d-display/)

### Links to discussion

[one](http://www.reddit.com/r/electronics/comments/2m6apx/finally_my_led_board_works_had_to_make_a_little/) [two](http://www.reddit.com/r/electronics/comments/2nrek4/almost_working_3d_pov_display/) [three](http://www.reddit.com/r/electronics/comments/2q9sg6/my_3d_pov_in_action_as_promised/)

### Photos

![Photo of it in action](/images/running.jpeg)

![Photo of it standing still](/images/still.jpeg)

![Me at EUCYS 2016 being super happy](/images/eucys-stand.jpeg)
