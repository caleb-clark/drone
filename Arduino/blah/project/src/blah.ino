
float voltage_lvl = 5.1;

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
    
    
    float zero = analogRead(A5);
    float one = analogRead(A1);
    float two = analogRead(A2);
    float three = analogRead(A3);
  
    float zero_ = 100*(zero*voltage_lvl)/1024.0;
  
    float one_ = 100*(one*voltage_lvl)/1024.0;
  
    float two_ = 100*(two*voltage_lvl)/1024.0;
  
    float three_ = 100*(three*voltage_lvl)/1024.0;
  
    Serial.println(String((int)zero_) + " " + String((int)one_) + " " + String((int)two_) + " " + String((int)three_));
    
  
  
}
