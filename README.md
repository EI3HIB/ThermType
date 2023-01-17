# ThermType & TermType

Basic code to print JS8Call logs to the terminal and/or a thermal printer - the idea is to capture & record relevant JS8Call traffic of interest.

  - TermType.py prints selected text to the terminal & plays sounds (requires termcolor & pygame modules)

  - ThermType.py prints selected text to a thermal printer and the terminal (requires termcolor and adafruit_thermal_printer modules)
    it also can illuminate LEDs and play sounds (requires pygame module) based on the messages received. This is being done with a Raspberry Pi 4, with the     printer and LEDs all connected to the GPIO header pins
    
  - ThermType-ESCPOS-Testing.py is a version designed to operate using generic thermal receipt printers over USB - this is in early testing and does not       include the code for Serial printers, playing sounds, blinking LEDs etc. 

    You will need to update:
    conn = USBConnection.create('28e9:0289,interface=0,ep_out=3,ep_in=0') # with your own printer identifier (e.g. 28e9:0289)
    And point:
    logfile = open("/home/daithi/.local/share/JS8Call/DIRECTED.TXT","r", encoding="ascii", errors="ignore") # to your own DIRECTED.TXT location

The code is *very* basic - I am just learning Python as I go along. 

The thermal printer I'm using is from:
https://shop.pimoroni.com/products/mini-thermal-printer?variant=28412531207

Currently the code works by monitoring JS8Call's DIRECTED.TXT file. My next steps are to try and see if I can get it working with the JS8Call API for better message handling capabilities.

With minor adjustments the code could perhaps lend itself to monitoring Direwolf (e.g. APRS messages) and perhaps PAT (e.g. email notification).

![working](https://user-images.githubusercontent.com/120377036/207146712-1145ed90-e14a-4da9-853f-27035d58a370.jpg)
