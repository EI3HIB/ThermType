# ThermType & TermType

Basic code to print JS8Call logs to the terminal and/or a thermal printer.

- TermType only prints slected text to the terminal (requires termcolor module)
- ThermType prints selected text to a thermal printer and the terminal (requires termcolor and adafruit_thermal_printer modules)

The code is very basic as I am just learning as I go along. 

The thermal printer I'm using is from:
https://shop.pimoroni.com/products/mini-thermal-printer?variant=28412531207

My next steps are to try and see if I can get it working with the JS8Call API for better message handling capabilities.

The idea behind this is to captur, record & show relevant JS8Call traffic of interest.

With minor adjustments the code should easily lend itself to monitoring Direwolf (e.g. APRS messages) and perhaps PAT (e.g. email notification).
![working](https://user-images.githubusercontent.com/120377036/207146712-1145ed90-e14a-4da9-853f-27035d58a370.jpg)
![terminaloutput](https://user-images.githubusercontent.com/120377036/207146739-9e26c922-dd10-4662-9911-67e45bab7b20.png)
