# coding: utf-8
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.output.text import ITextDocument
from com.pnfsoftware.jeb.core.units import INativeCodeUnit
from com.pnfsoftware.jeb.core.units.code.android import IApkUnit
from java.lang import Runnable
import re




#################################
Findstr = [

'System.loadLibrary'
]
other = ['umeng/', 'baidu/','google/','tencent/','cloudwalk/','kaer/','iflytek/']

pkg = ""  #自动获取

prinT = []

########################

class DecompileAll(Runnable):
  def __init__(self, ctx):
    self.ctx = ctx

  def run(self):
    self.outputDir = self.ctx.getBaseDirectory()
    engctx = self.ctx.getEnginesContext()
    if not engctx:
      print('Back-end engines not initialized')
      return

    projects = engctx.getProjects()
    if not projects:
      print('There is no opened project')
      return

    prj = projects[0]
    global pkg
    pkg = self.GetPackage(prj)

    codeUnits = RuntimeProjectUtil.findUnitsByType(prj, ICodeUnit, False)
    for codeUnit in codeUnits:
            self.decompileForCodeUnit(codeUnit)

  def GetPackage(self,prj):
    apk = RuntimeProjectUtil.findUnitsByType(prj, IApkUnit, False)[0]
    apkpkg = apk.getPackageName()
    print('Start from %s ------------------' %apkpkg)
    apkpkgname = apkpkg.split('.')
    pkgname = ""
    if len(apkpkgname)>2:
        pkgname = apkpkgname[0]+'/'+apkpkgname[1]+'/'+apkpkgname[2]
    else:
        pkgname = apkpkgname[0]+'/'+apkpkgname[1]
    return pkgname

  def decompileForCodeUnit(self, codeUnit):
    try:
      decomp = DecompilerHelper.getDecompiler(codeUnit)
      if not decomp:
        return
    except:
      pass
    if isinstance(codeUnit, INativeCodeUnit):
        methods = codeUnit.getMethods()
        if methods:
            for m in methods:
                a = m.getAddress()
                srcUnit = decomp.decompile(a)
                if srcUnit:
                    self.exportSourceUnit(srcUnit)
    else:
      allClasses = codeUnit.getClasses()
      for c in allClasses:
        if (c.getGenericFlags() & ICodeItem.FLAG_INNER) == 0:
          a = c.getAddress()
          if self.fitileo(a):
              srcUnit = decomp.decompile(a)
              if srcUnit:
                self.exportSourceUnit(srcUnit)

  def fitileo(self, a):
    for tt in other:
      if tt in a:
        return 0
    return 1

  def exportSourceUnit(self, srcUnit):
    ext = srcUnit.getFileExtension()
    csig = srcUnit.getFullyQualifiedName()
    subpath = csig[1:len(csig)-1]

    doc = self.getTextDocument(srcUnit)
    if not doc:
        return False
    text = self.formatTextDocument(doc)
    text = text.encode("utf-8")
    self.FindRe(text,subpath)
    #self.Findst(text,subpath)

  def FindRe(self,text,subpath):
    for ch in Findstr:
      pattern = re.compile(ch)
      matches = pattern.findall(text)
      if matches:
        sst = set(matches)
        matches = list(sst)
        for match in matches:
          prinT.append([match,subpath])

  def Findst(self,text,subpath):
    patt = re.compile(r'\"(\w+)\"')
    matts = patt.findall(text)
    if matts:
      sstt = set(matts)
      matts = list(sstt)
      for matt in matts:
        if len(matt)>=8 and len(matt)<=16:
          print("Find --> %-30s , From st---> %s" %(matt, subpath))

  def getTextDocument(self, srcUnit):
    formatter = srcUnit.getFormatter()
    if formatter and formatter.getDocumentPresentations():
      doc = formatter.getDocumentPresentations()[0].getDocument()
      if isinstance(doc, ITextDocument):
        return doc
    return None

  def formatTextDocument(self, doc):
    s = ''
    alldoc = doc.getDocumentPart(0, 10000000)
    for line in alldoc.getLines():
      s += line.getText().toString() + '\n'
    return s

class eseJEB2FindStr(IScript):
  def run(self, ctx):
    ctx.executeAsync("Find all...", DecompileAll(ctx))
    self.printall()
    print('Done.')

  def printall(self):
    pprint = self.sort1()
    #pprint = prinT
    print(len(pprint))
    for i in range(len(pprint)):
      maps = pprint[i]
      print("Find --> %-30s , From ---> %s" %(maps[0], maps[1]))

  def sort1(self):
    l = len(prinT)
    ppr = []
    for i in range(l):
        maxx = prinT[i][0]
        fgs = 1
        for k in range(len(ppr)):
            kk = ppr[k][0]
            if (maxx == kk) and (i!=0):
                fgs = 0
                break
        if fgs == 1:
            for j in range(i,l):
                cmpp = prinT[j][0]
                if cmpp == maxx:
                    ppr.append([maxx,prinT[j][1]])
    return ppr