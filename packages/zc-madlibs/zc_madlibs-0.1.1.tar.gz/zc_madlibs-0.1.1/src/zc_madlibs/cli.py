import requests
import json
import time
import sys
import os
import textwrap
import regex as re

def helpmsg():
    return"""MENU FOR MAD LIBS (a la python)-----------------
    Basic Usage:
    $poetry run rungame <story> -fast

    ex:
        $poetry run rungame codemas -fast
        FILLING OUT WORDS FOR STORY: The Night Before Codemas.
        Type -restart to restart the selection or type -q to quit.
        Place:
        -> <enter your choice here>
        ....
    Only 1 template may be used at a time:
    nightout -> "The Night After Finals" : a story about a wild night out on the town.
    codemas -> "The Night Before Codemas": a story about a developer coding on Christmas Eve.

    More Options:
    --help -> can be entered to display this message 
    --slow -> Used to slowly print the final story one character at a time. (0.5-second breaks)
            By default, text is printed all at once.
    --fast -> Prints final story one character at a time, but faster (0.05-second breaks)
    """

def parse_args(arguments):
    """identifies valid arguments in command-line input"""
    story_options = ["nightout", "codemas"]
    speed_options = ["fast", "slow", "none"]
    if (len(arguments) == 0) or ("-h" in arguments):
        print(helpmsg())
        sys.exit(0) 
    valid_speed = [] #collecting valid args here...
    valid_story = []
    for a in arguments:
        if a[0] == "-": 
            speed_choice = a[1:]
            if speed_choice not in speed_options:
                print(f"That isn't one of the options. You can choose from the following stories: {speed_options}")
                sys.exit(1)
            else: valid_speed.append(speed_choice)
        else:
            if a in story_options:
                valid_story.append(a)
                continue
            print(f"That isn't one of the options. You can choose from the following stories: {story_options}")
            sys.exit(1)
    if(len(valid_speed)) >1  or (len(valid_story) > 1):
        print("PSSST! You can only enter one story and one speed!")
        sys.exit(1)
    if len(valid_speed) == 0:
        valid_speed.append("none")
    if len(valid_story)==0:
        print("you must specify a story.")
        sys.exit(1)
           
    return(valid_story[0], valid_speed[0])

def slowprint(text, sleeptime):
     """slow print function. prints one character at 
     a time of a given string (text). sleep time 
     (time in between iterations of printing a char) 
     is a variable and can be an int or float representing seconds of pause time."""

     for word in text:
          for i in word:
               print(str(i), end='', flush=True)
               time.sleep(sleeptime)
               continue
          
def test_api():
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/hello"
    response = requests.get(url)
    if response.status_code == 200:
         return True
    return False
    
 #need this fx to handle multiple words....currently won't check more than one.

def is_correct_type(word, type):
            """returns boolean on whether a word is of a specified type
              (i.e noun, adjective). Both word and type must be strings.
            Accesses API Dictionary."""
            speechparts = []
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url)
            if test_api()== True:

                if response.status_code!= 404:
                    data = response.json()
                    for i in (data):
                        if i.get("meanings","") != "":
                            for j in i.get("meanings"):
                                speechpart = j.get("partOfSpeech")
                                speechparts.append(speechpart)
                                continue
                            continue
                        continue
                    if (type in speechparts):
                        return True
                else: 
                    return(False)

def validateword(u_input, reqtype, constraints):
    """returns boolean on whether u_input is valid, and 
    fits a required type and constraints provided. Accepts 
      """
    if len(u_input)== 0:
        print("you didn't enter a word.")
        return (False) 
    
    regexp =re.compile(r'[^a-zA-Z ]') #attempting a regex to check for non-alpha characters
    if regexp.match(u_input):
         print("invalid characters detected! Only alphanumeric characters are permitted.")
         return(False)
    
    if ("end" in constraints) == True:
        ending = constraints[(constraints.find("-")+1):]
        if u_input[-(len(ending)):] != ending:
            print("Hey! Did you listen to the intruction? Maybe try reading it again. :)")
            return(False)
        
    if (reqtype != ""):  
        if (is_correct_type(u_input, reqtype)) == True: 
            return(True)
        print(f"""*buzzer noise* The word you chose is not recognized as a valid {reqtype}.""")
        return(False)
    return(True)



def getdata(argument):

    """fetches data from JSON file local to poetry project"""
    fpath = ("src" + os.sep +"zc_madlibs" + os.sep + f"{argument}.json")
    try:
        with open(fpath, "r") as file:
            contents = json.load(file)
            return(contents)
    except:
         print("Problem opening file")
         sys.exit(1)
     
def fetch_words(contents):
        """prompts for 
        input for every word required, validates it,
        returns list of words."""

        required = contents[2]
        template = contents[1]
        title = contents[0]
                
        words = []

        startmsg = (f"""\nFILLING OUT WORDS FOR STORY - '{title}'.\nType -restart to restart the selection.""")
        print(startmsg)
        r = 0
        while r < len(required):
            current = required[r]
            constraints = current.get("constraints", "")
            reqtype = current.get("type", "")
            print(current.get("prompt for"))
            u_input = input("->") 
            if u_input.upper() == "-RESTART":
                words = []
                r = 0
                print(startmsg)
                continue
            if validateword(u_input, reqtype, constraints) == True:
                words.append(u_input)
                r +=1
                continue
            continue
        return(words, template, title)

def fill_story(data):
    """Returns formatted story created by inserting words at the indexes of * characters 
    in items of the template list. 
    Formatting depends on which story is being used.
    Uses text wrap function for neat formatting. 
    Accepts a tuple containing two lists(words, template) and a string (title)"""

    words = data[0]
    template = data[1]
    title = data[2]


    newstory = [f"\n************{title}***************\n"]
    i = 0
    for text in (template):
            if ("*" in text):
                newline = (text[:text.find("*")] + words[i])
                newstory.append(newline)
                i+=1
                continue
            newstory.append(text)
    newstory.append("\n*** THE END ***\n")
    if "Finals" in title:
        return(textwrap.fill(("".join(newstory) + ".\n"), width = 100))
    else: 
        return("".join(newstory))

def printfx(story, speed = "none"):
    """calls version of print function
      according to specified speed arg."""
    
    if speed =="none":
        print(story)
    if speed =="fast":
     slowprint(story, 0.05)
    if speed == "slow":
     slowprint(story, 0.5)
    
     
def main():
    args = sys.argv[1:] 
    (story, speed) = parse_args(args)
    printfx(fill_story(fetch_words(getdata(story))), speed)
    sys.exit(0) #this is the last function call so always want to make sure it exits.

