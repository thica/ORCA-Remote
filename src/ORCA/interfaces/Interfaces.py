# -*- coding: utf-8 -*-
"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2019  Carsten Thielepape
    Please contact me by : http://www.orca-remote.org/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import  imp

from kivy.logger            import Logger

from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.FileName    import cFileName
from ORCA.utils.LogError    import LogError
from ORCA.vars.Replace      import ReplaceVars

import ORCA.Globals as Globals

class cInterFaces(object):
    """ A container class for all interfaces """
    def __init__(self):
        #list of all Interfaces
        self.oInterfaceList              = []
        self.dInterfaces                 = {}
        self.dModules                    = {}
        self.uInterFaceListSettingString = u''
        self.dUsedInterfaces             = {}

    def InitVars(self):
        """ Clears the list of interfaces """
        self.dUsedInterfaces.clear()

    def Init(self):
        """ dummy """
        pass
    def DeInit(self):
        """ deinits the interfaces object """
        for oInterfaceName in self.dInterfaces:
            self.dInterfaces[oInterfaceName].DeInit()

    def Clear(self):
        """ clears the lst of interfaces """
        self.DeInit()
        del self.oInterfaceList[:]
        self.dInterfaces.clear()

    def LoadInterfaceList(self):
        """ loads the list of all inerfaces """
        Logger.debug (u'Interfaces: Loading Interface List')
        self.uInterFaceListSettingString = u''
        self.oInterfaceList = Globals.oPathInterface.GetFolderList()
        self.oInterfaceList.sort(key = lambda x: x)

        for uInterFaceName in self.oInterfaceList:
            self.uInterFaceListSettingString+=u'"{0}",'.format(uInterFaceName)
        self.uInterFaceListSettingString=self.uInterFaceListSettingString[:-1]

    def GetInterface(self,uInterFaceName):
        """
        Returns an cInterface class

        :rtype: cBaseInterFace
        :param string uInterFaceName: The name of the interface
        :return: The interface class (cBaseInterface)
        """

        return self.dInterfaces.get(uInterFaceName)


    def LoadInterface(self,uInterFaceName):
        """
        Loads an interface

        :rtype: module
        :param string uInterFaceName: The name of the interface
        :return: The interface module (not cBaseInterface)
        """
        if uInterFaceName in self.dInterfaces:
            return self.dModules.get(uInterFaceName)

        if uInterFaceName=="":
            return None
        Logger.info (u'Interfaces: Loading Interface: '+uInterFaceName)
        oFnInterfacePy  = cFileName(Globals.oPathInterface + uInterFaceName) + u'interface.py'
        oFnInterface    = cFileName(oFnInterfacePy)

        if not oFnInterface.Exists():
            LogError(u'Interfaces: Fatal Error Loading Interface,  Interface not found: '+uInterFaceName)
            return None

        try:
            oModule=self.dModules.get(uInterFaceName, imp.load_source('cInterface' + "_" + uInterFaceName, oFnInterface.string))
            self.dModules[uInterFaceName]=oModule
            oInterface = oModule.cInterface()
            oInterface.Init(uInterFaceName, oFnInterface)
            self.dInterfaces[uInterFaceName]=oInterface
            return oModule
        except Exception as e:
            uMsg=LogError(u'Interfaces: Fatal Error Loading Interface: '+uInterFaceName+ u' :',e)
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=uMsg, bAbort=True)
            return None

    def OnPause(self):
        """ Entry for on Pause """
        for oInterfaceName in self.dInterfaces:
            self.dInterfaces[oInterfaceName].OnPause()

    def OnResume(self):
        """ Entry for on resume """
        for oInterfaceName in self.dInterfaces:
            self.dInterfaces[oInterfaceName].OnResume()

    def RegisterInterFaces(self,uInterFaceName,fSplashScreenPercentageStartValue):

        """ we do it here, as we load only used interfaces, which we know after loading the definition """
        Logger.debug ('TheScreen: Register Interfaces')

        fSplashScreenPercentageRange=10.0

        if not uInterFaceName:
            fPercentage=fSplashScreenPercentageStartValue
            fPercentageStep=fSplashScreenPercentageRange/len(self.dUsedInterfaces)

            # Scheduling Register Interface
            aActions=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message the we register the interfaces','string':'showsplashtext','maintext':'$lvar(409)'}])

            #for Interface
            for uInterFaceName in self.oInterfaceList:
                for uKey in self.dUsedInterfaces:
                    uKey2=ReplaceVars(uKey)
                    if uKey2==uInterFaceName and uInterFaceName!=u'':
                        fPercentage=fPercentage+fPercentageStep
                        Globals.oEvents.AddToSimpleActionList(aActions,[{'name':'Update Percentage and Interface Name','string':'showsplashtext','subtext':uKey2,'percentage':str(fPercentage)},
                                                                                 {'name':'Register the Interface','string':'registerinterfaces','interfacename':uKey2}
                                                                                ])


                        break
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        else:
            self.LoadInterface(uInterFaceName)


    def DiscoverAll(self,uInterFaceName=u'', uConfigName=u'', bGui = False, bForce = False):
        # bForce not used (by now)
        if uInterFaceName == u'':
            aActions=[]
            for uInterFaceName in self.dInterfaces:
                oInterFace=self.dInterfaces[uInterFaceName]
                if oInterFace.oObjectConfig.oConfigParser.filename =='':
                    oInterFace.oObjectConfig.oConfigParser.LoadConfig(self)
                for uConfigName in oInterFace.oObjectConfig.oConfigParser.sections():
                    if uConfigName != "DEVICE_DEFAULT":
                        oSetting=oInterFace.GetSettingObjectForConfigName(uConfigName)
                        if bForce:
                            oSetting.aIniSettings.uOldDiscoveredIP = ""
                        if oSetting.aIniSettings.uHost=="discover" and oSetting.aIniSettings.uOldDiscoveredIP  == "":
                            Globals.oEvents.AddToSimpleActionList(aActions, [{'name': 'Discover single with gui', 'string': 'discover', 'interface': uInterFaceName, 'configname': uConfigName, 'gui': '1'}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
            return 0
        elif bGui:
            aActions=[]
            uAlias = Globals.oDefinitions.FindDefinitionAliasForInterfaceConfiguration(uInterFaceName=uInterFaceName, uConfigName=uConfigName)
            uDetail = "\n\n%s\n%s:%s" % (uAlias, uInterFaceName, uConfigName)
            Globals.oEvents.AddToSimpleActionList(aActions, [{'name': 'And Discover', 'string': 'call DiscoverSingle', 'DISCOVERINTERFACE': uInterFaceName, 'DISCOVERCONFIG': uConfigName, 'DISCOVERDETAILS': uDetail, 'gui':'0'}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        else:
            oInterFace = self.dInterfaces.get(uInterFaceName)
            if oInterFace:
                oSetting = oInterFace.GetSettingObjectForConfigName(uConfigName)
                if oSetting:
                    if oSetting.Discover():
                        return 0
        return 1


