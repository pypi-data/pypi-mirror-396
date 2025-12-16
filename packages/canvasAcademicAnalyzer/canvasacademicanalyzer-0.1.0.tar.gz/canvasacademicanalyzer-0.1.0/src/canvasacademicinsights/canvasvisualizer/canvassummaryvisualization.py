import matplotlib.pyplot as plt
class PlotError(Exception):
    pass
class CanvasSummaryVisualizer:
    def __init__(self, data):
        self.data = data

    def plot_overall_scores(self):
        '''
        Plots the final scores for courses in using a bar graph
        Classes in progress are included, so not all assements are included as they haven't been completed yet
        '''
        course_names = []
        scores = []
    
        for course in self.data:

            course_id, course_name, grade_meta_list, _ = course

            overall = None
            if grade_meta_list:
                meta = grade_meta_list[0]
                overall = meta.get("final_score")

            if isinstance(overall, (int, float)):
                course_names.append(course_name)
                scores.append(overall)

        if not course_names:
            print("No overall scores to plot.")
            return

        # Try-except statement added 
        try:
            if any(s<0 for s in scores):
                raise PlotError("Negative Scores")
            
            plt.figure(figsize=(14,6))
            plt.bar(course_names, scores)
            plt.xticks(rotation=45, ha="right")
            plt.ylabel("Overall score (%)")
            plt.ylim(0, 110)
            plt.title("Overall Canvas scores by course")
            plt.tight_layout()
            plt.show()

        except PlotError as e:
            print("PlotError:", e)

    def plot_grade_distribution(self, course_index: int = 0):
        """
        Plot a histogram of grade percentages for all graded items
        in a selected course.
        """


        # Try-except statement added
        try:
            if course_index < 0 or course_index >= len(self.data):
                raise IndexError("Invalid Index")
        except IndexError as e:
            print("IndexError:", e)
            return
        
        course_id, course_name, _, grade_items = self.data[course_index]

        percentages = []
        for item in grade_items:

            # Try-except statement added 
            try:
                score = getattr(item, "score", None) # gets your score on the assignment or quiz
                total = getattr(item, "total", None) # the total points the assesment is worth
                if score < 0:
                    raise PlotError("Invalid Score")
                if total < 0:
                    raise PlotError("Invalid Total")
                percentages.append(100 * score / total)
            except PlotError as e:
                print("PlotError: ", e)
                return
        
        plt.figure()
        plt.hist(percentages, bins=10, edgecolor="black")
        plt.xlabel("Score (%)")
        plt.ylabel("Frequency")
        plt.title(f"Grade Distribution for {course_name} ({course_id})")
        plt.tight_layout()
        plt.show()

    def plot_missing_assignments(self, course_index: int = 0):
        """
        Create a pie chart showing the proportion of completed vs missing assignments
        for the selected course.
        """
        
        # Try-except statement added
        try:
            if course_index < 0 or course_index >= len(self.data):
                raise IndexError("Invalid Index")
        except IndexError as e:
            print("IndexError:", e)
            return

        course_id, course_name, _, grade_items = self.data[course_index]

        completed = 0
        missing = 0

        for item in grade_items:
            score = getattr(item, "score", None)
            total = getattr(item, "total", None)

            # missing if no score or no total
            if score is None or total in (None, 0):
                missing += 1
            else:
                completed += 1

        # Avoid plotting an empty pie chart
        if completed == 0 and missing == 0:
            print("No assignment data available.")
            return

        plt.figure()
        
        plt.pie(
            [completed, missing],
            labels=["Completed", "Missing"],
            autopct="%1.1f%%",
            colors=["skyblue", "orange"],
        )
        plt.title(f"Completed vs Missing Assignments\n{course_name} ({course_id})")
        plt.tight_layout()
        plt.show()

    def plot_num_assessments_per_course(self):
        '''
        Plot a bar graph showing the number of assignments and quizzes per course
        '''
        course_names = []
        assign_counts = []
        quiz_counts = []

        for course_id, course_name, _, grade_items in self.data:

            # Try-except statement added
            try:
                if not grade_items:
                    raise ValueError("grade_items is empty or none")
                n_assign = sum(1 for item in grade_items if hasattr(item, "isAssignment") and item.isAssignment()) # counts the number of assignments
                n_quiz = sum(1 for item in grade_items if hasattr(item, "isQuiz") and item.isQuiz())  # counts the number of quizzes

                course_names.append(course_name)
                assign_counts.append(n_assign)
                quiz_counts.append(n_quiz)
            except ValueError as e:
                print(f"Skipping course {course_name} due to data error", e)

            # Only include courses that have at least one assignment or quiz
            if n_assign == 0 and n_quiz == 0:
                continue


        if not course_names:
            print("No course data.")
            return

        # x positions for courses
        x = list(range(len(course_names)))
        width = 0.4  # width of each bar

        # positions for assignment and quiz bars
        assign_x = [xi - width / 2 for xi in x]
        quiz_x   = [xi + width / 2 for xi in x]

        plt.figure(figsize=(14,6))
        plt.bar(assign_x, assign_counts, width=width, label="Assignments", color="skyblue")
        plt.bar(quiz_x,   quiz_counts,   width=width, label="Quizzes", color="orange")

        plt.xticks(x, course_names, rotation=45, ha="right")
        plt.ylabel("Count")
        plt.title("Number of assignments and quizzes per course")
        plt.legend()
        plt.tight_layout()
        plt.show()