# -*- coding: utf-8 -*-
#

"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2020  Carsten Thielepape
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

from typing                                 import Dict
from typing                                 import Union
from typing                                 import Tuple

from ORCA.scripts.BaseScript                import cBaseScript
from ORCA.utils.FileName                    import cFileName

from ORCA.utils.LogError                    import LogError
from ORCA.utils.LogError                    import LogErrorSmall
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.utils.TypeConvert                 import ToDic
from ORCA.vars.Replace                      import ReplaceVars

from ORCA.ui.ShowErrorPopUp                 import ShowErrorPopUp
from ORCA.Action                            import cAction

import ORCA.Globals as Globals


'''
<root>
  <repositorymanager>
    <entry>
      <name>HUE Helper Script</name>
      <description language='English'>HUE Helper Script</description>
      <description language='German'>HUE Hilfs - Skript</description>
      <author>Carsten Thielepape</author>
      <version>5.0.4</version>
      <minorcaversion>5.0.4</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/helper/helper_hue</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/helper_hue.zip</sourcefile>
          <targetpath>scripts/helper</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''


# noinspection PyUnusedLocal
class cScript(cBaseScript):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-helper_hue
    WikiDoc:TOCTitle:Helper Script Evaluate HUE Status
    = HUE Helper =

    This is a helper script for HUE commands
    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |cmd_type
    |The requested helper function: can be "evaluate_status","evaluate_light","RGB2XY" or XY2RGB
    |-
    |result
    |The result of a request (in for "evaluate_status","evaluate_light".
     This should be the raw result of either the status request to the bridge hue, or from a single lights status
    |-
    |index
    |For "evaluate_light": The Hue Light index of the light
    |-
    |x
    |For "XY2RGB": the X Value of the light color to convert
    |-
    |y
    |For "XY2RGB": the Y Value of the light color to convert
    |-
    |r
    |For "RGB2XY": the Red Value of the light color to convert
    |-
    |g
    |For "RGB2XY": the Green Value of the light color to convert
    |-
    |b
    |For "RGB2XY": the Blue Value of the light color to convert
    |-
    |retvar
    |The variable prefix where the result variable will get set
    |}</div>

    Remarks:
    "evaluate_status" will set a list a variables according to list of all lamps and groups in the following format (as an array)
    "evaluate_light" will set a list a variables in the same format as "evalutae status" but not as an array


    WikiDoc:End
    """

    def __init__(self):
        super().__init__()
        self.uType:str                  = u'HELPERS'
        self.uIniFileLocation:str       = u"none"
        self.dStatus:Dict               = {}
        self.oHueConverter              = None

    def Init(self, uObjectName: str, oFnObject: Union[cFileName, None] = None) -> None:
        """ Main Init, loads the HueConverter Script"""
        super().Init(uObjectName=uObjectName,oFnObject=oFnObject)
        self.oHueConverter = self._LoadHueConverter()


    def RunScript(self, *args, **kwargs) -> Union[Dict,None]:
        """ Main Entry point, parses the cmd_type and calls the relevant functions """
        try:
            if 'cmd_type' in kwargs:
                uCmdType = kwargs['cmd_type']
                if uCmdType == u'evaluate_status':
                    self.DumpStatus(**kwargs)
                    return None
                if uCmdType == u'evaluate_light':
                    self.DumpLight(**kwargs)
                    return None
                if uCmdType == u'evaluate_group':
                    self.DumpGroup(**kwargs)
                    return None
                if uCmdType == u'RGB2XY':
                    self.RGB2XY(**kwargs)
                    return None
                if uCmdType == u'XY2RGB':
                    self.XY2RGB(**kwargs)
                    return None

            return None
        except Exception as e:
            LogErrorSmall(uMsg="Can't run Hue Helper script, invalid parameter",oException=e)
            return None


    def DumpLight(self,**kwargs) -> None:
        """ Dumps a spezific light status set into customs vars """
        try:

            vResult = kwargs['result']
            if isinstance(vResult,str):
                vResult = ToDic(ReplaceVars(vResult))

            dResult:Dict        = vResult
            uPrefix:str         = kwargs.get('retvar','')
            uLightKey:str       = kwargs.get('index', '')
            if uPrefix=='':
                oAction:cAction =kwargs['oAction']
                if oAction is not None:
                    uPrefix=oAction.uRetVar

            self.DumpSingleLight(iID=-1,uLightKey= uLightKey,dLight=dResult,uPrefix= uPrefix,uType=u'Light')
            return None
        except Exception as e:
            LogErrorSmall(uMsg="DumpLight: Error parsing HUE Bridge response",oException=e)
            return None

    def DumpGroup(self,**kwargs) -> None:
        """ Dumps a specific light status set into customs vars """
        try:
            vResult = kwargs['result']
            if isinstance(vResult,str):
                vResult = ToDic(ReplaceVars(vResult))

            dResult:Dict     = vResult
            uPrefix:str      = kwargs.get('retvar','')
            uLightKey:str    = kwargs.get('index', '')
            if uPrefix=='':
                oAction:cAction=kwargs['oAction']
                if oAction is not None:
                    uPrefix=oAction.uRetVar

            self.DumpSingleLight(iID=-1, uLightKey=uLightKey,dLight=dResult, uPrefix=uPrefix, uType=u'Group')
            return None
        except Exception as e:
            LogErrorSmall(uMsg="DumpGroup: Error parsing HUE Bridge response",oException=e)
            return None

    def DumpStatus(self,**kwargs) -> None:
        """ Dumps the lights and groups status into varsvars """
        try:
            vResult = kwargs['result']
            if isinstance(vResult,str):
                vResult = ToDic(ReplaceVars(vResult))

            dResult:Dict = vResult
            self.dStatus = dResult
            uPrefix:str = kwargs.get('retvar','')
            if uPrefix=='':
                oAction:cAction = kwargs['oAction']
                if oAction is not None:
                    uPrefix=oAction.uRetVar
            dLights:Dict = dResult['lights']
            dGroups:Dict = dResult['groups']

            # Vars for Lights & Groups in one list
            iIndex:int=0
            for uLightKey in dLights:
                self.DumpSingleLight(iIndex,uLightKey,dLights[uLightKey],uPrefix,"Light")
                iIndex+=1
            for uGroupKey in dGroups:
                self.DumpSingleLight(iIndex,uGroupKey,dGroups[uGroupKey],uPrefix,"Group")
                iIndex+=1
            return None
        except Exception as e:
            LogErrorSmall(uMsg="DumpStatus: Error parsing HUE Bridge response",oException=e)
            return None

    def RGB2XY(self,**kwargs) -> None:
        """ Converts rgb values to hue xy and dumps it into vars """
        try:
            fR:float         = ToFloat(ReplaceVars(kwargs.get('r',1.0)))
            fG:float         = ToFloat(ReplaceVars(kwargs.get('g',1.0)))
            fB:float         = ToFloat(ReplaceVars(kwargs.get('b',1.0)))
            uPrefix:str      = ReplaceVars(kwargs.get('retvar',''))
            uLightKey:str    = ReplaceVars(kwargs.get('index', ''))
            uType:str        = ReplaceVars(kwargs.get('type', 'Light'))
            if uType == "Group":
                uType="groups"
            else:
                uType="lights"

            tGammut:Tuple    = self._GetGamut(self.dStatus[uType][uLightKey].get('modelid', ""))
            oConverter = self.oHueConverter.Converter(tGammut)
            x,y        = oConverter.rgb_to_xy(fR, fG, fB)
            if uPrefix=='':
                oAction=kwargs['oAction']
                if oAction is not None:
                    uPrefix=oAction.uRetVar

            self.oResultParser.SetVar2(str(x), "", uPrefix, u'Storing X-Value', uAddName=u"_x")
            self.oResultParser.SetVar2(str(y), "", uPrefix, u'Storing Y-Value', uAddName=u"_y")
            return None
        except Exception as e:
            LogErrorSmall(uMsg="RGB2XY: Error parsing parameter",oException=e)
            return None

    def XY2RGB(self,**kwargs) -> None:
        """ Converts HUE xy to rgb and dumps it into vars """
        try:
            r:float
            g:float
            b:float
            fX:float
            fY:float

            fX         = ToFloat(kwargs.get('x',1.0))
            fY         = ToFloat(kwargs.get('y',1.0))
            uPrefix    = kwargs.get('retvar','')
            uLightKey  = kwargs.get('index', '')
            uType      = kwargs.get('type', 'Light')
            if uType == "Group":
                uType = "groups"
            else:
                uType = "lights"
            tGammut:Tuple = self._GetGamut(self.dStatus[uType][uLightKey].get('modelid', ""))
            oConverter    = self.oHueConverter.Converter(tGammut)
            r,g,b         = oConverter.xy_to_rgb(fX, fY)

            dStatusLight:Dict = self.dStatus.get(uLightKey,{})
            if len(dStatusLight)>0:
                uType=dStatusLight["lightstype"]

            self.oResultParser.SetVar2(str(r), "", uPrefix, u'Storing R-Value', uAddName=u"_r")
            self.oResultParser.SetVar2(str(g), "", uPrefix, u'Storing G-Value', uAddName=u"_g")
            self.oResultParser.SetVar2(str(b), "", uPrefix, u'Storing B-Value', uAddName=u"_b")
            return None
        except Exception as e:
            LogErrorSmall(uMsg="XY2RGB: Error parsing parameter",oException=e)
            return None

    def DumpSingleLight(self, iID:int,uLightKey:str, dLight:Dict, uPrefix:str,uType:str) -> None:
        """ Helper function to dump a light/group into vars """

        try:

            uIndex:str      = u""
            uOnTag:str      = u"on"
            uDetailsTag:str = u"state"

            r:float      = 1.0
            g:float      = 1.0
            b:float      = 1.0
            x:float      = 1.0
            y:float      = 1.0
            bri:float    = 1.0

            if iID >= 0:
                uIndex = u"[" + str(iID) + u"]"

            if uType == u"Group":
                uOnTag = u"all_on"
                uDetailsTag = "action"

            # Some devices return just single values (Philips is really bad!)
            x = dLight[uDetailsTag].get('xy', (1.0, 1.0))[0]
            y = dLight[uDetailsTag].get('xy', (1.0, 1.0))[1]

            uOn=str(dLight['state'][uOnTag])

            bri = dLight[uDetailsTag].get('bri', -1.0)
            if bri == -1.0:
                if uOn == "true":
                    bri = 254
                else:
                    bri = 0

            dLight["lightstype"] = uType
            self.oResultParser.SetVar2(uLightKey, "", uPrefix, u'Storing Light Configuration', uAddName=u"_index" + uIndex)
            self.oResultParser.SetVar2(uType, "", uPrefix, u'Storing Light Configuration', uAddName=u"_category" + uIndex)
            self.oResultParser.SetVar2(dLight['name'], "", uPrefix, u'Storing Light Configuration', uAddName=u"_name" + uIndex)
            self.oResultParser.SetVar2(str(dLight['state'][uOnTag]), "", uPrefix, u'Storing Light Configuration', uAddName=u"_on" + uIndex)
            self.oResultParser.SetVar2(dLight[uDetailsTag].get('colormode', "none"), "", uPrefix, u'Storing Light Configuration', uAddName=u"_colormode" + uIndex)
            self.oResultParser.SetVar2(str(bri), "", uPrefix, u'Storing Light Configuration', uAddName=u"_bri" + uIndex)
            self.oResultParser.SetVar2(str(dLight[uDetailsTag].get('ct', 0)), "", uPrefix, u'Storing Light Configuration', uAddName=u"_ct" + uIndex)
            self.oResultParser.SetVar2(str(dLight[uDetailsTag].get('hue', 0)), "", uPrefix, u'Storing Light Configuration', uAddName=u"_hue" + uIndex)
            self.oResultParser.SetVar2(str(dLight[uDetailsTag].get('hs', 0)), "", uPrefix, u'Storing Light Configuration', uAddName=u"_hs" + uIndex)
            self.oResultParser.SetVar2(dLight[uDetailsTag].get('effect', "none"), "", uPrefix, u'Storing Light Configuration', uAddName=u"_effect" + uIndex)
            self.oResultParser.SetVar2(str(x), "", uPrefix, u'Storing Light Configuration', uAddName=u"_x" + uIndex)
            self.oResultParser.SetVar2(str(y), "", uPrefix, u'Storing Light Configuration', uAddName=u"_y" + uIndex)
            self.oResultParser.SetVar2(str(dLight[uDetailsTag].get('sat', 0)), "", uPrefix, u'Storing Light Configuration', uAddName=u"_sat" + uIndex)
            self.oResultParser.SetVar2(dLight.get('manufacturername', ""), "", uPrefix, u'Storing Light Configuration', uAddName=u"_manufacturername" + uIndex)
            self.oResultParser.SetVar2(dLight['type'], "", uPrefix, u'Storing Light Configuration', uAddName=u"_type" + uIndex)
            self.oResultParser.SetVar2(dLight.get('modelid', ""), "", uPrefix, u'Storing Light Configuration', uAddName=u"_modelid" + uIndex)
            self.oResultParser.SetVar2(str(dLight['state'].get('any_on', "true")), "", uPrefix, u'Storing Group Configuration', uAddName=u"_all_on" + uIndex)
            self.oResultParser.SetVar2(dLight['state'].get('class', 'unknown'), "", uPrefix, u'Storing Group Configuration', uAddName=u"_class" + uIndex)

            if x!=0.0 or y!=0.0:
                tGammut = self._GetGamut(dLight.get('modelid', ""))
                oConverter = self.oHueConverter.Converter(tGammut)
                r, g, b = oConverter.xy_to_rgb(x, y, bri)
            self.oResultParser.SetVar2(str(r), "", uPrefix, u'Storing Light Configuration', uAddName=u"_r" + uIndex)
            self.oResultParser.SetVar2(str(g), "", uPrefix, u'Storing Light Configuration', uAddName=u"_g" + uIndex)
            self.oResultParser.SetVar2(str(b), "", uPrefix, u'Storing Light Configuration', uAddName=u"_b" + uIndex)
            return None
        except Exception as e:
            LogErrorSmall(uMsg="Error parsing HUE Bridge response for single light/group of status", oException=e)
            return None

    def _LoadHueConverter(self):
        """ Loads the hue converter script """
        oFnScript     = cFileName(self.oPathMyCode+"hue-python-rgb-converter-master/rgbxy") +"__init__.py"

        if not oFnScript.Exists():
            return None

        try:
            oModule=Globals.oModuleLoader.LoadModule(oFnModule=oFnScript,uModuleName='Module_Rgb_xy')
            oClasses=oModule.GetModule()
            return oClasses
        except Exception as e:
            uMsg=LogError(uMsg=u'Script Hue Helper: Fatal Error Loading HUE RGB Converter: '+oFnScript.string+ u' :',oException=e)
            ShowErrorPopUp(uMessage=uMsg)
            return None

    def _GetGamut(self,uModelId) ->Tuple:
        """ Gets the gammut for a model ID """
        try:
            return self.oHueConverter.get_light_gamut(uModelId)
        except Exception:
            # noinspection PyRedundantParentheses
            return (self.oHueConverter.XYPoint(1.0, 0.0), self.oHueConverter.XYPoint(0.0, 0.1), self.oHueConverter.XYPoint(0.0, 0.0),)

