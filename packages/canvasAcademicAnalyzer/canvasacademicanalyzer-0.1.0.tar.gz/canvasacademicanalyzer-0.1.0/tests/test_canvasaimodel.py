import unittest
import urllib.request
import requests
import random
import io
import sys
from datetime import datetime
from canvasacademicinsights.canvasaianalyzer import clean
from canvasacademicinsights.canvasaianalyzer import model
from canvasacademicinsights.canvasmain import canvasdataretriever as c 


class TestAIModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        courses = []
        for j in range(5): 
            gradeList = []
            sampleCourse = [
                "courseid",
                "coursename",
                "courseenrollment",
            ]

            counter = 1
            for i in range(10): 
                counter += 1
                if random.random() > 0.5:
                    gradeList.append(c.QuizGrade(name = f"Test{random.random()}", score = random.random() * 100, total = 100, date = datetime.strptime(f"2025-11-{counter}", "%Y-%m-%d")))
                else:
                    gradeList.append(c.AssignmentGrade(name = f"Test{random.random()}", score = random.random() * 100, total = 100, date = datetime.strptime(f"2025-11-{counter}", "%Y-%m-%d")))
            sampleCourse.append(gradeList)
            courses.append(sampleCourse)
            self.courses = courses
            self.ai = model.AI()
            
    def testCleanData(self):
        clean.cleanCourseData(self.courses)
        self.assertEqual(len(self.courses), 5)
        for c in self.courses:
            self.assertGreater(len(c[0]), 0)
            self.assertGreater(len(c[1]), 0)
            self.assertGreater(len(c[2]), 0)
            self.assertEqual(len(c[3]), 10)
    
    def testAIModel(self): 
        httpResponse = urllib.request.urlopen(model.HEALTH_CHECK)
        self.assertEqual(httpResponse.status, 200)           
        httpResponse = requests.post("http://localhost:11434/api/generate", json={"model" : model.MODEL, "prompt": "Hi!"})      
        self.assertEqual(httpResponse.status_code, 200)  
        sys.stdout = io.StringIO()         
        self.ai.ask("Hello!")
        output = sys.stdout.getvalue()
        self.assertGreater(len(output), 0)
        self.ai = None
        try:
            httpResponse = urllib.request.urlopen(model.HEALTH_CHECK)
        except:
            httpResponse = None

        # Python Garbage Collector might not immediately destory the object (and so server does not quit). 
        # We want to make sure that either the process is running or destroyed and nothing else has gone wrong. 
        self.assertEqual(httpResponse.status, 200 or None)

    
    def tearDown(self):
        self.courses = None
        self.ai = None
    
    @classmethod
    def tearDownClass(cls):
        pass
        
