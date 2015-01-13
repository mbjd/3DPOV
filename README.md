_3DPOV
======

Arduino sketch for my 3-dimensional persistence of vision display (runs on a Teensy 3.1). It does rotational sync using a hall sensor. Every time the hall sensor passes the magnet, an interrupt is triggered and the rotational period is measured. A timer is started that updates the LEDs 100 times per full revolution. Each time, two for loops get the right data from byteArray and update the LED drivers (TLC5927) using SPI.

Some links to discussion:
http://www.reddit.com/r/electronics/comments/2m6apx/finally_my_led_board_works_had_to_make_a_little/
http://www.reddit.com/r/electronics/comments/2nrek4/almost_working_3d_pov_display/
http://www.reddit.com/r/electronics/comments/2q9sg6/my_3d_pov_in_action_as_promised/