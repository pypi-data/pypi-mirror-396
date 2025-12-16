import unittest
from datetime import datetime
from canvasacademicinsights.canvasmain import canvasinsights as ci
from canvasacademicinsights.canvasmain import canvasdataretriever as cr

class TestMain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        #Below sets up test data to use
        self.testData = []

        for j in range(5): 
            sampleCourse = [
                "courseid",
                "coursename",
                [{'html_url': 'https://canvas.ubc.ca/courses/174247/grades/2650436',
                'current_grade': None,
                'current_score': None,
                'final_grade': None,
                'final_score': 10.0}],
            ]

            sampleCourse.append(['Lab1', 3.7, 5.0, '2025-10-13T06:59:00Z'])
            sampleCourse.append(['Q1', 97.0, 100.0, None])
            self.testData.append(sampleCourse)
            
    def test_clean_data(self):
        self.cleanData = ci.cleanData(self.testData)
        self.assertEqual(self.cleanData[0][0],"courseid")
        self.assertEqual(self.cleanData[0][1],"coursename")
        self.assertEqual(self.cleanData[0][2],[{'html_url': 'https://canvas.ubc.ca/courses/174247/grades/2650436', 'current_grade': None, 'current_score': None, 'final_grade': None, 'final_score': 10.0}])
        self.assertTrue(isinstance(self.cleanData[0][3][0], cr.AssignmentGrade))
        self.assertTrue(isinstance(self.cleanData[0][3][1], cr.QuizGrade))
        
    def test_get_courses(self):
        self.courses= ci.getCourses(self.testData)
        self.assertEqual(len(self.courses), 5)
        self.assertEqual(self.courses[0], 'coursename')
        self.assertEqual(self.courses[1], 'coursename')
        self.assertEqual(self.courses[2], 'coursename')
        self.assertEqual(self.courses[3], 'coursename')
        self.assertEqual(self.courses[4], 'coursename')
        
    def tearDown(self):
        self.testData = None
        self.cleanData = None
        
    @classmethod
    def tearDownClass(cls):
        pass
        


