# Canvas Academic Insights

This package retrieves grade data from Canvas and provides visualizations and AI feedback.

## Description
Canvas Academic Insights is a Python package designed for comprehensive analysis and visualizations of academic performance metrics obtained from UBC's Canvas website via an API token. This package cleans and organizes raw data safely and generates multiple visual representations of academic performance across courses and over time. This package also provides AI-generated feedback, providing high-level interpretations of grade trends and constructing a weekly study plan for the student.

## Getting Started

### Dependencies
- `canvasapi`
- `numpy`
- `matplotlib`
- `ollama`

### Executing Program
Start the Ollama service for AI feedback; otherwise, AI feedback might be unavailable. Get your Canvas URL and token from UBC's website and enter them when prompted. There will be a prompt to obtain either AI feedback or a visualization of a course from this package; either enter `ai` or `visual`. If `ai` is entered, then an AI-generated summary of academic performance will be provided. If `visual` is selected, an additional prompt for a specific course index will be asked, which starts from 0 and ends at $n-1$, with $n$ being the number of courses obtained from the API. Once entered, visuals for overall academic performance will be produced, as well as course-specific visuals for the course index used.

## Authors
Yue Wang  
Richard  Hua  
Jordan Kaseram 

## Version History
- 0.1
    - Initial Release

