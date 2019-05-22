import sympy, re, calcCalc
from PyQt4 import QtGui, QtCore



""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

RIGHT NOW:

Every input is cleaned (clean_up) and gets spit out nicely as a function 
and a variable (diff)

Need to still...
                 ...QTDesigner connections
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class myCalc(QtGui.QWidget, calcCalc.Ui_CalcCalc):
    
    def __init__(self, parent = None):
        super(myCalc,self).__init__(parent)
        #Why doesn't this work?
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.myInput.returnPressed.connect(self.processr)
        self.myOutput.setReadOnly(True)
        
    def processr(self):
        try:
            q = str(self.myInput.text())
            q = calcInput(q)
            q = re.sub(r'\*\*', "^", str(q))
        except:
            q = "Invald input"
        self.myOutput.setText(q)
        self.myInput.clear()
                
        

def clean_up(dirty): # Gets string, returns cleaned string
    
    #remove spaces
    nspaces = re.sub(r'\s+', "", dirty)
    
    #change ^ to **
    ncarrot = re.sub(r'\^', "**", nspaces)
    
    return ncarrot
    
def break_up(x): #Gets string of function, outputs ready for sympy function
    
    #cut between commas
    cut = re.split(r',', x)
    
    #Cut again to subtract left side from right if there is an equal sign
    if "=" in cut[0]:
        neq = re.split(r'\=',cut[0])
        func = "['" + neq[0] +"-" + neq[1] + "']"
    else: # no equals
        #Read in function from first half, variables from second half
        func = re.findall(r'([a-zA-Z0-9\*\-\+\\\(\)]+)', cut[0])
    
    var = re.findall(r'([a-zA-Z])', cut[1])
    

    #So func can have multiple inputs because there could be an imbedded
    # command, so we need to account for this...
    realfunc = str(func)[3:len(str(func))-2]
    realvar =  str(var)[2:len(str(var))-2]
    return [realfunc, realvar]
    
   
    
#inputr = raw_input("Enter Math Command:\n")
def calcInput(inputr):
    clean_up(inputr)
    raw = clean_up(inputr) #cleans up input

    #Finds commands: everything of 2 letters or more
    com = re.findall(r'([a-zA-Z]{2,})', raw)

    #No command, straight math
    if len(com) == 0:
        if "=" in raw:
            neq = re.split(r'\=',raw)
            func = "" + neq[0] + "-" + neq[1]
            var = re.findall(r'[a-zA-z]',raw)
            ans = sympy.solve(func,var[0])
        else:
            ans = sympy.sympify(raw)
    else:
        #Finds function, everything after first command
        func = re.split(com[0], raw)

        #Make it 2 strings so my life is easier
        func = str(func[1])
        build = break_up(func)
        myFunc = build[0]
        myVar = sympy.symbols(build[1])
    
        #com[0] is the first command of input
        if com[0] == 'diff' or com[0] == 'differentiate' or com[0] == 'derivative':
           ans = sympy.diff(myFunc,myVar)
        elif com[0] == "int" or com[0] == "integrate" or com[0] == "integral":
            ans = sympy.integrate(myFunc,myVar)
        elif com[0] == "sol" or com[0] == "solve" or com[0] == "solution":
            ans = sympy.solve(myFunc,myVar)
        
        else:
           ans = "I'm sorry, I don't understand the command ", com[0]
    
    return ans

def main():
    app = QtGui.QApplication([])
    x = myCalc()
    x.show()
    app.exec_()

    
    
if __name__ == "__main__":
    main()