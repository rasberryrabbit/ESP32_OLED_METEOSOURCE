# ESP32_OLED_METEOSOURCE
  
1.3" oled display 128x64. sh1106 controller.  
Or support waveshare 1.54" e-paper via SPI(optional).  
  
ESP32  
3.3V   -- VCC  
GND    -- GND  
GPIO22 -- SCL  
GPIO21 -- SDA  
GPIO32  -- 1 wire DS18B20 (optional)  
GPIO5 -- Force enter config mode on Power up  
(SPI)  
GPIO14 -- SCK  
GPIO13 -- MOSI  
GPIO18 -- CS  
GPIO33 -- DC  
GPIO23 -- RESET  
GPIO4 -- BUSY  
  
  
  
ESP32C3-SuperMini  
  
3.3V   -- VCC  
GND    -- GND  
GPIO9  -- SCL  
GPIO8  -- SDA  
GPIO0  -- 1 wire DS18B20 (optional)  
GPIO10 -- Force enter config mode on Power up  
(SPI)  
GPIO4 -- SCK  
GPIO6 -- MOSI  
GPIO20 -- CS  
GPIO3 -- DC  
GPIO2 -- RESET  
GPIO1 -- BUSY  
  
  
It need "config.txt" with requiring following info.  
ssid=(wifi name)  
pass=(wifi pass)  
lat=(your location)  
lon=(your location)  
key=(meteosource appid)  
timezone=(timezone delta in hours, float)
  
  
