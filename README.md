# sebi-measurements

## tools/advantest_r3265a_load_basic_file.py
Saves the given BASIC program to the Advantest R3265A/R3271A See Controller Function OPERATION MANUAL

## procedures/hp437b_sensor_data_write.py
Writes the given sensor data to the HP437B power meter. Example files can be seen in calibration/*

## procedures/hp8720a_validate_output_power.py
Needs a HP 8720A and a HP 437B and this will sweep the frequency of the VNA and measure the output power.

## tools/advantest_r3265a_picture_splash.py
Hacky python script that will resize a picture, color it monochrome and then write it via 'GPOINT' instructions to the
Advantest R3265A.

## tools/load_calkit_hp8720a.py
Store a calibration kit defined by the user into a HP 8720A VNA.
Very crude asserts and nearly no error checking. But works with the sample file in 
calibration/kirkby_0776.json
You have to change the path to the used json manually and the VISA communictation string too.
Maybe I'll extend it in the future.