#include <Arduino.h>

void setup();
void loop();
#line 1 "src/blah.ino"

float voltage_lvl = 5.075;

void setup()
{
   Serial.begin(115200);     //  opens serial port, sets data rate to 9600 bps
}


void loop()
{

//Conversion formula for voltage

  

  //String response;

  // This logic can be made into a boolean
  // supported by GPIOs
  
    
  //  response = Serial.readString();
    //Serial.println(response);
    
    
    float zero = analogRead(A0);
    float one = analogRead(A1);
    float two = analogRead(A2);
    float three = analogRead(A3);
  
    float zero_ = 10000*((zero*voltage_lvl)/1024.0);
  
    float one_ = 10000*((one*voltage_lvl)/1024.0);
  
    float two_ = 10000*((two*voltage_lvl)/1024.0);
  
    float three_ = 10000*((three*voltage_lvl)/1024.0);
  
    Serial.println(String((unsigned int)zero_) + " " + String((unsigned int)one_) + " " + String((unsigned int)two_) + " " + String((unsigned int)three_));
    
  
  
}
