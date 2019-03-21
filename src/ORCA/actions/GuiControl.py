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

from ORCA.vars.Replace          import ReplaceVars
from ORCA.actions.Base          import cEventActionBase
from ORCA.utils.Sleep           import fSleep

import ORCA.Globals as Globals

__all__ = ['cEventActionsGuiControl']

class cEventActionsGuiControl(cEventActionBase):
    """ Gui Related Actions (showpage, ..) """

    def ExecuteActionShowPage(self,oAction):
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-ShowPage
        WikiDoc:TOCTitle:showpage
        The showpage action shows a specific page. You need to provide the name of the page as defined in your page definition. Do not mix file name and page name. If page name is 'settings' , the settings dialog will be  shown. For android devices, the settings dialog will be shown, if you press the settings button of your Android device.
        You can also set, how a page is displayed. For this, you can pass the same parameter as described in 'setpageeffect'. This is optional, if you don't pass this the last global effects are used. Passing effect types here will not change global settings.
        If a page get shown, the pagestop actions for the leaving page and the pagestart actions for the new page are executed. This will not happen if the new page/leaving page is a popup. If you want to get the pagestop actions/pagestart actions executed, if you show a popup, you have to set the enforce parameter. Pagestop actions and pagestart actions of the popup page are always executed
        You also could use a short form, where the pagename is added directly to the string. eg. string="showpage $(LASTPAGE)"

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |showpage
        |-
        |pagename
        |Page name, name of the page to display
        |-
        |effect
        |Page effect (optional)
        |-
        |direction
        |Page effect direction (optional)
        |-
        |enforce
        |Force pagestop actions & pagestop actions on popup call.
         Valid options are
         * ENFORCESTARTACTIONS
         * ENFORCESTOPACTIONS
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="gotolastpage" string="showpage" pagename="$var(LASTPAGE)" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEvenDispatcher.LogAction(u'ShowPage',oAction)
        uEffect         = ReplaceVars(oAction.dActionPars.get("effect",""))
        uDirection      = ReplaceVars(oAction.dActionPars.get("direction",""))
        uPageName       = ReplaceVars(oAction.dActionPars.get("pagename",""))
        uCurrentEffect  = ""
        if uEffect:
            uCurrentEffect=Globals.oTheScreen.uCurrentEffect
        if uDirection:
            uCurrentDirection= Globals.oTheScreen.uCurrentEffectDirection
        if uEffect or uDirection:
            self.ExecuteActionSetPageEffect(oAction)

        iRet=Globals.oTheScreen.ShowPage(uPageName)
        if uEffect:
            Globals.oTheScreen.SetPageEffect(uCurrentEffect)
        if uDirection:
            Globals.oTheScreen.SetPageEffectDirection(uDirection=uCurrentDirection)
        self.oEvenDispatcher.bDoNext = False
        fSleep(0.1)

        return iRet

    def ExecuteActionSetPageEffect(self,oAction):

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-SetPageEffect
        WikiDoc:TOCTitle:setpageffect
        = setpageeffect =
        With this action, you can set, how a page is displayed. This is a global parameter, which is active for all showpage actions, until it will be defined again. For some page effects like 'slide', you can set the direction, from where he new page should be shown. This is a global parameter, which is active for all showpage actions, until it will be defined again.
        Please play around with the page effects to get a visual expression of the effect. Find examples in the "showcase" definition

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |setpageeffect
        |-
        |effect
        |name of the effect, could be
        * 'no'
        * 'fade'
        * 'slide'
        * 'wipe'
        * 'swap'
        * 'fallout'
        * 'risein'
        |-
        |direction
        |direction of the page effect. Valid page effects directions are:
        *'left'
        *'right'
        *'up'
        *'down'
        |}</div>

        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
         <action name="Set effect page" string="setpageeffect" effect="side" direction="left"/>
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEvenDispatcher.LogAction(u'SetPageEffect',oAction)

        self.oEvenDispatcher.bDoNext = True
        uEffect    = ReplaceVars(oAction.dActionPars.get("effect",""))
        uDirection = ReplaceVars(oAction.dActionPars.get("direction",""))

        if Globals.oTheScreen.SetPageEffect(uEffect=uEffect):
            if Globals.oTheScreen.SetPageEffectDirection(uDirection=uDirection):
                return 0
            else:
                return 1

        else:
            return 1

