from canvasapi import Canvas
from datetime import datetime

dateFormat = "%Y-%m-%dT%H:%M:%SZ"

class CanvasConnectionError(Exception):
    pass

def getData(canvas_url, access_token, skip_ids):
    try:
        canvas = Canvas(canvas_url, access_token)
    except:
        raise CanvasConnectionError
    
    return parseData(canvas, skip_ids)

def parseData(canvas, skip_ids):
    data = []
    user = canvas.get_current_user()
    #print(f"Logged in as: {user.name}")

    courses = user.get_courses()

    #print("\nAll Courses:")
    for course in courses:
        courseData = []
        
        if hasattr(course, 'id') and course.id and course.id in skip_ids:
            continue
        elif hasattr(course, 'id') and course.id:
            courseData.append(course.id)
            print(f"ID: {course.id}")
        else:
            courseData.append(-1)
        if hasattr(course, 'name') and course.name:
            courseData.append(course.name)
            #print(f"Name: {course.name}")
        else:
            courseData.append("")
            
        enrollments = course.get_enrollments(type=['StudentEnrollment'], include=['grades'])

        for enrollment in enrollments:
            if hasattr(enrollment, 'user') and enrollment.user:
                user_name = enrollment.user['name']
                #if hasattr(enrollment, 'grades') and enrollment.grades:
                if user_name == user.name:
                    enrollmentData = []
                    if hasattr(enrollment, 'grades') and enrollment.grades:
                        enrollmentData.append(enrollment.grades)
                        #print(f"Student: {user_name}, Scores: {enrollment.grades}")
                    else:
                        enrollmentData.append("")
                        
                    courseData.append(enrollmentData)

        assignments = course.get_assignments()

        for assignment in assignments:

            assignmentData = []

            if hasattr(assignment, 'name') and assignment.name:
                assignmentData.append(assignment.name)
                #print(assignment.name)
            else:
                assignmentData.append("")

            submission = assignment.get_submission(user.id, include=['score'])

            if hasattr(submission, 'score') and submission.score:
                assignmentData.append(submission.score)
                #print(submission.score)
            else:
                assignmentData.append(-1)

            if hasattr(assignment, 'points_possible') and assignment.points_possible:
                assignmentData.append(assignment.points_possible)
                #print(assignment.points_possible)
            else:
                assignmentData.append(-1)
                
            if hasattr(assignment, 'due_at') and assignment.due_at:
                assignmentData.append(assignment.due_at)
                #print(assignment.due_at)
            else:
                assignmentData.append(None)

            courseData.append(assignmentData)
            
        data.append(courseData)
        print("Done")
                
    return data
    

def cleanData(data):
    cleandata = []
    for courseList in data:
        coursedata = []
        gradeList = []
        for i in range(len(courseList)):
            if i == 0:
                coursedata.append(courseList[0]) #course id
            elif i == 1:
                coursedata.append(courseList[1]) #course name
            elif i == 2:
                coursedata.append(courseList[2]) #course enrollment
            else:
                item = courseList[i]
                name = item[0]
                score = item[1]
                total = item[2]
                date = None
                if item[3] is not None:
                    date = datetime.strptime(item[3], dateFormat)
                if (len(name) < 4 and 'q' in name.lower()) or 'quiz' in name.lower():
                    gradeList.append(QuizGrade(name, score, total, date))
                else:
                    gradeList.append(AssignmentGrade(name, score, total, date))
        coursedata.append(gradeList)
        cleandata.append(coursedata)
    return cleandata
        
        
class Grade():
    def __init__(self, name, score, total, date):
        self.__name = name
        self.__score = score
        self.__total = total
        self.__date = date
        
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, value):
        self.__name = value
    
    @property
    def score(self):
        return self.__score
    
    @score.setter
    def score(self, value):
        self.__score = value
    
    @property
    def total(self):
        return self.__total
    
    @total.setter
    def total(self, value):
        self.__total = value
        
    @property
    def date(self):
        return self.__date
    
    @date.setter
    def date(self, value):
        self.__date = value
        
    def __str__(self):
        strList = []
        strList.append(self.name)
        strList.append(self.score)
        strList.append(self.total)
        strList.append(self.date)
        return str(strList)
        
class AssignmentGrade(Grade):
    def isAssignment(self):
        return True
    
    def isQuiz(self):
        return False
    
    def __str__(self):
        strList = []
        strList.append(self.name)
        strList.append(self.score)
        strList.append(self.total)
        strList.append(self.date)
        strList.append('Assignment')
        return str(strList)
    
class QuizGrade(Grade):
    def isAssignment(self):
        return False
    
    def isQuiz(self):
        return True
    
    def __str__(self):
        strList = []
        strList.append(self.name)
        strList.append(self.score)
        strList.append(self.total)
        strList.append(self.date)
        strList.append('Quiz')
        return str(strList)