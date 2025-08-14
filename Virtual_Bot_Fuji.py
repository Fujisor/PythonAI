import speech_recognition as voice_recognation, requests, json
import time, pyttsx3, datetime, webbrowser, ollama as my_ai_companion, os
# Added for .env support
from dotenv import load_dotenv

load_dotenv()

name_of_bot = "Berry" # Bot name
name_of_user = "" # Holder for user name
Command_TimeOut = 10 # seconds of inactivity before exiting interaction mode
recog = voice_recognation.Recognizer() # It will recognize voice
mic = voice_recognation.Microphone(sample_rate=48000)
# Use environment variables for file paths
import os
chat_history = os.getenv("CHAT_HISTORY_PATH") # See .env file
log_file = os.getenv("ERROR_LOG_PATH") # See .env file

def initial_recognizer():
        
        # Recognizer configuration
        recog.pause_threshold = 0.5                # Seconds of silence before assuming you're done speaking
        recog.phrase_threshold = 0.5               # Minimum speaking duration to consider as a phrase
        recog.dynamic_energy_threshold = True      # Automatically adjust energy threshold based on noise
        recog.operation_timeout = 5                # Max time (in seconds) to wait before throwing timeout error
        recog.non_speaking_duration = 0.5          # Silence time before/after speech to trim the input
        recog.energy_threshold = 4000              # Manual energy threshold to detect speech (loudness)
        # print(voice_recognation.Microphone.list_microphone_names()) # Print all the available microphone source
        return recog
        
def initialize_engine():
    engine = pyttsx3.init("sapi5") # sapi5 = holder of the two voice
    voice = engine.getProperty('voices')
    engine.setProperty('voice', voice[1].id)
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-60)
    volume = engine.getProperty('volume')
    engine.setProperty('volume', volume+0.7)
    return engine

# Collect all error of the program
def log_errors(error):
     with open(log_file, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {str(error)}\n")

# Cheacking the history
def log_histrory():
    if os.path.exists(chat_history):
        try:
            with open(chat_history, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If file exists but is empty or corrupted
            return []
    return []

# Saving every interaction
def save_interaction(question, answer):
    history = log_histrory()
    history.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "user": question,
        "bot": answer
    })

    with open(chat_history, "w") as f:
        json.dump(history, f, indent=2)

# Speak Function 
def speak(text):
    engine = initialize_engine()
    engine.say(text)
    engine.runAndWait()

# Command for wake up the bot
def wake_command():
    try:
        print("Listening for wake-up word...")
        with mic as command_source:
            recog.adjust_for_ambient_noise(command_source, duration=1)
            audio = recog.listen(command_source, timeout=7, phrase_time_limit=5)
            text = recog.recognize_google(audio)
            print(f"User said: {text}")
            return text.lower()
    except voice_recognation.UnknownValueError as e:
        log_errors(e)
        print("⚠️ Could not understand wake word.")
    except voice_recognation.WaitTimeoutError as e:
        log_errors(e)
        print("⌛ Wake word listening timed out.")
    except Exception as e:
        log_errors(e)
        print(f"❌ Error during wake word listening: {str(e)}")
    return None

# All voice command transfrom to text that will understand of the program
def command():
 
    while True:
        try:

            with mic as command_source:
                recog.adjust_for_ambient_noise(command_source, duration=1)
                print("\r", end="", flush=True)
                print(f"{name_of_bot} is listening.......", end="", flush=True)
                audio_source = recog.listen(command_source, timeout = Command_TimeOut, phrase_time_limit = 10) # input for microphone
                                                                                                # phrase_time_limit = 10 = Maximum time allowed to capture a single phrase
                                                                                                # timeout = 10 = Maximum time before throwing listening timeout
                print("\r", end="", flush=True) # Move cursor to the beginning of the current line
                print("Recognizing.......", end="", flush=True) # 'end=""' prevents newline, 'flush=True' forces the output to appear immediately
                text_messages = recog.recognize_google(audio_source) # Recognize using google
                print("\r", end="", flush=True)
                print(f"User said: {text_messages}")
                return text_messages.lower()

        except voice_recognation.UnknownValueError as e:
            log_errors(e)
            speak("Could not understand audio.")
            return None

        except voice_recognation.RequestError as e:
            log_errors(e)
            print("Speech recognition service error.")
            return None

        except voice_recognation.WaitTimeoutError as e:
            log_errors(e)
            print("Listening timed out.")
            return "timeout"
            
        
        except Exception as e:
            log_errors(e)
            print(f"An unexpected error occurred: {str(e)}")
            return None

# Day converter for word          
def day_cal():
    day = datetime.datetime.today().weekday() + 1 # So it will start for Monday
    day_week = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }

    if day in day_week.keys():
        day_today = day_week[day]
        print(day_today)
    return day_today

def welcome():

    # while True:
        # print("What is your name?")
        # input = command()

        # if input: # Only continue if the input is not None or empty

        #     name_of_user = input
        #     break

    hour = int(datetime.datetime.now().hour) # Whole number for hour
    time_now = time.strftime("%I %M %p")
    time_now = time_now.lstrip("0") # # Only removes leading 0 from entire string
    print(hour)
    print(time_now)
    day = day_cal()
    
    if (hour >= 0) and (hour <= 12) and ('AM' in time_now):
        speak(f"Good Morning {name_of_user}, It's {day} and the time is {time_now}")
        speak(f"I am your assistant {name_of_bot}. How can I help you?")

    elif(hour >= 1) and (hour <= 6) and ('PM' in time_now):
        speak(f"Good afternon {name_of_user}, It's {day} and the time is {time_now}")
        speak(f"I am your assistant {name_of_bot}. How can I help you?")

    else:
        speak(f"Good evening {name_of_user}, It's {day} and the time is {time_now}")
        speak(f"I am your assistant {name_of_bot}. How can I help you?")

# Getting weather using API
def get_weather():
    # Use API key from environment variable
    weather_API_key = os.getenv("WEATHER_API_KEY") # See .env file

    while True:
        speak("Which city do you want the weather for?")
        input = command()

        if input and input != "timeout":
            city_place = input
            break
        else:
            speak("I didn't catch that. Please say the city name again.")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_place}&appid={weather_API_key}"
    try:
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            speak(f"Sorry, I couldn't find weather information for {city_place}.")
            return

        temp_kelvin = data["main"]["temp"]
        temp_celsius = temp_kelvin - 273.15
        weather_descriptiom = data["weather"][0]["description"]

        answer = f"The weather in {city_place} is {weather_descriptiom}  the temperature is about {temp_celsius:.1f}"
        save_interaction(input, answer)
        speak(answer)

    except requests.exceptions.RequestException as e:
        log_errors(e)
        print(f"Request Error\n{e}")

# Here where AI located
def Ai_companion(content):
    
    try:
        reponse = my_ai_companion.chat(
            model= 'llama3',
            messages=[
                {"role": "user", "content": "You are Berry, a friendly assistant. Answer clearly and simply, like you're talking to a friend. Keep it short and natural."},
                {"role": "user", "content": content}
                ]
        )

        answer = reponse['message']['content']
        save_interaction(content, answer)
        speak(answer)

    except Exception as e:
        log_errors(e)
        speak("Sorry, I had trouble responding.")

def main():
    interaction_mode = False
    last_interaction = time.time() # Track the last time something happenedTrack the last time something happened
    first_interaction = False
    
    try:

        while True:
            current_time_loop = time.time()

            if not interaction_mode and (current_time_loop - last_interaction > 300):
                    
                print("No activity for 5 minutes. Exiting...")
                speak("No activity detected. Shutting down.")
                break

            try:
                

                if not interaction_mode:

                    text_wake_up = wake_command()
                    
                    if text_wake_up and name_of_bot.lower() in text_wake_up.lower():
                        answer = "Hello there"
                        save_interaction(text_wake_up, answer)
                        speak(answer)
                        interaction_mode = True
                        first_interaction = True
                        last_interaction = time.time() # timestamp of the last time the user interacted

                    else:
                        print("Wake-up word not detected, coutinuing....")

                elif first_interaction:
                    welcome()
                    first_interaction = False
                    continue
                
                else:

                    print(f"{name_of_bot} is listening for the next command")
                    text_messages = command()

                    if text_messages == "timeout":
                        speak("No command for 10secs, Returning to wake up mode")
                        interaction_mode = False
                        continue

                    elif text_messages and "get weather" in text_messages.lower():
                        get_weather()
                        last_interaction = time.time()

                    elif text_messages and "go to chat" in text_messages.lower():

                        is_chat_ai = True

                        while is_chat_ai:

                            speak(f"Ask me Something {name_of_user}")

                            ai_interaction = command()
                            
                            if ai_interaction and ("exit" in ai_interaction.lower() or ai_interaction == "timeout"):
                                speak("exiting.....")
                                is_chat_ai = False

                            elif ai_interaction:
                                speak(Ai_companion(ai_interaction))
                                continue

                            else:
                                speak("I didn't catch that. Please say the city name again.")
                                continue


                    elif text_messages and "goodbye" in text_messages.lower():
                        speak(f"Goodbye {name_of_user}. Shutting down.")
                        break

                    else:
                        continue

            except voice_recognation.UnknownValueError as e:
                log_errors(e) 
                print("⚠️ Could not understand audio.")

            
    except Exception as e:
        log_errors(e)
        print(f"Critical error in the main system loop {e}")


if __name__ == "__main__":
    main()