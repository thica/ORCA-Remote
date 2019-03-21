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

from ORCA.vars.Access       import SetVar
from ORCA.vars.Access       import SetVarWithOutVarTranslation
from ORCA.vars.Access       import GetVar
from ORCA.vars.Replace      import ReplaceVars
from ORCA.vars.Helpers      import Round, Find_nth_Character
from ORCA.utils.LoadFile    import LoadFile
from ORCA.utils.LogError    import LogError
from ORCA.utils.TypeConvert import ToFloat
from ORCA.utils.TypeConvert import ToUnicode
from ORCA.utils.FileName    import cFileName

import ORCA.vars.Globals

__all__ = ['Var_Concatenate',
           'Var_Decrease',
           'Var_DelArray',
           'Var_Divide',
           'Var_Find',
           'Var_Format',
           'Var_FromVar',
           'Var_GetArray',
           'Var_Hex2Int',
           'Var_HexStringToString',
           'Var_Increase',
           'Var_Int2Hex',
           'Var_Invert',
           'Var_Len',
           'Var_LoadFile',
           'Var_LowerCase',
           'Var_Multiply',
           'Var_Part',
           'Var_Power',
           'Var_Round',
           'Var_StringToHexString',
           'Var_ToVar',
           'Var_Trim',
           'Var_UpperCase',
          ]

def Var_Invert(uVarName):
    """
    Inverts a given variable value.
    Converts the following values
    [0|1]
    [false:true] [False:True] [FALSE:TRUE]
    [off:on][Off:On][OFF:ON]
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue = GetVar(uVarName=uVarName)

    uVarNameOrg = uVarName

    if uValue is not None:
        if uValue == u'0':
            uValue = u'1'
        elif uValue == u'1':
            uValue = u'0'
        elif uValue == u'false':
            uValue = u'true'
        elif uValue == u'true':
            uValue = u'false'
        elif uValue == u'False':
            uValue = u'True'
        elif uValue == u'True':
            uValue = u'False'
        elif uValue == u'FALSE':
            uValue = u'TRUE'
        elif uValue == u'TRUE':
            uValue = u'FALSE'
        elif uValue == u'OFF':
            uValue = u'ON'
        elif uValue == u'ON':
            uValue = u'OFF'
        elif uValue == u'off':
            uValue = u'on'
        elif uValue == u'on':
            uValue = u'off'
        elif uValue == u'Off':
            uValue = u'On'
        elif uValue == u'On':
            uValue = u'Off'
        elif uValue == u'':
            uValue = u'1'
    SetVar(uVarName=uVarName, oVarValue=uValue)

    uVarNameOrg = uVarName
    Logger.debug(u'Var_Invert: [%s] returned [%s]  (stored in [%s])' % (uVarNameOrg, uValue, uVarName))

    return uValue


def Var_NormalizeInt(uVar):
    """
    Internal function to remove ".0" from a converted integer based string

    :rtype: string
    :param string uVar: The variable value for the action
    :return: The changed variable value
    """

    if uVar[-2:] == u'.0':
        return uVar[:-2]
    else:
        return uVar


def Var_Increase(uVarName, uStep='1', uMax=''):
    """
    Increase a given variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uStep: The value to added to the original value, can be a variable itself
    :param string uMax: The maximum value, which can't be exceeded, can be a variable itself, If empty, no limit is used
    :return: The changed variable value
    """

    uValue = u''
    try:
        uValue = GetVar(uVarName=uVarName)
        uValueOrg = uValue

        if uValue == u'':
            uValue = '0'
        uStepToUse = GetVar(uVarName=uStep)
        if uStepToUse == u'':
            uStepToUse = uStep
        uStepToUse = ReplaceVars(uStepToUse)
        uMaxToUse = GetVar(uVarName=uMax)
        if uMaxToUse == u'':
            uMaxToUse = uMax

        fValue = ToFloat(uValue)
        fValue += ToFloat(uStepToUse)
        if not uMaxToUse == u'':
            fMaxToUse = ToFloat(uMaxToUse)
            if fValue > fMaxToUse:
                fValue = fMaxToUse
        uValue = ToUnicode(fValue)
        uValue = Var_NormalizeInt(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
        Logger.debug(u'Var_Increase: [%s] plus [%s] returned [%s]  (stored in [%s])' % (uValueOrg, uStepToUse, uValue, uVarName))
    except Exception as e:
        LogError(u'Var_Increase: Invalid Argument', e)
        return u'Error'

    return uValue


def Var_Decrease(uVarName, uStep, uMin):
    """
    Decrease a given variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uStep: The value to added to the original value, can be a variable itself
    :param string uMin: The minimum value, which can't be deceeded, can be a variable itself, If empty, no limit is used
    :return: The changed variable value
    """

    uValue = u''
    try:
        uValue = GetVar(uVarName=uVarName)
        uValueOrg = uValue
        if uValue == u'':
            uValue = '0'

        uStepToUse = GetVar(uVarName=uStep)
        if uStepToUse == u'':
            uStepToUse = uStep
        uMinToUse = GetVar(uVarName=uMin)
        uMinToUse = ReplaceVars(uMinToUse)
        if uMinToUse == u'':
            uMinToUse = uMin

        fValue = ToFloat(uValue)
        fValue -= ToFloat(uStepToUse)
        if not uMinToUse == u'':
            fMinToUse = ToFloat(uMinToUse)
            if fValue < fMinToUse:
                fValue = fMinToUse
        uValue = ToUnicode(fValue)
        uValue = Var_NormalizeInt(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
        Logger.debug(u'Var_Decrease: [%s] minus [%s] returned [%s]  (stored in [%s])' % (uValueOrg, uStepToUse, uValue, uVarName))
    except Exception as e:
        LogError(u'Var_Decrease: Invalid Argument', e)
        return u'Error'
    return uValue


def Var_Multiply(uVarName, uFactor):
    """
    Multiplies a given variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uFactor: The value to multiply with the original value, can be a variable itself
    :return: The changed variable value
    """

    uValue = u''
    try:
        uValue = GetVar(uVarName=uVarName)
        uValueOrg = uValue

        if uValue == u'':
            return u''

        uFactorToUse = GetVar(uVarName=uFactor)
        if uFactorToUse == u'':
            uFactorToUse = uFactor
        uFactorToUse = ReplaceVars(uFactorToUse)
        fFactor = ToFloat(uFactorToUse)
        fValue = ToFloat(uValue)
        fValue = fValue * fFactor
        uValue = ToUnicode(fValue)
        uValue = Var_NormalizeInt(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
        Logger.debug(u'Var_Multiply: [%s] * [%s] returned [%s]  (stored in [%s])' % (uValueOrg, uFactorToUse, uValue, uVarName))
    except Exception as e:
        LogError(u'Var_Multiply: Invalid Argument', e)
        return u'Error'
    return uValue


def Var_Divide(uVarName, uDivisor):
    """
    Divides a given variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uDivisor: The value to divide the original value with, can be a variable itself
    :return: The changed variable value
    """

    uValue = u''
    try:
        uValue = GetVar(uVarName=uVarName)
        uValueOrg = uValue
        if uValue == u'':
            return u''

        uDivisorToUse = GetVar(uVarName=uDivisor)
        if uDivisorToUse == '':
            uDivisorToUse = uDivisor
        uDivisorToUse = ReplaceVars(uDivisorToUse)
        fDivisor = ToFloat(uDivisorToUse)

        if fDivisor == 0:
            return uValue

        fValue = ToFloat(uValue)
        fValue = fValue / fDivisor
        uValue = ToUnicode(fValue)
        uValue = Var_NormalizeInt(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
        Logger.debug(u'Var_Divide: [%s] / [%s] returned [%s]  (stored in [%s])' % (uValueOrg, uDivisorToUse, uValue, uVarName))
    except Exception as e:
        LogError(u'Var_Divide: Invalid Argument', e)
        return u'Error'
    return uValue


def Var_Power(uVarName, uPower):
    """
    Exponentiate a given variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uPower: The value to exponentiate the original value with, can be a variable itself
    :return: The changed variable value
    """

    uValue = u''
    try:
        uValue = GetVar(uVarName=uVarName)
        uValueOrg = uValue
        if uValue == u'':
            return u''

        uPowerToUse = GetVar(uVarName=uPower)
        if uPowerToUse == u'':
            uPowerToUse = uPower
        uPowerToUse = ReplaceVars(uPowerToUse)
        fPower = ToFloat(uPowerToUse)
        fValue = ToFloat(uValue)
        fValue = fValue ** fPower
        uValue = ToUnicode(fValue)
        uValue = Var_NormalizeInt(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
        Logger.debug(u'Var_Power: [%s] ^ [%s] returned [%s]  (stored in [%s])' % (uValueOrg, uPowerToUse, uValue, uVarName))
    except Exception as e:
        LogError(u'Var_Power: Invalid Argument', e)
        return u'Error'
    return uValue


def Var_UpperCase(uVarName):
    """
    Converts a variable value to uppercase.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue = GetVar(uVarName=uVarName)
    uValue = uValue.upper()
    SetVar(uVarName=uVarName, oVarValue=uValue)
    return uValue


def Var_LowerCase(uVarName):
    """
    Converts a variable value to lowercase.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue = GetVar(uVarName=uVarName)
    uValue = uValue.lower()
    SetVar(uVarName=uVarName, oVarValue=uValue)
    return uValue


def Var_Trim(uVarName):
    """
    Removes trailing a leading spaces from a var value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue = GetVar(uVarName=uVarName)
    uValue = uValue.strip()
    SetVar(uVarName=uVarName, oVarValue=uValue)
    return uValue


def Var_FromVar(uVarName, uContext=u''):
    """
    Pulls the variable value from a variable value which represents a variable name
    eg varname1 = "test"
    varname2 = "varname1"
    FromVar(varname2) returns "test"

    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the variable, from where the value is pulled
    :param string uContext: The context for the variable. Internally the context will be added as a prefix to the variable name
    :return: The changed variable value
    """

    uValue = ReplaceVars(GetVar(uVarName=uVarName, uContext=uContext))
    uValue2 = ReplaceVars(GetVar(uVarName=uValue,uContext=uContext))
    if uValue2 != u'':
        uValue = uValue2
    SetVar(uVarName=uVarName, oVarValue=uValue,uContext=uContext)
    return uValue


def Var_ToVar(uVarName, uNewVarName):
    """
    Sets a variable value to a var name without variable translation
    eg varname1 = "test"
    varname2 = "varname1"
    ToVar("varname2","varname1") returns "varname1"

    uNewVarName will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uNewVarName: The new variable value
    :return: uNewVarName
    """

    SetVarWithOutVarTranslation(uNewVarName, uVarName, "")
    return uNewVarName


def Var_Round(uVarName, uPos):
    """
    Rounds a var value to the given round position.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)
    Example: Round(1.81,0) return 2. Round(1.81,1) returns 1.80

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uPos: The round position
    :return: The changed variable value
    """

    uValue = GetVar(uVarName=uVarName)

    try:
        if uValue == u'':
            return u''
        uPosToUse = GetVar(uVarName=uPos)
        if uPosToUse == u'':
            uPosToUse = uPos
        iPos = int(uPos)
        uValue = ToUnicode(Round(ToFloat(uValue), iPos))
        SetVar(uVarName=uVarName, oVarValue=uValue)

    except Exception as e:
        LogError(u'Var_Round: Invalid Argument [' + uVarName + u'=' + uValue + u']:', e)
        return u'Error'

    return uValue


def Var_Concatenate(uVarName, uAddVar):
    """
    Adds a string to a variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uAddVar: The string to add to the var value, can be a variable itself
    :return: The changed variable value
    """

    uValue = GetVar(uVarName=uVarName)
    uValueAdd = GetVar(uVarName=uAddVar)
    if uValueAdd == u'':
        uValueAdd = uAddVar
    uValue += uValueAdd
    SetVar(uVarName=uVarName, oVarValue=uValue)
    return uValue


def Var_Part(uVarName, uStart, uEnd):
    """
    Extracts a part of a variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uStart: The start position within the var value
    :param string uEnd: The end position within the var value
    :return: The changed variable value
    """

    uValue = u''
    try:
        uValue = GetVar(uVarName=uVarName)
        if uValue == u'':
            return u''
        if not uStart == '':
            if not uEnd == '':
                uValue = uValue[int(uStart):int(uEnd)]
            else:
                uValue = uValue[int(uStart):]
        else:
            uValue = uValue[:int(uEnd)]
        SetVar(uVarName=uVarName, oVarValue=uValue)
    except Exception as e:
        LogError('Var_Part: Invalid Argument', e)
        return u'Error'
    return uValue


def Var_Len(uVarName, uDestVar):
    """
    Returns the length of a variable value.
    The changed variable value will be returned and stored in the destination var (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uDestVar: The destination var for the var value length
    :return: The length of the variable value
    """

    uValue = GetVar(uVarName=uVarName)
    uValue = ToUnicode(len(uValue))
    SetVar(uVarName=uDestVar, oVarValue=uValue)
    return uValue


def Var_StringToHexString(uVarName):
    """
    Converts a var value to a hex string.
    The changed variable value will be returned and stored in the destination var (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue = GetVar(uVarName=uVarName)
    uValue = uValue.encode("hex")
    SetVar(uVarName=uVarName, oVarValue=uValue)
    return uValue


def Var_HexStringToString(uVarName):
    """
    Converts a var value which represents a hex string to a string which represents the number.
    The changed variable value will be returned and stored in the destination var (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue = GetVar(uVarName=uVarName)
    uValue = uValue.decode("hex")
    SetVar(uVarName=uVarName, oVarValue=uValue)
    return uValue


def Var_Find(uVarName, uFindVar, uDestVar):
    """
    Finds the posiion of a substring in a variable value.
    The changed variable value will be returned and stored in the destination var (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uFindVar: The string to search for
    :param string uDestVar: The name of the variable for the result (the Position) If not found, '-1' will be returned
    :return: The position of the substring
    """

    uValue = GetVar(uVarName=uVarName)
    uValue = uVarName
    if uValue == u'':
        uValue = uVarName
    uValue = ReplaceVars(uValue)

    uFindVar = ReplaceVars(uFindVar)
    iPos = uValue.find(uFindVar)
    uResult = ToUnicode(iPos)
    SetVar(uVarName=uDestVar, oVarValue=uResult)
    Logger.debug(u'Var_Find: [%s] in [%s] returned [%s]  (stored in [%s])' % (uFindVar, uValue, uResult, uDestVar))
    return uResult


def Var_GetArray(uVarName, iLevel):
    """
    Returns an array of vars form the uservars, if the VarName is indexed

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param int iLevel: The array level, which means the nested level of square brackets '[xx]'
    :return: An array of vars for the selected level
    """

    aRet = []
    iPosStart = Find_nth_Character(uVarName, "[", iLevel)
    if iPosStart > 0:
        uRootVarName = uVarName[:iPosStart + 1]
        for uName in ORCA.vars.Globals.dUserVars:
            if uName.startswith(uRootVarName):
                aRet.append(uName)
        aRet = sorted(aRet)
    return aRet


def Var_DelArray(uVarName):
    """
    Deletes an var Array, the var name needs to end with []. No Triggers will be raised

    :rtype: None
    :param string uVarName: The array name
    """

    uKeyName = uVarName[:-1]
    aDelKeys = []
    for uKey, uValue in ORCA.vars.Globals.dUserVars.items():
        if uKey.startswith(uKeyName):
            aDelKeys.append(uKey)
    for uKey in aDelKeys:
        del ORCA.vars.Globals.dUserVars[uKey]

def Var_Hex2Int(uVarName):
    """
    Converts a Variable which represents an hex value to a string of an Int value
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue = u''
    try:
        uValue = GetVar(uVarName=uVarName)

        if uValue == '':
            return u'0'
        if uValue == 'Error':
            return u'0'

        if uValue.lower().startswith('0x'):
            iValue = int(uValue, 0)
        else:
            iValue = int(uValue, 16)

        uValue = ToUnicode(iValue)
        uValue = Var_NormalizeInt(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
    except Exception as e:
        LogError(u'Var_Hex2Int: Invalid Argument (%s):' % uValue, e)
        return u'0'
    return uValue


def Var_Int2Hex(uVarName, uFormat='{0:0>2X}'):
    """
    Converts a Variable which represents an int value to a string of a hex value
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uFormat: The format to use for the conversion
    :return: The changed variable value
    """

    uValue = u''
    try:
        uValue = GetVar(uVarName=uVarName)

        if uValue == '':
            return u'0'
        if uValue == 'Error':
            return u'0'

        uValue = uFormat.format(int(uValue))
        uValue = ToUnicode(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
    except Exception as e:
        LogError(u'Var_Int2Hex: Invalid Argument (%s):' % uValue, e)
        return u'0'
    return uValue


def Var_LoadFile(uVarName, uFileName):
    """
    Loads the content a file into a var
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uFileName: The filename for the content to load
    :return: The changed variable value
    """

    try:
        oFileName = cFileName('').ImportFullPath(uFileName)
        uValue = LoadFile(oFileName)
        SetVar(uVarName=uVarName, oVarValue=uValue)
    except Exception as e:
        LogError(u'Var_LoadFile: Error Loading File Content (%s:%s)' % (uVarName, oFileName.string), e)
        return u''
    return uValue


def Var_Format(uVarName, uFormat):
    """
    Formats a variable content to a given format
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :rtype: string
    :param string uVarName: The variable name for the action, from where the value is pulled
    :param string uFormat: The format to use (python syntax)
    :return: The changed variable value
    """

    try:
        uValue = GetVar(uVarName=uVarName)
        if uValue is None:
            return u''
        uFormatToUse = ORCA.vars.Globals.dUserVars.get(uFormat)
        if uFormatToUse is None:
            uFormatToUse = uFormat

        if uFormatToUse.startswith('(int)'):
            uFormatToUse = uFormatToUse[5:]
            uValue = int(ToFloat(uValue))
        elif uFormatToUse.startswith('(float)'):
            uFormatToUse = uFormatToUse[7:]
            uValue = ToFloat(uValue)

        uValue = uFormatToUse.format(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
    except Exception as e:
        LogError(u'Var_Format: Invalid Argument', e)
        return u''
    return uValue
