# -*- coding: utf-8 -*-

from os import listdir
from os.path import isfile, join


imports = []

imports_qtcore = []
imports_qtgui = []
imports_qtwidgets = []

imports_lccolor = []
imports_lcdisplay = []
imports_lcgeometry = []
imports_lcmesh = []
imports_lctopology = []
imports_lcwidget = []

body = []

mydir = "app/models"
onlyfiles = [join(mydir, f) for f in listdir(mydir) if isfile(join(mydir, f))]
mydir = "app/views"
onlyfiles += [join(mydir, f) for f in listdir(mydir) if isfile(join(mydir, f))]
mydir = "app/controllers"
onlyfiles += [join(mydir, f) for f in listdir(mydir) if isfile(join(mydir, f))]


for file in onlyfiles:
    print(file)
    with open(file, encoding='utf-8') as f:
        lines = f.readlines()

        for n, line in enumerate(lines):
            if line[:6] == 'from .' or line[:1] == '#':
                continue

            if line[:4] == 'from' or line[:6] == 'import':
                imports.append(line)
            else:
                body.append(line)

f = open('full.txt', 'w', encoding='utf-8')

imports2 = sorted(set(imports))
imports = []
for s in imports2:
    if s[:25] == 'from PyQt5.QtCore import ':
        imports_qtcore += s[25:-1].split(', ')
    elif s[:24] == 'from PyQt5.QtGui import ':
        imports_qtgui += s[24:-1].split(', ')
    elif s[:28] == 'from PyQt5.QtWidgets import ':
        imports_qtwidgets += s[28:-1].split(', ')
    elif s[:26] == 'from libcore.color import ':
        imports_lccolor += s[26:-1].split(', ')
    elif s[:28] == 'from libcore.display import ':
        imports_lcdisplay += s[28:-1].split(', ')
    elif s[:29] == 'from libcore.geometry import ':
        imports_lcgeometry += s[29:-1].split(', ')
    elif s[:25] == 'from libcore.mesh import ':
        imports_lcmesh += s[25:-1].split(', ')
    elif s[:29] == 'from libcore.topology import ':
        imports_lctopology += s[29:-1].split(', ')
    elif s[:27] == 'from libcore.widget import ':
        imports_lcwidget += s[27:-1].split(', ')
    else:
        imports += s



imports += 'from PyQt5.QtCore import ' + ', '.join(set(imports_qtcore)) + "\n"
imports += 'from PyQt5.QtGui import ' + ', '.join(set(imports_qtgui)) + "\n"
imports += 'from PyQt5.QtWidgets import ' + ', '.join(set(imports_qtwidgets)) + "\n"

imports += 'from libcore.color import ' + ', '.join(set(imports_lccolor)) + "\n"
imports += 'from libcore.display import ' + ', '.join(set(imports_lcdisplay)) + "\n"
imports += 'from libcore.geometry import ' + ', '.join(set(imports_lcgeometry)) + "\n"
imports += 'from libcore.mesh import ' + ', '.join(set(imports_lcmesh)) + "\n"
imports += 'from libcore.topology import ' + ', '.join(set(imports_lctopology)) + "\n"
imports += 'from libcore.widget import ' + ', '.join(set(imports_lcwidget)) + "\n"

for s in imports:
    f.write(s)

for s in body:
    f.write(s)
