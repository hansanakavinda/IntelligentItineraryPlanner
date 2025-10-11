@echo off

echo Activating virtual environment...
call ..\venv\Scripts\activate

echo Running Tests...
python test_haversin_distance.py

echo Running Test Case 2: K-means Clustering...
python test_kmeans.py

echo Running Test Case 3: Content-Based Filtering...
python test_content_filtering.py

echo.
pause