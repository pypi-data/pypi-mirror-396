import unittest
from unittest.mock import patch
from canvasacademicinsights.canvasvisualizer import canvassummaryvisualization as sv


class TestSummaryVisuals(unittest.TestCase):

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

    # This @patch("package.subpackage.module.plt") makes it easy to mock classes or objects in a module under a test
    # https://docs.python.org/3/library/unittest.mock.html is the link to its documentation
    @patch("canvasacademicinsights.canvasvisualizer.canvassummaryvisualization.plt")
    def test_plot_overall_scores(self, mock_plt):
        visualizer = sv.CanvasSummaryVisualizer(self.testData)
        visualizer.plot_overall_scores()
        expected_names = ["coursename"] * 5
        expected_scores = [10.0] * 5

        mock_plt.figure.assert_called_once_with(figsize=(14, 6))
        mock_plt.bar.assert_called_once_with(expected_names, expected_scores)
        mock_plt.ylabel.assert_called_once_with("Overall score (%)")
        mock_plt.ylim.assert_called_once_with(0, 110)
        mock_plt.title.assert_called_once_with("Overall Canvas scores by course")
        self.assertTrue(mock_plt.bar.called)
        self.assertTrue(mock_plt.xticks.called)
        self.assertTrue(mock_plt.tight_layout.called)
        self.assertTrue(mock_plt.show.called)

    @patch("canvasacademicinsights.canvasvisualizer.canvassummaryvisualization.plt")
    def test_plot_grade_distribution(self, mock_plt):    
        # Fake grade items that match what the function expects
        class FakeGradeItem:
            def __init__(self, score, total):
                self.score = score
                self.total = total
        self.testData[0][3] = [
            FakeGradeItem(8, 10),
            FakeGradeItem(15, 20), 
            FakeGradeItem(5, 5),
        ]
        visualizer = sv.CanvasSummaryVisualizer(self.testData)
        visualizer.plot_grade_distribution()
        expected_percentages = [80.0, 75.0, 100.0]

        mock_plt.figure.assert_called_once()
        mock_plt.hist.assert_called_once_with(expected_percentages, bins=10, edgecolor="black")
        mock_plt.hist.assert_called_once_with(expected_percentages, bins=10, edgecolor="black")
        mock_plt.xlabel.assert_called_once_with("Score (%)")
        mock_plt.ylabel.assert_called_once_with("Frequency")
        mock_plt.title.assert_called_once_with("Grade Distribution for coursename (courseid)")
        self.assertTrue(mock_plt.hist.called)
        self.assertTrue(mock_plt.tight_layout.called)
        self.assertTrue(mock_plt.show.called)

    @patch("canvasacademicinsights.canvasvisualizer.canvassummaryvisualization.plt")
    def test_plot_missing_assignments(self, mock_plt):
        class FakeGradeItem:
            def __init__(self, score, total):
                self.score = score
                self.total = total
        
        self.testData[0][3] = [
            FakeGradeItem(None, 20),
            FakeGradeItem(24,26)
        ]
        visualizer = sv.CanvasSummaryVisualizer(self.testData)
        visualizer.plot_missing_assignments()
        expected_completed = 1
        expected_missing = 1

        mock_plt.figure.assert_called_once()
        mock_plt.pie.assert_called_once_with(
            [expected_completed, expected_missing],
            labels=["Completed", "Missing"],
            autopct="%1.1f%%",
            colors=["skyblue", "orange"]
        )
        mock_plt.title.assert_called_once_with(f"Completed vs Missing Assignments\ncoursename (courseid)")
        self.assertTrue(mock_plt.tight_layout.called)
        self.assertTrue(mock_plt.show.called)

    @patch("canvasacademicinsights.canvasvisualizer.canvassummaryvisualization.plt")
    def test_plot_num_assignments_per_course(self, mock_plt):
        class FakeAssignment:
            def isAssignment(self): return True
            def isQuiz(self): return False
        class FakeQuiz:
            def isAssignment(self): return False
            def isQuiz(self): return True

        self.testData[0][3] = [
            FakeAssignment(),
            FakeAssignment(),
            FakeQuiz(),
        ]
        

        visualizer = sv.CanvasSummaryVisualizer(self.testData)
        visualizer.plot_num_assessments_per_course()

        mock_plt.figure.assert_called_once_with(figsize=(14,6))
        bar_calls = mock_plt.bar.call_args_list
        self.assertEqual(len(bar_calls), 2)

        assign_args, assign_keyword_args = bar_calls[0]
        self.assertIn(2, assign_args[1])  # second argument is assign_counts
        self.assertIn(assign_keyword_args["label"], "Assignments")
        self.assertIn(assign_keyword_args["color"], "skyblue")

        quiz_args, quiz_keyword_args = bar_calls[1]
        self.assertIn(1, quiz_args[1])   # second argument is quiz_counts
        self.assertIn(quiz_keyword_args["label"], "Quizzes")
        self.assertIn(quiz_keyword_args["color"], "orange")
