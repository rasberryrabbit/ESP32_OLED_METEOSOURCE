# ESP32_OLED_METEOSOURCE
  
1.3" oled display 128x64. sh1106 controller.  
  
ESP32  
3.3V -- VCC  
GND  -- GND  
D4   -- SCL  
D5   -- SDA  
D18   -- 1 wire DS18B20 (optional)
D19   -- Force enter config mode    
  
  
ESP32C3-SuperMini  
  
3.3V -- VCC  
GND  -- GND  
D5   -- SCL  
D6   -- SDA  
D7   -- 1 wire DS18B20 (optional)  
D8   -- Force enter config mode  
  
  
It need "config.txt" with requiring following info.  
ssid=(wifi name)  
pass=(wifi pass)  
lat=(your location)  
lon=(your location)  
key=(meteosource appid)  
timezone=(timezone delta in hours, float)
  
  
