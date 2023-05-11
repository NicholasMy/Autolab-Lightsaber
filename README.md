# Autolab Lightsaber

### A physical Lightsaber that displays the stress level of Autolab

## Installation

### Server

The server is incredibly easy to run with Docker.

1. Edit `server/config.py` to your liking. The most important thing to change the number of LEDs to the number of
   VIRTUAL LEDs on the physical lightsaber.
2. Copy or rename `server/secret.py.template` to `server/secret.py` and fill in the values.
3. Run `docker compose up --build -d` in the root directory of this repository.
4. The server should now be running on port 6333 bound to your host. You can connect to http://localhost:6333/ in a
   browser to test it.
5. By default, you'll need to provide a reverse proxy with SSL. I recommend Nginx, but covering that is outside the
   scope of this project. Without a reverse proxy, you'll need to disable "secure" on the WebSocket connection in the
   Arduino sketch:

```c++
// Towards the top of hardware/lightsaber.ino
WiFiClient wifiClient;
WebSocketClient ws(true); // Secure (use SSL)

WiFiClient wifiClient;
WebSocketClient ws(false); // Insecure (don't use SSL)
```

### Hardware

I used an ESP8266, but any similar microcontroller should work.

1. Open `hardware/lightsaber.ino` in the Arduino IDE.
2. Edit the `host`, `wsPort`, `wirelessSsid`, and `wirelessPassword` variables to match your server config and WiFi
   network.
3. Edit the `NUM_LEDS` variable to the PHYSICAL number of LEDs on the lightsaber.
4. Edit the `LED_FOLD_1` variable to be the final LED in the first segment of your LED strip with 2 folds, so it
   overlaps 3 times. For example, if your LED strip is 100 LEDs long, and you have 2 folds, you would set this to 33. If
   you have a different hardware configuration (such as different offsets than mine), it will require modifying
   the `getPhysicalLedNumber` function.
5. The default pin for the LED strip's data line is 5 (D1 on the ESP8266). Change this if necessary
   via `#define LED_PIN`. Several examples are provided and commented out.
6. You'll need to use [my custom fork](https://github.com/NicholasMy/esp8266-websocketclient) of the ESP8266
   WebSocket Library. The original one doesn't handle HTTP headers correctly, so it's unlikely to work. It also requires
   SSL certificate verification, which I disabled for the purposes of this project. The minimal risk isn't worth the
   hassle of reflashing the ESP8266 every time the SSL certificate expires. Download my fork as a Zip archive from
   GitHub. In the Arduino IDE, go to `Sketch > Include Library > Add .ZIP Library...` and select the zip file you just
   downloaded.
7. Connect your microcontroller and click the upload button in the Arduino IDE.
8. Wait for that to finish, and you're all set! If you look at the serial output, you should see "Connected to
   websocket!" once everything is working.

### TODO

* Program lighting animations
* Add photos of the hardware
* Add more details about the physical build
* Add 3D printable parts
