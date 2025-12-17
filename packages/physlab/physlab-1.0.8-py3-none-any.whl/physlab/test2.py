from core import *

graph1 = graph([0,1,2],[2.1, 4.3, 6.6])
graph1.add_title('bu')
graph1.quick_save('', format = 'pgf', subdir = 'tex')
