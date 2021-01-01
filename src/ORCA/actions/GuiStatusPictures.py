# -*- coding: utf-8 -*-
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

from ORCA.vars.Replace          import ReplaceVars
from ORCA.actions.Base          import cEventActionBase
from ORCA.Action                import cAction
from ORCA.actions.ReturnCode    import eReturnCode

import ORCA.Globals as Globals
__all__ = ['cEventActionsGuiStatusPictures']

class cEventActionsGuiStatusPictures(cEventActionBase):
    """ Actions for showing gui flags (busy, interface active, ...) """
    def ExecuteActionSetTransmitterPicture(self,oAction:cAction) -> eReturnCode:

        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-SetTransmitterPicture
        WikiDoc:TOCTitle:settransmitterpicture
        = settransmitterpicture =
        Sets the picture to activated while a interface is active. Good for indicating transmit status. By default it will be set in the appstart actions, so it will be used as a default for all pages. Otherwise you can set it for each page individually by setting it in the pagestartactions, or even change it as part of a button action. To avoid, that the picture will be shown right from the start, you should disable it in your widget definition.
        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |settransmitterpicture
        |-
        |picturename
        |Name of the picture to show
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="settransmitterpicture" picturename="Picture Transmit" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        uPictureName:str = ReplaceVars(oAction.dActionPars.get("picturename",""))
        self.oEventDispatcher.LogAction(uTxt=u'SetTransmitterPicture',oAction=oAction)
        if oAction.oParentWidget is not None:
            oAction.oParentWidget.oParentScreenPage.SetTransmitterPicture(uTransmitterPictureName=uPictureName)
        else:
            Globals.oTheScreen.uDefaultTransmitterPictureName = uPictureName
        return eReturnCode.Nothing

    def ExecuteActionSetWaitPicture(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-SetWaitPicture
        WikiDoc:TOCTitle:setwaitpicture
        = setwaitpicture =
        Sets the picture to activated while an internal step blocks the app (eg. Creation of a page). Good for indicating a wait status. It will be set as default in the appstart actions, so it will be used as a default for all pages. Otherwise you can set it for each page individually by setting it in the pagestartactions, or even change it as part of a button action.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |setwaitpicture
        |-
        |picturename
        |Name of the picture to show
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="setwaitpicture" picturename="Picture Wait" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        uPictureName:str = ReplaceVars(oAction.dActionPars.get("picturename",""))
        self.oEventDispatcher.LogAction(uTxt=u'SetWaitPicture',oAction=oAction)
        if oAction.oParentWidget is not None:
            oAction.oParentWidget.oParentScreenPage.SetWaitPicture(uWaitPictureName=uPictureName)
        else:
            Globals.oTheScreen.uDefaultWaitPictureName= uPictureName
        return eReturnCode.Nothing

    def ExecuteActionEnableTransmitterPicture(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-EnableTransmitterPicture
        WikiDoc:TOCTitle:enabletransmitterpicture
        = enabletransmitterpicture =
        Shows the Transmitterpicture. ORCA shows the transmitterpicture by default, if a command if send to an interface. There is no need to call it manually, but you can do so if required.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |enabletransmitterpicture
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="enabletransmitterpicture" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(uTxt=u'EnableTransmitterPicture',oAction=oAction)
        self.oEventDispatcher.bDoNext = False
        if Globals.oTheScreen.oCurrentPage is not None:
            if Globals.oTheScreen.oCurrentPage.oWidgetPictureTransmit is not None:
                Globals.oTheScreen.oCurrentPage.oWidgetPictureTransmit.EnableWidget(bEnable=True)
        return eReturnCode.Nothing

    def ExecuteActionDisableTransmitterPicture(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-DisableTransmitterPicture
        WikiDoc:TOCTitle:disabletransmitterpicture
        = disabletransmitterpicture =
        Hides the Transmitterpicture. ORCA hides the transmitterpicture by default, after a command has been send to an interface. There is no need to call it manually, but you can do so if required.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |disabletransmitterpicture
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="disabletransmitterpicture" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.bDoNext = False
        self.oEventDispatcher.LogAction(uTxt=u'DisableTransmitterPicture',oAction=oAction)
        if Globals.oTheScreen.oCurrentPage is not None:
            if Globals.oTheScreen.oCurrentPage.oWidgetPictureTransmit is not None:
                Globals.oTheScreen.oCurrentPage.oWidgetPictureTransmit.EnableWidget(bEnable=False)
        return eReturnCode.Nothing

    def ExecuteActionEnableWaitPicture(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-EnableWaitPicture
        WikiDoc:TOCTitle:enablewaitpicture
        = enablewaitpicture =
        Shows the wait picture.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |enablewaitpicture
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="enablewaitpicture" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(uTxt=u'EnableWaitPicture',oAction=oAction)
        self.oEventDispatcher.bDoNext = False
        if Globals.oTheScreen.oCurrentPage is not None:
            if Globals.oTheScreen.oCurrentPage.oWidgetPictureWait is not None:
                Globals.oTheScreen.oCurrentPage.oWidgetPictureWait.EnableWidget(bEnable=True)
        return eReturnCode.Nothing

    def ExecuteActionDisableWaitPicture(self,oAction:cAction) -> eReturnCode:
        """
        WikiDoc:Doc
        WikiDoc:Context:ActionsDetails
        WikiDoc:Page:Actions-DisableWaitPicture
        WikiDoc:TOCTitle:disablewaitpicture
        = disablewaitpicture =
        Hides the wait picture.

        <div style="overflow:auto; ">
        {| class="wikitable"
        ! align="left" | Attribute
        ! align="left" | Description
        |-
        |string
        |disablewaitpicture
        |}</div>
        A short example:
        <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
        <action name="" string="disablewaitpicture" />
        </syntaxhighlight></div>
        WikiDoc:End
        """

        self.oEventDispatcher.LogAction(uTxt=u'DisableWaitPicture',oAction=oAction)
        self.oEventDispatcher.bDoNext = False
        if Globals.oTheScreen.oCurrentPage is not None:
            if Globals.oTheScreen.oCurrentPage.oWidgetPictureWait is not None:
                Globals.oTheScreen.oCurrentPage.oWidgetPictureWait.EnableWidget(bEnable=False)
        return eReturnCode.Nothing

