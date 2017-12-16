
float voltage_lvl = 5.1;

void setup()
{
   Serial.begin(9600);     //  opens serial port, sets data rate to 9600 bps
}


void loop()
{

//Conversion formula for voltage

  

  String response;

  // This logic can be made into a boolean
  // supported by GPIOs
  if (Serial.available() > 0) {
    
    response = Serial.readString();
    Serial.println(response);
    if (response == "GET") {
    
    int zero = analogRead(A0);
    int one = analogRead(A1);
    int two = analogRead(A2);
    int three = analogRead(A3);
  
    float zero_ = (zero*5.131)/1024.0;
  
    float one_ = (one*voltage_lvl)/1024.0;
  
    float two_ = (two*voltage_lvl)/1024.0;
  
    float three_ = (three*voltage_lvl)/1024.0;
  
    Serial.println(String(zero_) + " " + String(one_) + " " + String(two_) + " " + String(three_));
    }
  }
  
}
