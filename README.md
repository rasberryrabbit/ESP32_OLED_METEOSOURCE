# ESP32_OLED_METEOSOURCE
  
1.3" oled display 128x64. sh1106 controller.  
  
ESP32  
3.3V   -- VCC  
GND    -- GND  
GPIO22 -- SCL  
GPIO21 -- SDA  
GPIO4  -- 1 wire DS18B20 (optional)  
GPIO35 -- Force enter config mode on Power up  
  
  
ESP32C3-SuperMini  
  
3.3V   -- VCC  
GND    -- GND  
GPIO9  -- SCL  
GPIO8  -- SDA  
GPIO0  -- 1 wire DS18B20 (optional)  
GPIO10 -- Force enter config mode on Power up  
  
  
It need "config.txt" with requiring following info.  
ssid=(wifi name)  
pass=(wifi pass)  
lat=(your location)  
lon=(your location)  
key=(meteosource appid)  
timezone=(timezone delta in hours, float)
  
  
