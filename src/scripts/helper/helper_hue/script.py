# -*- coding: utf-8 -*-
#

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

import imp

from ORCA.scripts.BaseScript                import cBaseScript
from ORCA.utils.FileName                    import cFileName

from ORCA.utils.LogError                    import LogError
from ORCA.utils.LogError                    import LogErrorSmall
from ORCA.utils.TypeConvert                 import ToFloat
from ORCA.ui.ShowErrorPopUp                 import ShowErrorPopUp

'''
<root>
  <repositorymanager>
    <entry>
      <name>HUE Helper Script</name>
      <description language='English'>HUE Helper Script</description>
      <description language='German'>HUE Hilfs - Skript</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/helper/helper_hue</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/helper_hue.zip</sourcefile>
          <targetpath>scripts/helper</targetpath>
        </source>
      </sources>
      <skipfiles>
        <file>scripts/helper/helper_hue/script.pyc</file>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

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
        cBaseScript.__init__(self)
        self.uType = u'HELPERS'
    def Init(self,uScriptName,uScriptFile=u''):
        """ Main Init, loads the HueConverter Script"""
        cBaseScript.Init(self,uScriptName,uScriptFile)
        self.oHueConverter = self._LoadHueConverter()
        self.dStatus = {}


    def RunScript(self, *args, **kwargs):
        """ Main Entry point, parses the cmd_type and calls the relevant functions """
        try:
            if 'cmd_type' in kwargs:
                uCmdType = kwargs['cmd_type']
                if uCmdType == u'evaluate_status':
                    return self.DumpStatus(**kwargs)
                if uCmdType == u'evaluate_light':
                    return self.DumpLight(**kwargs)
                if uCmdType == u'evaluate_group':
                    return self.DumpGroup(**kwargs)
                if uCmdType == u'RGB2XY':
                    return self.RGB2XY(**kwargs)
                if uCmdType == u'XY2RGB':
                    return self.XY2RGB(**kwargs)

        except Exception as e:
            LogErrorSmall("Can't run Hue Helper script, invalid parameter",e)
            return 1


    def DumpLight(self,**kwargs):
        """ Dumps a spezific light status set into customs vars """
        try:
            dResult     = kwargs['result']
            uPrefix     = kwargs.get('retvar','')
            uLightKey   = kwargs.get('index', '')
            if uPrefix=='':
                oAction=kwargs['oAction']
                if oAction is not None:
                    uPrefix=oAction.uRetVar

            self.DumpSingleLight(-1, uLightKey, dResult, uPrefix, u'Light')
        except Exception as e:
            LogErrorSmall("DumpLight: Error parsing HUE Bridge response",e)
        return 0

    def DumpGroup(self,**kwargs):
        """ Dumps a spezific light status set into customs vars """
        try:
            dResult     = kwargs['result']
            uPrefix     = kwargs.get('retvar','')
            uLightKey   = kwargs.get('index', '')
            if uPrefix=='':
                oAction=kwargs['oAction']
                if oAction is not None:
                    uPrefix=oAction.uRetVar

            self.DumpSingleLight(-1, uLightKey, dResult, uPrefix, u'Group')
        except Exception as e:
            LogErrorSmall("DumpGroup: Error parsing HUE Bridge response",e)
        return 0

    def DumpStatus(self,**kwargs):
        """ Dumps the lights and groups status into varsvars """
        try:
            dResult = kwargs['result']
            self.dStatus = dResult
            uPrefix = kwargs.get('retvar','')
            if uPrefix=='':
                oAction=kwargs['oAction']
                if oAction is not None:
                    uPrefix=oAction.uRetVar
            dLights = dResult['lights']
            dGroups = dResult['groups']

            '''
            # Vars for Lights only
            iIndex=0
            for uLightKey in dLights:
                self.DumpSingleLight(iIndex,uLightKey,dLights[uLightKey],uPrefix,"Light")
                iIndex+=1

            # Vars for Groups only
            dGroups = dResult['groups']
            iIndex=0
            for uGroupKey in dGroups:
                self.DumpSingleLight(iIndex,uGroupKey,dGroups[uGroupKey],uPrefix,"Group")
                iIndex+=1
            '''

            # Vars for Lights & Groups in one list
            iIndex=0
            for uLightKey in dLights:
                self.DumpSingleLight(iIndex,uLightKey,dLights[uLightKey],uPrefix,"Light")
                iIndex+=1
            for uGroupKey in dGroups:
                self.DumpSingleLight(iIndex,uGroupKey,dGroups[uGroupKey],uPrefix,"Group")
                iIndex+=1
        except Exception as e:
            LogErrorSmall("DumpStatus: Error parsing HUE Bridge response",e)
        return 0

    def RGB2XY(self,**kwargs):
        """ Converts rgb values to hue xy and dumps it into vars """
        try:
            fR         = ToFloat(kwargs.get('r',1.0))
            fG         = ToFloat(kwargs.get('g',1.0))
            fB         = ToFloat(kwargs.get('b',1.0))
            uPrefix    = kwargs.get('retvar','')
            uLightKey  = kwargs.get('index', '')
            uType      = kwargs.get('type', 'Light')
            if uType == "Group":
                uType="groups"
            else:
                uType="lights"

            tGammut    = self._GetGamut(self.dStatus[uType][uLightKey].get('modelid', ""))
            oConverter = self.oHueConverter.Converter(tGammut)
            x,y        = oConverter.rgb_to_xy(fR, fG, fB)
            if uPrefix=='':
                oAction=kwargs['oAction']
                if oAction is not None:
                    uPrefix=oAction.uRetVar

            self.oResultParser.SetVar2(str(x), "", uPrefix, u'Storing X-Value', uAddName=u"_x")
            self.oResultParser.SetVar2(str(y), "", uPrefix, u'Storing Y-Value', uAddName=u"_y")
        except Exception as e:
            LogErrorSmall("RGB2XY: Error parsing parameter",e)
        return 0


    def XY2RGB(self,**kwargs):
        """ Converts HUE xy to rgb and dumps it into vars """
        try:
            fX         = ToFloat(kwargs.get('x',1.0))
            fY         = ToFloat(kwargs.get('y',1.0))
            uPrefix    = kwargs.get('retvar','')
            uLightKey  = kwargs.get('index', '')
            uType      = kwargs.get('type', 'Light')
            if uType == "Group":
                uType = "groups"
            else:
                uType = "lights"
            tGammut = self._GetGamut(self.dStatus[uType][uLightKey].get('modelid', ""))
            oConverter = self.oHueConverter.Converter(tGammut)
            r,g,b       = oConverter.xy_to_rgb(fX, fY)

            dStatusLight = self.dStatus.get(uLightKey,{})
            if len(dStatusLight)>0:
                uType=dStatusLight["lightstype"]

            self.oResultParser.SetVar2(str(r), "", uPrefix, u'Storing R-Value', uAddName=u"_r")
            self.oResultParser.SetVar2(str(g), "", uPrefix, u'Storing G-Value', uAddName=u"_g")
            self.oResultParser.SetVar2(str(b), "", uPrefix, u'Storing B-Value', uAddName=u"_b")
        except Exception as e:
            LogErrorSmall("XY2RGB: Error parsing parameter",e)
        return 0


    def DumpSingleLight(self, iID,uLightKey, dLight, uPrefix,uType):
        """ Helper function to dump a light/group into vars """

        try:

            uIndex = u''
            uOnTag = u"on"
            uDetailsTag = "state"

            r      = 1.0
            g      = 1.0
            b      = 1.0
            x      = 1.0
            y      = 1.0
            bri    = 1.0

            if iID >= 0:
                uIndex = u"[" + str(iID) + u"]"

            if uType == u"Group":
                uOnTag = u"all_on"
                uDetailsTag = "action"

            # Some devices return just single values (Philips is really bad!)
            x = dLight[uDetailsTag].get('xy', (1.0, 1.0))[0]
            y = dLight[uDetailsTag].get('xy', (1.0, 1.0))[1]

            uOn=str(dLight['state'][uOnTag])

            bri = dLight[uDetailsTag].get('bri', -1)
            if bri == -1:
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

            if (x!=0.0 or y!=0.0):
                tGammut = self._GetGamut(dLight.get('modelid', ""))
                oConverter = self.oHueConverter.Converter(tGammut)
                r, g, b = oConverter.xy_to_rgb(x, y, bri)
            self.oResultParser.SetVar2(str(r), "", uPrefix, u'Storing Light Configuration', uAddName=u"_r" + uIndex)
            self.oResultParser.SetVar2(str(g), "", uPrefix, u'Storing Light Configuration', uAddName=u"_g" + uIndex)
            self.oResultParser.SetVar2(str(b), "", uPrefix, u'Storing Light Configuration', uAddName=u"_b" + uIndex)
        except Exception as e:
            LogErrorSmall("Error parsing HUE Bridge response for single light/group of status", e)

    def _LoadHueConverter(self):
        """ Loads the hue converter script """
        oFnScript     = cFileName(self.oPathMyCode+"hue-python-rgb-converter-master/rgbxy") +"__init__.py"

        if not oFnScript.Exists():
            return None

        try:
            oModule = imp.load_source('Module_Rgb_xy', oFnScript.string)
            return oModule
        except Exception as e:
            uMsg=LogError(u'Script Hue Helper: Fatal Error Loading HUE RGB Converter: '+oFnScript.string+ u' :',e)
            ShowErrorPopUp(uMessage=uMsg)
            return None

    def _GetGamut(self,uModelId):
        """ Gets the gammut for a model ID """
        try:
            return self.oHueConverter.get_light_gamut(uModelId)
        except Exception as e:
            return (self.oHueConverter.XYPoint(1.0, 0.0), self.oHueConverter.XYPoint(0.0, 0.1), self.oHueConverter.XYPoint(0.0, 0.0),)

