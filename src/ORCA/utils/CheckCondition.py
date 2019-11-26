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
from typing import List
from typing import Tuple
from typing import Dict
from typing import Union

from xml.etree.ElementTree           import Element


from kivy.logger            import Logger

from ORCA.utils.LogError    import LogError
from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp

from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.TypeConvert import ToFloat2
from ORCA.Action            import cAction



# One Character Conditions at the end
aConditions: List[str] = [u'==', u'!=', u'<>', u'>=', u'<=', u'=', u'<', u'>']

def SplitCondition(*,uCondition: str) -> Tuple[str,str,str]:
    """
    Splits a condition string by operators
    :param string uCondition: Condition to split
    :return: tuple: [0]=uConditionCheckType, [1]=uConditionVar, {2]=uConditionValue
    """
    for uConditionSeparator in aConditions:
        aRsp: List[str,str] = uCondition.split(uConditionSeparator)
        if len(aRsp) == 2:
            uConditionCheckType:str = uConditionSeparator
            uConditionVar:str       = aRsp[0]
            uConditionValue:str     = aRsp[1]
            return uConditionCheckType,uConditionVar,uConditionValue

    Logger.error(u'Wrong Condition:', uCondition)
    return "", "", ""

def CheckCondition(*,oPar: Union[Dict,cAction,Element]) -> bool:
    """
    Checks if a condition is true
    We check for Single Click and Double Click
    ConditionTypes: '==' , '!='  compares Strings
    ConditionTypes: '<' , '>' compares Integers )
    ConditionVar / ConditionValue: If Starts if '$' , the Application Vars are referenced

    :param cAction|dict oPar: Either an cAction or a dict
    :return: True, if condition checks to true
    """

    if oPar.__class__.__name__ == "cAction":
        oAction: cAction = oPar
        oPar = oAction.dActionPars
    else:
        oAction: cAction = cAction()

    uConditionCheckType: str = oPar.get(u'conditionchecktype')
    uCondition: str          = oPar.get(u'condition')
    uContext: str            = oPar.get(u"varcontext", "")

    if uConditionCheckType is None:
        if uCondition is None:
            return True

    uConditionVar: str   = oPar.get(u'conditionvar')
    uConditionValue: str = oPar.get(u'conditionvalue')

    if uCondition != '' and uCondition is not None:
        uConditionCheckType, uConditionVar, uConditionValue = SplitCondition(uCondition=uCondition)

    bRet: bool = False

    try:
        if not oAction.oParentWidget is None:
            if not oAction.uActionTapType == u'both':
                if oAction.uActionTapType == u'single':
                    if oAction.oParentWidget.bDoubleTap:
                        return bRet
                if oAction.uActionTapType == u'double':
                    if not oAction.oParentWidget.bDoubleTap:
                        return bRet

        if uConditionCheckType == u'':
            return True
        uVar: str = ReplaceVars(uConditionVar, uContext)
        if uVar.startswith('$var('):
            uVar = ReplaceVars(uVar, uContext)

        uValue: str              = ReplaceVars(uConditionValue, uContext)
        uConditionCheckType: str = ReplaceVars(uConditionCheckType, uContext)
        if uConditionCheckType == u'==' or uConditionCheckType == u'=':
            if uVar == uValue:
                bRet = True
        elif uConditionCheckType == u'!=' or uConditionCheckType == u'<>':
            if uVar != uValue:
                bRet = True
        else:
            fValue: float
            bIsValue: bool
            fVar: float
            bIsVar: bool
            fValue, bIsValue = ToFloat2(uValue)
            fVar, bIsVar     = ToFloat2(uVar)

            if bIsValue and bIsVar:
                if uConditionCheckType == u'>':
                    if fVar > fValue:
                        bRet = True
                elif uConditionCheckType == u'>=':
                    if fVar >= fValue:
                        bRet = True
                elif uConditionCheckType == u'<':
                    if fVar < fValue:
                        bRet = True
                elif uConditionCheckType == u'<=':
                    if fVar <= fValue:
                        bRet = True
    except Exception as e:
        ShowErrorPopUp(uMessage=LogError(uMsg=u'CheckCondition: Cannot validate option: %s %s %s' % (uConditionVar, uConditionCheckType, uConditionValue), oException=e))
        return False

    Logger.debug("Checking condition [%s]:[%s][%s][%s] returns %s" % (uConditionVar, uVar, uConditionCheckType, uValue[:100], str(bRet)))

    return bRet
