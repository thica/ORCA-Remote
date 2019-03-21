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

from kivy.logger            import Logger

from ORCA.utils.LogError    import LogError
from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp

from ORCA.vars.Replace      import ReplaceVars
from ORCA.utils.TypeConvert import ToFloat2
from ORCA.Action            import cAction

# One Character Conditions at the end
aConditions = [u'==', u'!=', u'<>', u'>=', u'<=', u'=', u'<', u'>']


def SplitCondition(uParCondition):
    """
    Splits a condition string by operators

    :rtype: list
    :param string uParCondition: Condition to split
    :return: list: [0]=uConditionCheckType, [1]=uConditionVar, {2]=uConditionValue
    """

    for uCondition in aConditions:
        tRsp = uParCondition.split(uCondition)
        if len(tRsp) == 2:
            uConditionCheckType = uCondition
            uConditionVar       = tRsp[0]
            uConditionValue     = tRsp[1]
            return uConditionCheckType,uConditionVar,uConditionValue

    Logger.error(u'Wrong Condition:', uParCondition)
    return "", "", ""


def CheckCondition(oPar):
    """
    Checks if a condition is true
    We check for Single Click and Double Click
    ConditionTypes: '==' , '!='  compares Strings
    ConditionTypes: '<' , '>' compares Integers )
    ConditionVar / ConditionValue: If Starts if '$' , the Application Vars are referenced

    :rtype: bool
    :param cAction|dict oPar: Either an cAction or a dict
    :return: True, if condition checks to true
    """

    if oPar.__class__.__name__ == "cAction":
        oAction = oPar
        oPar = oAction.dActionPars
    else:
        oAction = cAction()

    uConditionCheckType = oPar.get(u'conditionchecktype')
    uCondition          = oPar.get(u'condition')
    uContext            = oPar.get(u"varcontext", "")

    if uConditionCheckType is None:
        if uCondition is None:
            return True

    uConditionVar = oPar.get(u'conditionvar')
    uConditionValue = oPar.get(u'conditionvalue')

    if uCondition != '' and uCondition is not None:
        uConditionCheckType, uConditionVar, uConditionValue = SplitCondition(uCondition)

    bRet = False

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
        uVar = ReplaceVars(uConditionVar, uContext)
        if uVar.startswith('$var('):
            uVar = ReplaceVars(uVar, uContext)

        uValue = ReplaceVars(uConditionValue, uContext)
        uConditionCheckType = ReplaceVars(uConditionCheckType, uContext)
        if uConditionCheckType == u'==' or uConditionCheckType == u'=':
            if uVar == uValue:
                bRet = True
        elif uConditionCheckType == u'!=' or uConditionCheckType == u'<>':
            if uVar != uValue:
                bRet = True
        else:
            fValue, bIsValue = ToFloat2(uValue)
            fVar, bIsVar = ToFloat2(uVar)

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
        uMsg = LogError(u'CheckCondition: Cannot validate option: %s %s %s' % (uConditionVar, uConditionCheckType, uConditionValue), e)
        Logger.error(uMsg)
        ShowErrorPopUp(uMessage=uMsg)
        return False

    Logger.debug("Checking condition [%s]:[%s][%s][%s] returns %s" % (uConditionVar, uVar, uConditionCheckType, uValue[:100], str(bRet)))

    return bRet
