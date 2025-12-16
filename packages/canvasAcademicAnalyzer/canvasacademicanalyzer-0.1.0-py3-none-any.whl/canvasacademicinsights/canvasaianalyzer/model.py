import ollama
import subprocess
import time
import urllib.request

# TODO get different param sizes for models

OLD = "gemma2:2b"
LOW = "gemma3:270m"
MID = "gemma3:1b" 
HIGH = "gemma3:4b"

MODEL = MID

HEALTH_CHECK = "http://localhost:11434/api/tags"

class ModelError(Exception):
    pass

class AI:
    def __init__(self):
        self.process = subprocess.Popen(["ollama", "serve"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        # wait for ollama server to run
        while True:
            try:
                urllib.request.urlopen(HEALTH_CHECK)
                break
            except ModelError:
                print("Waiting for ollama server to start...")
                time.sleep(0.2)

        # verify correct model is installed
        result = subprocess.run(["ollama", "show", MODEL], capture_output=True, text=True)
        if result.returncode != 0:
            subprocess.run(["ollama", "pull", MODEL])
    
    def __del__(self):
        try:
            self.process.terminate()
        except Exception as ModelError:
            print("Error terminating ollama server:", ModelError)


    def ask(self, prompt):
        # clear terminal
        print("\033[2J\033[3J\033[H", end="")
        # stream chat for interactivity
        for chunk in ollama.chat( 
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        ):
            if chunk.message.content:
                # flush buffer to interactivity
                print(chunk.message.content, end='', flush=True)
        print()
    
    def cleanCourseData(self, data):
        ai_grades = []
        for course in data:
            coursename = course[1]
            gradelist = course[3]

            temp = {
                "Course": coursename,
                "Assignments":  [],
                "Quizzes": []
            }

            for item in gradelist:
                if item.isAssignment() and item.score != None:
                    temp["Assignments"].append((item.name, f'Score: {item.score}', f'Total: {item.total}', f'Date {item.date.strftime("%Y-%m-%d") if item.date is not None else "Not Available"}'))
                elif item.isQuiz() and item.score != None:
                    temp["Quizzes"].append((item.name, f'Score{item.score}', f'Total: {item.total}', f'Date {item.date.strftime("%Y-%m-%d") if item.date is not None else "Available"}'))

            ai_grades.append(temp)
        
        return ai_grades