import time
import sys
from sensor_library import *
import gpiozero
from gpiozero import LED 
from gpiozero import Button

#variables for our force sensors and output devices
var1 = Force_Sensing_Resistor(0)
var2 = Force_Sensing_Resistor(1)
var3 = Force_Sensing_Resistor(2)
var4 = Force_Sensing_Resistor(3)

red_led = LED(20)
yellow_led = LED(16)
green_led = LED(21)
button = Button(12)

red_on = False
contrecoup_count = 0


#----------------Task 1----------------

def status():
    #This function allows the device to turn on once the button is pressed
    while True:
        if button.is_pressed == False:
            green_led.on()
            print ("Hello! The device is now ON and READY!")
            print("GREEN light is now ON!")
            break
        
            
def off(max_force, force_counter):
    #This function allows the device to turn off once the button is pressed while the device is running
    global contrecoup_count
    
    if button.is_pressed == False:
        green_led.off()
        yellow_led.off()
        red_led.off() #We turn off all the lights since we don't know which light will be on when the user turns it off
        while True:
            
            ask = input("Do you wish to access the data of the player? (Yes / No): ") #Ask the user if they would like a summary generated
        
            if ask.lower() == 'yes':
                print("\n--------------------------PLAYER SUMMARY--------------------------") #A summary is generated for medical professionals to review to aid in their diagnosis
                print ("\nThe maximum force experienced during the game:", max_force,"N")
                print ("The player has experienced a total of", contrecoup_count, "contrecoup injuries")
                print ("The total sum of the threshold counter is: ", force_counter, "N")
                break
            
            elif ask.lower() == 'no':
                print ("Good Game! Have a nice day and play safe :) ")
                break
            
        print("Goodbye! The device is now OFF!")        
        sys.exit() #Ends the program
                

#----------------Task 2----------------

def average(data1, data2, data3, data4):
    #This function calculates the average value for the last 3 data points in the raw force data
    #A list from each sensor is passed on to this function as an argument
    if len(data1) >= 3:
        average = []
        for force in [data1, data2, data3, data4]:
            average_value = round((force[-1] + force[-2] + force[-3])/3,1)
            average.append(average_value)
            
        return average #Returns the a 4-item list representing the moving average values for each force sensor

def threshold(value):
    #This function assigns a threshold force value for a new game
    #The "value" that is being passed on to this function is a rating that ranges from 1-5 by the medics from the previous game
    #Higher the value, the lower the threshold force value
    if value == 1:
        standard1 = 100 #Arbitrary number for the purpose of the range of the force sensor
    elif value == 2:
        standard1 = 95
    elif value == 3:
        standard1 = 90
    elif value == 4:
        standard1 = 85
    elif value == 5:
        standard1 = 80

    standard2 = int(standard1*10)
    standard3 = int(standard2*(2/3))

    #Standard 1 is the threshold force value for a single impact
    #Standard 2 is the threshold force value for a sequence of impacts
    #Standard 3 is the warning threshold force value that notifies that the force counter has almost reached Standard 2

    return standard1, standard2, standard3

def medics_info():
    #This function returns 3 threshold values that correspond to the rating given by the medics
        while True:
            try:
                value = int(input("What is the value given by the medics? (1-5): "))
                threshold1, threshold2, threshold3 = threshold(value)
                print ("Your maximum threshold upon single impact for this game is: ", threshold1, "N")
                print ("Your maximum threshold upon sequence of impact for this game is: ", threshold2, "N")
                print ("Your warning threshold upon sequence of impact for this game is: ", threshold3, "N")
                
            except UnboundLocalError:
                print ("Invalid Number. Try again.")
            except ValueError:
                print ("Invalid Entry. Try again.")

            else:
                if value in [1,2,3,4,5]: 
                    return threshold1, threshold2, threshold3 #Returns the threshold force values for analysis of the forces in the maih function

def single(threshold1, data):
    #This function signals a red light if any of the force sensors detect a force greater than the threshold 1 (for high single impact forces causing concussions)
    #Takes in two arguments--One being the maximum threshold force value for a single impact and the entire list of data from each sensor
    global red_on
    
    for force in data:
        if force > threshold1: 
            green_led.off()
            yellow_led.off()
            red_led.on()
            red_on = True


#----------------Task 4---------------- (comes before task 3 because the functions are called within Task 3)

def check_time(time_data, index, force_data):
    #This function considers the time between measured forces and updates the new value to the corresponding force sensor
    #Takes in three arguments--One being a list of times of significant forces, the second being the index value corresponding to the position of each list, and the list of forces at that time
    global contrecoup_count

    MIN_TIME = 3
    MULTIPLIER1 = 1.4 #The data gets multiplied by this multiplier if the player experiences forces indicating possible contrecoup injury (impacts from opposite sides)
    MULTIPLIER2 = 1.2 #The data gets multiplied by this multiplier if the player experiences multiple forces adjacent to one another within a short period of time
    contrecoup_check = False #see if this is necessary !!!!!
    
    for i in range(4): #The time between the most recent significant hits are compared between each force sensor and compared to the minimum time range to determine indication of possible contrecoup injury
        if i != index and time_data [i] != 0.0:
            time_elapsed = time_data[index] - time_data[i]
            if time_elapsed < MIN_TIME and time_elapsed >= 0.0:
                if (i%2 == 0 and index%2 == 0) or (i%2 != 0 and index%2 != 0):
                    force_data[index] = force_data[index]*MULTIPLIER1
                    print("\nThe new value of the data point is: ", round(force_data[index],1), "N", "due to coup-contrecoup injury from Force", (i+1),"\n")
                    contrecoup_check = True
                    contrecoup_count += 1 #Need this data for the summary generated in the off() function
                else:
                    force_data[index] = force_data[index]*MULTIPLIER2
                    print("\nThe new value of the data point is: ", round(force_data[index],1), "N", "due to simultaneous impact in a short period of time from Force", (i+1),"\n")

    return force_data[index], contrecoup_check #Returns an updated list of the forces, and a status of whether the player is at risk of contrecoup injury


def blink(contrecoup_check, led):
    #This function makes the lights blink if player is at predicted risk of contrecoup injury
    #Takes in two arguments--One being a status of whether the player is at risk of contrecoup injury and the variable for the led light that is currently on

    if contrecoup_check == True:
        led.blink()
        print("Light is now BLINKING due to contrecoup effect!")
        contrecoup_check = False
    
    return contrecoup_check #Returns an updated status of whether the player is at risk of contrecoup injury


#----------------Task 3----------------

def sequence(data, threshold1, threshold2, threshold3, min_force, force_counter, time_raw, sig_time):
    #This function keeps track of sequential forces that add up to cause concussion risk
    #Takes in eight arguments--One being a list of the force readings from all sensors at a certain time, the threshold values generated at the beginning of the program,
    #   the minimum force threshold for a force to be considered significant, a force counter variable to keep track of added forces, the time that a force occurred, and a list of times of forces that are considered significant 

    index = 0 #an indexing variable to keep track of the force sensor being evaluated within the function

    global red_on  
    
    for force in data:
        
        if force > min_force and force < threshold1:
            sig_time[index] = time_raw #a list is created to keep track of the times of the most recent significant hits for each force sensor 
            force, contrecoup_check = check_time(sig_time, index, data)
            force_counter += force
           
            
            if force_counter > threshold2:
                yellow_led.off()
                red_led.on()
                print ("RED light is now ON!")
            elif force_counter > threshold3 and red_on == False: #red must be off in order for this section of the code to run (If red light is on for whatever reason, no other lights should be on)
                green_led.off()
                yellow_led.on()
                print ("YELLOW light is now ON!")
                contrecoup_check = blink(contrecoup_check, yellow_led)
                  
            else:
                green_led.on()
                contrecoup_check = blink(contrecoup_check, green_led)
                
        index += 1    
    return round(force_counter,1) #Returns the updated value of the force counter, after taking account of injuries related to impacts within short periods of time


def find_max_force(data, max_force):
    #This function keeps track of the highest force experienced by the player
    #Takes in two arguments -- A list of forces from each sensor for comparison and variable for recording the maximum force experienced from any sensor
    for force in data:
        if force > max_force:
            max_force = force
    return max_force #Returns the updated maximum force value

def main():
    #This function compiles all of the previously written functions, initiates obtaining data from force sensors, and prints values onto the monitor  
    
    #initializes the original state of the lights as "OFF"
    red_led.off()  
    yellow_led.off()
    green_led.off()

    #initialize variables
    min_force = 30
    max_force = 0
    force_counter = 0
    forcelist1 = [] 
    forcelist2 = []
    forcelist3 = []
    forcelist4 = []
    sig_time = [0.0, 0.0, 0.0, 0.0]
    
    status() #runs function to start program upon pressing the button
    threshold1, threshold2, threshold3 = medics_info() #determines threshold values
    
    while True:
        #Obtaining data from the sensors and creating lists of force sensor readings
        data1 = var1.force_raw()
        forcelist1.append(data1)
        data4 = var2.force_raw() - 8 #Changed the variable name due to the positioning of the sensors, subtracted 9 to account for systematic error in the force sensor
        forcelist4.append(data4)
        data3 = var3.force_raw()
        forcelist3.append(data3)
        data2 = var4.force_raw() 
        forcelist2.append(data2)
        
        raw_time = round(time.perf_counter(),1) #records the time for each force reading
        data = average(forcelist1, forcelist2, forcelist3, forcelist4) #generates a 4-item list of force sensor readings for each sensor according to the moving average calculated
        
        try:                
            print("Force 1: ",data[0], "N \t Force 2: ",data[1], "N \t Force 3: ",data[2], "N \t Force 4: ",data[3], "N \t Time:", raw_time, "s \t Force Counter:", force_counter, "N")
        except TypeError:
            pass
        
        else:
            time.sleep(1)
            max_force = find_max_force(data, max_force)
            single(threshold1, data) #analyzes data for single high-impact forces
            force_counter = sequence(data, threshold1, threshold2, threshold3, min_force, force_counter, raw_time, sig_time) #analyzes data for sequentially forces that add up over time
            off(max_force, force_counter) #function checks if button is pressed, signalling that the user wants the device turned off

main()