import sys
import os
import re
from datetime import datetime,timedelta
from typing import ClassVar, Protocol

if (len(sys.argv)<=2):
    str = ("Read dbg.txt and olemas32dbg.txt to anlyze elapse time. \n"
            "Usage:\n"
            "   py {} <TagFile> olemas32dbg.txt\n"
            .format(os.path.basename(__file__))
    )
    print(str)
    sys.exit()

strTagFile = sys.argv[1]
strOlemas32dbgtxt = sys.argv[2]

# For each elapse(Start, End)
class CElapse:
    tSta = datetime.min
    tEnd = datetime.min
    tDiffms: int = 0
    def CalcTimeDiff(self):
        tDiff = self.tEnd - self.tSta
        self.tDiffms = tDiff.seconds*1000 + tDiff.microseconds//1000
    def SetStart(self, dt: datetime):
        self.tSta = dt
    def SetEnd(self, dt: datetime):
        self.tEnd = dt
        self.CalcTimeDiff()

# SuperClass
class CTimeDiff:
    strTag: str
    rgElapse: list[CElapse]
    nOutputCount: ClassVar[int] = 1 # Last nOutput
    rSta: str
    rEnd: str

    tBeginChk = datetime.min # Collect time when only after tBegin
    tFinishChk = datetime.max # Collect time when only before tFinish
    bStarted = False # True after "Start". False after "End"

    def __init__(self, otBeginChk:datetime=datetime.min, otFinishChk:datetime=datetime.max):
        self.tBeginChk = otBeginChk
        self.tFinishChk = otFinishChk
        self.rgElapse = []

    def __init__(self, ostrTag:str, otrSta:str, otrEnd:str, otBeginChk:datetime=datetime.min, otFinishChk:datetime=datetime.max):
        self.strTag = ostrTag
        self.rSta = otrSta
        self.rEnd = otrEnd
        self.tBeginChk = otBeginChk
        self.tFinishChk = otFinishChk
        self.rgElapse = []

    def Check(self, line: str):
        if (m := re.search(self.rSta, line)): # Start Time
            strTime = m.group(1)
            dt = datetime.strptime(strTime, "%Y-%m-%dT%H:%M:%S.%f")
            if(dt>=self.tBeginChk and dt<self.tFinishChk):
                self.Elp_Append()
                self.Elp_GetLast().SetStart(dt)
                self.bStarted = True
        if (m := re.search(self.rEnd, line)): # End Time
            if(self.bStarted):
                strTime = m.group(1)
                dt = datetime.strptime(strTime, "%Y-%m-%dT%H:%M:%S.%f")
                self.Elp_GetLast().SetEnd(dt)
                self.bStarted = False

    def Elp_Append(self) :
        self.rgElapse.append(CElapse())

    def Elp_GetLast(self) -> CElapse:
        return self.rgElapse[-1]
    
    def PrintLast(self):
        if(len(self.rgElapse)>0):
            # Count from last n output
            for i in range(self.nOutputCount, 0, -1): # 2, 1
                i2 = len(self.rgElapse) - i
                if (i2>=0):
                    print(self.strTag + " ", self.rgElapse[i2].tDiffms)
#            print(type(self).__name__ + " ", self.rgElapse[-1].tDiffms)

    def PrintEach(self):
        if(len(self.rgElapse)>0):
            for i in range(0, len(self.rgElapse)):
                print(self.strTag + " ", self.rgElapse[i].tDiffms)

    def PrintTotal(self):
        if(len(self.rgElapse)>0):
            tTotalDiffms = 0
            for i in range(0, len(self.rgElapse)):
                tTotalDiffms += self.rgElapse[i].tDiffms
            print(self.strTag + " ", tTotalDiffms)


strRegDateTime = r"(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\d)" # yyyy-mm-ddTHH:mm:ss.fff

rgTd: list[CTimeDiff] = []

with open(strTagFile, errors='ignore') as fIn:
    strTags = fIn.readlines()
    for i in range(len(strTags)//3):
        strTag = strTags[i*3].strip()
        strSta = strRegDateTime + " " + strTags[i*3+1].strip()
        strEnd = strRegDateTime + " " + strTags[i*3+2].strip()
        td = CTimeDiff(strTag, strSta, strEnd)
        rgTd.append(td)

with open(strOlemas32dbgtxt, errors='ignore') as fIn:
    for i,line in enumerate(fIn):
        for td in rgTd:
            td.Check(line)

for td in rgTd:
    td.PrintEach()
