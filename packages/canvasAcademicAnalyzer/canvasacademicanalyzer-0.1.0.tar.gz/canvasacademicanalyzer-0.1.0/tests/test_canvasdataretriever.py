import unittest
from datetime import datetime
from canvasacademicinsights.canvasmain import canvasdataretriever as cr

class TestCleaner(unittest.TestCase):
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
            
        self.dateFormat = "%Y-%m-%dT%H:%M:%SZ"
        self.testDate = datetime.strptime('2025-10-13T06:59:00Z', self.dateFormat)
        self.testDate2 = datetime.strptime('2025-10-13T07:59:00Z', self.dateFormat)
        
        self.grade = cr.Grade('Hi',0,10,self.testDate)
        self.assignment = cr.AssignmentGrade('Hi',0,10,self.testDate)
        self.quiz = cr.QuizGrade('Hi',0,10,self.testDate)
        
    def test_clean_data(self):
        self.cleanData = cr.cleanData(self.testData)
        self.assertEqual(self.cleanData[0][0],"courseid")
        self.assertEqual(self.cleanData[0][1],"coursename")
        self.assertEqual(self.cleanData[0][2],[{'html_url': 'https://canvas.ubc.ca/courses/174247/grades/2650436', 'current_grade': None, 'current_score': None, 'final_grade': None, 'final_score': 10.0}])
        self.assertTrue(isinstance(self.cleanData[0][3][0], cr.AssignmentGrade))
        self.assertTrue(isinstance(self.cleanData[0][3][1], cr.QuizGrade))
        
    def test_grade(self):
        self.assertEqual(self.grade.name,'Hi')
        self.assertEqual(self.grade.score,0)
        self.assertEqual(self.grade.total,10)
        self.assertEqual(self.grade.date,self.testDate)
        self.assertNotEqual(str(self.grade),'')
        self.grade.name = '2'
        self.grade.score = 10
        self.grade.total = 20
        self.grade.date = self.testDate2
        self.assertEqual(self.grade.name,'2')
        self.assertEqual(self.grade.score,10)
        self.assertEqual(self.grade.total,20)
        self.assertEqual(self.grade.date,self.testDate2)
        pass
    
    def test_assignment_grade(self):
        self.assertEqual(self.assignment.name,'Hi')
        self.assertEqual(self.assignment.score,0)
        self.assertEqual(self.assignment.total,10)
        self.assertEqual(self.assignment.date,self.testDate)
        self.assertTrue(self.assignment.isAssignment())
        self.assertFalse(self.assignment.isQuiz())
        self.assertNotEqual(str(self.assignment),'')
        pass
    
    def test_quiz_grade(self):
        self.assertEqual(self.quiz.name,'Hi')
        self.assertEqual(self.quiz.score,0)
        self.assertEqual(self.quiz.total,10)
        self.assertEqual(self.quiz.date,self.testDate)
        self.assertFalse(self.quiz.isAssignment())
        self.assertTrue(self.quiz.isQuiz())
        self.assertNotEqual(str(self.quiz),'')
        pass
        
    def tearDown(self):
        self.testData = None
        self.cleanData = None
        self.dateFormat = None
        self.testDate = None
        self.testDate2 = None
        self.grade = None
        self.assignment = None
        self.quiz = None
        
    @classmethod
    def tearDownClass(cls):
        pass