# -*- coding: utf-8 -*-  
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionCommentData, ActionRenameData
from com.pnfsoftware.jeb.core.units.code.android import IApkUnit
from java.lang import Runnable

###############################
pkg = ""
###############################

class eseJEB2DeobscureClass(IScript):
    def run(self, ctx):
        ctx.executeAsync("Running deobscure class ...", JEB2AutoRename(ctx))
        print('Done')


class JEB2AutoRename(Runnable):
    def __init__(self, ctx):
        self.ctx = ctx

    def run(self):
        ctx = self.ctx
        engctx = ctx.getEnginesContext()
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

        units = RuntimeProjectUtil.findUnitsByType(prj, IDexUnit, False)

        for unit in units:
            classes = unit.getClasses()
            if classes:
                for clazz in classes:
                    sourceIndex = clazz.getSourceStringIndex()
                    clazzAddress = clazz.getAddress()
                    if pkg in clazzAddress:
                    	if sourceIndex == -1 or '$' in clazzAddress:# Do not rename inner class
                        	# print('without have source field', clazz.getName(True))
                        	continue

                    	sourceStr = str(unit.getString(sourceIndex))
                    	if '.java' in sourceStr:
                        	sourceStr = sourceStr[:-5]

                    	# print(clazz.getName(True), sourceIndex, sourceStr, clazz)
                    	if clazz.getName(True) != sourceStr:
                        	self.comment_class(unit, clazz, clazz.getName(True))  # Backup origin clazz name to comment
                        	self.rename_class(unit, clazz, sourceStr, True)  # Rename to source name

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

    def rename_class(self, unit, originClazz, sourceName, isBackup):
        actCtx = ActionContext(unit, Actions.RENAME, originClazz.getItemId(), originClazz.getAddress())
        actData = ActionRenameData()
        actData.setNewName(sourceName)

        if unit.prepareExecution(actCtx, actData):
            try:
                result = unit.executeAction(actCtx, actData)
                if result:
                    print('rename to %s success!' % sourceName)
                else:
                    print('rename to %s failed!' % sourceName)
            except Exception, e:
                print (Exception, e)

    def comment_class(self, unit, originClazz, commentStr):
        actCtx = ActionContext(unit, Actions.COMMENT, originClazz.getItemId(), originClazz.getAddress())
        actData = ActionCommentData()
        actData.setNewComment(commentStr)

        if unit.prepareExecution(actCtx, actData):
            try:
                result = unit.executeAction(actCtx, actData)
                if result:
                    print('comment to %s success!' % commentStr)
                else:
                    print('comment to %s failed!' % commentStr)
            except Exception, e:
                print (Exception, e)
