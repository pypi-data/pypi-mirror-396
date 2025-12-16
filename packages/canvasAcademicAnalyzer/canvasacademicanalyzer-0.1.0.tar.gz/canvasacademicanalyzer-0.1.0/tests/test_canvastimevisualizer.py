import unittest
from unittest.mock import patch
import datetime
from canvasacademicinsights.canvasvisualizer import canvastimevisualization as tv


class TestTimeVisuals(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
            cls.grade_meta_data =[{
                'html_url': 'https://canvas.ubc.ca/courses/174247/grades/2650436',
                'current_grade': None,
                'current_score': None,
                'final_grade': None,
                'final_score': 10.0,
            }]
            cls.assesments = []

    def setUp(self):
        self.testData = [["courseid","coursename", self.grade_meta_data, self.assesments] for j in range(5)] 

    def tearDown(self):
        self.testData = None
        #print("tearDown: Finished a test.")

    @classmethod
    def tearDownClass(cls):
        #print("tearDownClass: All tests done")
        pass


    def test_get_last_graded_items_normal(self):
        class FakeAssignment:
            def __init__(self, score, total, date):
                self.score = score
                self.total = total
                self.date = date
            def isAssignment(self): return True
            def isQuiz(self): return False

        class FakeQuiz:
            def __init__(self, score, total, date=None):
                self.score = score
                self.total = total
                self.date = date
            def isAssignment(self): return False
            def isQuiz(self): return True

        a1 = FakeAssignment(9, 10, "2025-01-01")
        a2 = FakeAssignment(5, 5,  "2025-02-01")
        q1 = FakeQuiz(8, 10, "2025-01-10")
        q2 = FakeQuiz(7, 10, "2025-02-05")
        self.testData[0][3] = [a1, a2, q1, q2]

        visualizer = tv.CanvasTimeVisualization(self.testData)
        last_a, last_q = visualizer.get_last_graded_items()

        self.assertIs(last_a, a2)  
        self.assertIs(last_q, q2)  
        self.assertEqual(last_a.date, "2025-02-01")
        self.assertEqual(last_q.date, "2025-02-05")

    @patch("canvasacademicinsights.canvasvisualizer.canvastimevisualization.plt")
    def test_plot_weekly_average_score_heatmap(self, mock_plt):
        class FakeGradeItem:
            def __init__(self, score, total, date):
                self.score = score
                self.total = total
                self.date = date

        self.testData[0][3] = [
            FakeGradeItem(18, 20, datetime.date(2025, 1, 10)), 
            FakeGradeItem(24, 26, datetime.date(2025, 1, 12)), 
        ] 
        self.testData[1][3] = [
            FakeGradeItem(18, 20, datetime.date(2025, 1, 17)), 
            FakeGradeItem(24, 26, datetime.date(2025, 1, 19)), 
        ]
        visualizer = tv.CanvasTimeVisualization(self.testData)
        visualizer.plot_weekly_average_score_heatmap()

        mock_plt.figure.assert_called_once_with(figsize=(14, 6))
        mock_plt.xlabel.assert_called_once_with("Week")
        mock_plt.ylabel.assert_called_once_with("Course")
        mock_plt.title.assert_called_once_with("Weekly average percentage score by course")
        self.assertTrue(mock_plt.imshow.called)
        self.assertTrue(mock_plt.colorbar.called)
        self.assertTrue(mock_plt.tight_layout.called)
        self.assertTrue(mock_plt.show.called)

                





if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)