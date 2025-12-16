from canvasacademicinsights.canvasmain import canvasdataretriever as cr
from canvasacademicinsights.canvasvisualizer.canvassummaryvisualization import CanvasSummaryVisualizer
from canvasacademicinsights.canvasvisualizer.canvastimevisualization import CanvasTimeVisualization
from canvasacademicinsights.canvasaianalyzer import grades
from canvasacademicinsights.canvasaianalyzer import organize
from ast import literal_eval

def start():
    data = []
    data = processState("start", data)
    print("Finished retrieving Canvas data")
    data = processState("clean", data)
    print("Finished retrieving Canvas data")
    processState("choice", data)
    
def processState(state, data):
    match state:
        case "start":
            print("Welcome to the Canvas Academic Insights library, please enter some details before we can start")
            print("Note, if the library returns a forbidden error please make a list and add the id right before the error to the list")
            url = input("Enter the canvas url")
            token = input("Enter the canvas access token you created from your account")
            ids = input("Enter list of course ids to skip")
            
            if ids:
                ids = ids.replace('[','')
                ids = ids.replace(']','')
                ids = ids.split(',')
                ids = [int(idstring.strip()) for idstring in ids]
            else:
                ids = []
            
            try:
                raw = getData(url, token, ids)
            except cr.CanvasConnectionError:
                print("An error was encountered retrieving canvas data")
                return ''
            return raw
        case "clean":
            clean = cleanData(data)
            return clean
        case "choice":
            while True:
                choice = input("Enter visual or ai for summaries, or exit")
                if choice == 'visual':
                    processState("visual", data)
                    break
                elif choice == 'ai':
                    processState("ai", data)
                    break
                elif choice == 'exit':
                    break
        case "visual":
            print("The following is a list of courses");
            print(getCourses(data))
            index = int(input("Enter index number for visual summary"))
            getVisual(data, index)
            processState("choice", data)
        case "ai":
            getAIRecommendations(data)
            processState("choice", data)
        case _:
            pass

def getData(url, token, ids):
    data = cr.getData(url, token, ids)
    return data

def cleanData(data):
    data = cr.cleanData(data)
    return data

def getCourses(data):
    courses = []
    for course in data:
        coursename = course[1]
        courses.append(coursename)
    return courses

def getVisual(data, index):
    viz = CanvasSummaryVisualizer(data)
    viz.plot_overall_scores()
    viz.plot_grade_distribution(index)
    viz.plot_missing_assignments(index)
    viz.plot_num_assessments_per_course()

    time_viz = CanvasTimeVisualization(data)
    time_viz.plot_item_scores(index)
    time_viz.plot_all_last_graded_items_bar()
    time_viz.plot_weekly_average_score_heatmap()
    
def getAIRecommendations(data):
    grades.strongCourseAsk(data)
    grades.gradesAsk(data)
    organize.dueDatesAsk(data)
    organize.studyPlanAsk(data)