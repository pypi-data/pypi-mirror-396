def cleanCourseData(data):
    ai_grades = []
    for course in data:
        try: 
            coursename = course[1]
        except:
            coursename = ""
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