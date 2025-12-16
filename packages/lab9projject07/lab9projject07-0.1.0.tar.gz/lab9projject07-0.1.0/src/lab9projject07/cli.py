import sys

def num_to_word():
    if len(sys.argv) < 2: # Dunia: checks if there is an argument after the file name
        print("you must enter a number")
        sys.exit() # Dunia: exits the program if there is no argument after the file name
    
    # Dunia:created 2 different variables that will store the inputs seperately so its easier, meaning one for the numbers and one for the options
    num_inputs = ["1", "2", "3"]
    option_inputs = ["--save", "--load", "-h", "--help"]

    args = sys.argv
    input_num = args[1:]

    # Lucas: this checks if --help or -h is in the argument and if it finds those, it will run the "help" part and explain what the function does.
    if ("--help" in input_num) or ("-h" in input_num):
        return "This function says the input number. If '--save' is used, it will save the answer to a file. If '--load is used, it will load the previous saved answer."
     # Lucas: loads the answer
    if "--load" in input_num:
     with open('saved.txt') as l:
        return(l.readlines())
    # Dunia: created a loop that will go through the arguments and separate the numbers from the options 
    numbers_only = []
    for arg in input_num:
        if arg in num_inputs:
            numbers_only.append(arg)
    # Dunia: added a try and except block to catch any errors if the input is not valid
    try:
       input_num.append(numbers_only[0])
    except:
        print("Error: please provide a valid number: 1, 2 or 3")
        sys.exit()
    if "1" in input_num:
        answer = "one"
    elif "2" in input_num:
        answer = "two"
    elif "3" in input_num:
        answer = "three"
    else:
       answer = "invalid input"
    print (answer)
    
    if "--save" in input_num:
        with open('saved.txt', "w") as s:
            s.write(answer)