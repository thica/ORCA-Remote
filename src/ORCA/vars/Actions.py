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
           'Var_GetArrayEx',
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

def Var_Invert(uVarName:str) -> str:
    """
    Inverts a given variable value.
    Converts the following values
    [0|1]
    [false:true] [False:True] [FALSE:TRUE]
    [off:on][Off:On][OFF:ON]
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue:str = GetVar(uVarName=uVarName)
    uValueOrg:str = uValue

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

    Logger.debug(u'Var_Invert: [%s] returned [%s] (stored in %s)' % (uValueOrg, uValue,uVarName))

    return uValue


def Var_NormalizeInt(uVar:str) -> str:
    """
    Internal function to remove ".0" from a converted integer based string

    :param str uVar: The variable value for the action
    :return: The changed variable value
    """

    if uVar[-2:] == u'.0':
        return uVar[:-2]
    else:
        return uVar


def Var_Increase(uVarName:str, uStep:str='1', uMax:str='') -> str:
    """
    Increase a given variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uStep:    The value to added to the original value, can be a variable itself
    :param str uMax:     The maximum value, which can't be exceeded, can be a variable itself, If empty, no limit is used
    :return: The changed variable value
    """

    try:
        uValue:str    = GetVar(uVarName=uVarName)
        uValueOrg:str = uValue

        if uValue == u'':
            uValue = '0'
        uStepToUse:str = GetVar(uVarName=uStep)
        if uStepToUse == u'':
            uStepToUse = uStep
        uStepToUse = ReplaceVars(uStepToUse)
        uMaxToUse:str = GetVar(uVarName=uMax)
        if uMaxToUse == u'':
            uMaxToUse = uMax

        fValue:float = ToFloat(uValue)
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
        LogError(uMsg=u'Var_Increase: Invalid Argument', oException=e)
        return u'Error'



def Var_Decrease(uVarName:str, uStep:str, uMin:str) -> str:
    """
    Decrease a given variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uStep: The value to added to the original value, can be a variable itself
    :param str uMin: The minimum value, which can't be deceeded, can be a variable itself, If empty, no limit is used
    :return: The changed variable value
    """

    try:
        uValue:str      = GetVar(uVarName=uVarName)
        uValueOrg:str   = uValue
        if uValue == u'':
            uValue = '0'

        uStepToUse:str = GetVar(uVarName=uStep)
        if uStepToUse == u'':
            uStepToUse = uStep
        uMinToUse:str = GetVar(uVarName=uMin)
        uMinToUse = ReplaceVars(uMinToUse)
        if uMinToUse == u'':
            uMinToUse = uMin

        fValue:float = ToFloat(uValue)
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
        LogError(uMsg=u'Var_Decrease: Invalid Argument', oException=e)
        return u'Error'


def Var_Multiply(uVarName:str, uFactor:str) ->str:
    """
    Multiplies a given variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uFactor: The value to multiply with the original value, can be a variable itself
    :return: The changed variable value
    """

    try:
        uValue:str    = GetVar(uVarName=uVarName)
        uValueOrg:str = uValue

        if uValue == u'':
            return u''

        uFactorToUse:str = GetVar(uVarName=uFactor)
        if uFactorToUse == u'':
            uFactorToUse = uFactor
        uFactorToUse = ReplaceVars(uFactorToUse)
        fFactor:float = ToFloat(uFactorToUse)
        fValue:float = ToFloat(uValue)
        fValue = fValue * fFactor
        uValue = ToUnicode(fValue)
        uValue = Var_NormalizeInt(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
        Logger.debug(u'Var_Multiply: [%s] * [%s] returned [%s]  (stored in [%s])' % (uValueOrg, uFactorToUse, uValue, uVarName))
    except Exception as e:
        LogError(uMsg=u'Var_Multiply: Invalid Argument', oException=e)
        return u'Error'


def Var_Divide(uVarName:str, uDivisor:str) -> str:
    """
    Divides a given variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uDivisor: The value to divide the original value with, can be a variable itself
    :return: The changed variable value
    """

    try:
        uValue:str      = GetVar(uVarName=uVarName)
        uValueOrg:str   = uValue
        if uValue == u'':
            return u''

        uDivisorToUse:str = GetVar(uVarName=uDivisor)
        if uDivisorToUse == '':
            uDivisorToUse = uDivisor
        uDivisorToUse = ReplaceVars(uDivisorToUse)
        fDivisor:float = ToFloat(uDivisorToUse)

        if fDivisor == 0:
            return uValue

        fValue:float = ToFloat(uValue)
        fValue = fValue / fDivisor
        uValue = ToUnicode(fValue)
        uValue = Var_NormalizeInt(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
        Logger.debug(u'Var_Divide: [%s] / [%s] returned [%s]  (stored in [%s])' % (uValueOrg, uDivisorToUse, uValue, uVarName))
    except Exception as e:
        LogError(uMsg=u'Var_Divide: Invalid Argument', oException=e)
        return u'Error'
    return uValue


def Var_Power(uVarName:str, uPower:str) -> str:
    """
    Exponentiate a given variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uPower: The value to exponentiate the original value with, can be a variable itself
    :return: The changed variable value
    """

    try:
        uValue:str = GetVar(uVarName=uVarName)
        uValueOrg:str = uValue
        if uValue == u'':
            return u''

        uPowerToUse:str = GetVar(uVarName=uPower)
        if uPowerToUse == u'':
            uPowerToUse = uPower
        uPowerToUse = ReplaceVars(uPowerToUse)
        fPower:float = ToFloat(uPowerToUse)
        fValue:float = ToFloat(uValue)
        fValue = fValue ** fPower
        uValue = ToUnicode(fValue)
        uValue = Var_NormalizeInt(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
        Logger.debug(u'Var_Power: [%s] ^ [%s] returned [%s]  (stored in [%s])' % (uValueOrg, uPowerToUse, uValue, uVarName))
    except Exception as e:
        LogError(uMsg=u'Var_Power: Invalid Argument', oException=e)
        return u'Error'


def Var_UpperCase(uVarName:str) -> str:
    """
    Converts a variable value to uppercase.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue:str = GetVar(uVarName=uVarName).upper()
    SetVar(uVarName=uVarName, oVarValue=uValue)
    return uValue


def Var_LowerCase(uVarName:str) -> str:
    """
    Converts a variable value to lowercase.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param stri uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue:str = GetVar(uVarName=uVarName).lower()
    SetVar(uVarName=uVarName, oVarValue=uValue)
    return uValue


def Var_Trim(uVarName:str) -> str:
    """
    Removes trailing a leading spaces from a var value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue:str = GetVar(uVarName=uVarName).strip()
    SetVar(uVarName=uVarName, oVarValue=uValue)
    return uValue


def Var_FromVar(uVarName:str, uContext:str=u'') -> str:
    """
    Pulls the variable value from a variable value which represents a variable name
    eg varname1 = "test"
    varname2 = "varname1"
    FromVar(varname2) returns "test"

    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the variable, from where the value is pulled
    :param str uContext: The context for the variable. Internally the context will be added as a prefix to the variable name
    :return: The changed variable value
    """

    uValue:str  = ReplaceVars(GetVar(uVarName=uVarName, uContext=uContext))
    uValue2:str = ReplaceVars(GetVar(uVarName=uValue,uContext=uContext))
    if uValue2 != u'':
        uValue = uValue2
    SetVar(uVarName=uVarName, oVarValue=uValue,uContext=uContext)
    return uValue


def Var_ToVar(uVarName:str, uNewVarName:str) -> str:
    """
    Sets a variable value to a var name without variable translation
    eg varname1 = "test"
    varname2 = "varname1"
    ToVar("varname2","varname1") returns "varname1"

    uNewVarName will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uNewVarName: The new variable value
    :return: uNewVarName
    """

    SetVarWithOutVarTranslation(uNewVarName, uVarName, "")
    return uNewVarName


def Var_Round(uVarName:str, uPos:str) -> str:
    """
    Rounds a var value to the given round position.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)
    Example: Round(1.81,0) return 2. Round(1.81,1) returns 1.80

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uPos: The round position
    :return: The changed variable value
    """

    uValue: str = GetVar(uVarName=uVarName)

    try:
        if uValue == u'':
            return u''

        uPosToUse:str = GetVar(uVarName=uPos)
        if uPosToUse == u'':
            uPosToUse = uPos
        iPos:int = int(uPosToUse)
        uValue = ToUnicode(Round(ToFloat(uValue), iPos))
        SetVar(uVarName=uVarName, oVarValue=uValue)
        return uValue

    except Exception as e:
        LogError(uMsg=u'Var_Round: Invalid Argument [' + uVarName + u'=' + uValue + u']:', oException=e)
        return u'Error'


def Var_Concatenate(uVarName:str, uAddVar:str) -> str:
    """
    Adds a string to a variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uAddVar: The string to add to the var value, can be a variable itself
    :return: The changed variable value
    """

    uValue:str = GetVar(uVarName=uVarName)
    uValueAdd:str = GetVar(uVarName=uAddVar)
    if uValueAdd == u'':
        uValueAdd = uAddVar
    uValue += uValueAdd
    SetVar(uVarName=uVarName, oVarValue=uValue)
    return uValue


def Var_Part(uVarName:str, uStart:str, uEnd:str) -> str:
    """
    Extracts a part of a variable value.
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uStart: The start position within the var value
    :param str uEnd: The end position within the var value
    :return: The changed variable value
    """

    try:
        uValue:str = GetVar(uVarName=uVarName)
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
        LogError(uMsg='Var_Part: Invalid Argument', oException=e)
        return u'Error'


def Var_Len(uVarName: str, uDestVar:str) -> str:
    """
    Returns the length of a variable value.
    The changed variable value will be returned and stored in the destination var (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uDestVar: The destination var for the var value length
    :return: The length of the variable value
    """

    uValue = GetVar(uVarName=uVarName)
    uValue = ToUnicode(len(uValue))
    SetVar(uVarName=uDestVar, oVarValue=uValue)
    return uValue


def Var_StringToHexString(uVarName:str) -> str:
    """
    Converts a var value to a hex string.
    The changed variable value will be returned and stored in the destination var (Triggers raised if set)
    eg: "paul" to "7061756c"

    :param str uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """
    uValue = GetVar(uVarName=uVarName)
    try:
        uValue = ToUnicode(uValue.encode("utf-8").hex())
        SetVar(uVarName=uVarName, oVarValue=uValue)
        return uValue
    except Exception as e:
        LogError(uMsg=u'Var_StringToHexString: Invalid Argument [' + uVarName + u'=' + uValue + u']:', oException=e)
        return u'Error'


def Var_HexStringToString(uVarName:str) -> str:
    """
    Converts a var value which represents a hex string to a string which represents the ASCII.
    The changed variable value will be returned and stored in the destination var (Triggers raised if set)
    eg: "7061756c" to "paul"

    :param str uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """
    uValue: str = GetVar(uVarName=uVarName)
    try:
        uValue=ToUnicode(bytearray.fromhex(uValue).decode())
        SetVar(uVarName=uVarName, oVarValue=uValue)
        return uValue
    except Exception as e:
        LogError(uMsg=u'Var_HexStringToString: Invalid Argument [' + uVarName + u'=' + uValue + u']:', oException=e)
        return u'Error'


def Var_Find(uVarName:str, uFindVar:str, uDestVar:str) -> str:
    """
    Finds the posiion of a substring in a variable value.
    The changed variable value will be returned and stored in the destination var (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uFindVar: The string to search for
    :param str uDestVar: The name of the variable for the result (the Position) If not found, '-1' will be returned
    :return: The position of the substring
    """

    uValue:str = GetVar(uVarName=uVarName)
    if uValue == u'':
        uValue = uVarName
    uValue = ReplaceVars(uValue)

    uFindVar:str = ReplaceVars(uFindVar)
    iPos:int = uValue.find(uFindVar)
    uResult:str = ToUnicode(iPos)
    SetVar(uVarName=uDestVar, oVarValue=uResult)
    Logger.debug(u'Var_Find: [%s] in [%s] returned [%s]  (stored in [%s])' % (uFindVar, uValue, uResult, uDestVar))
    return uResult


def Var_GetArray(uVarName:str, iLevel:int, bSort:bool = True) -> List[str]:
    """
    Returns an array of vars from the uservars, if the VarName is indexed

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param int iLevel: The array level, which means the nested level of square brackets '[xx]'
    :param bool bSort: Flag, if the array should be sorted
    :return: An array of vars for the selected level
    """

    aRet:List[str] = []
    iPosStart:int = Find_nth_Character(uVarName, "[", iLevel)
    if iPosStart > 0:
        uRootVarName:str = uVarName[:iPosStart + 1]
        for uName in ORCA.vars.Globals.dUserVars:
            if uName.startswith(uRootVarName) and len(uName)>len(uRootVarName) and uName[len(uRootVarName)]!="]":
                aRet.append(uName)
        if bSort:
            aRet = sorted(aRet)
    return aRet

def Var_GetArrayEx(uVarName:str, iLevel:int, bSort:bool = True) -> List[Tuple[str,str]]:
    """
    Returns an array of Tuple vars from the uservars, if the VarName is indexed

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param int iLevel: The array level, which means the nested level of square brackets '[xx]'
    :param bool bSort: Flag, if the array should be sorted
    :return: An array of tupleds (varname, varindex) for the selected level, where index is the varindex in the brackets
    """

    aRet:List[Tuple[str,str]] = []
    iPosStart:int = Find_nth_Character(uVarName, "[", iLevel)
    if iPosStart > 0:
        uRootVarName:str = uVarName[:iPosStart + 1]
        for uName in ORCA.vars.Globals.dUserVars:
            if uName.startswith(uRootVarName) and len(uName)>len(uRootVarName) and uName[len(uRootVarName)]!="]":
                uIndex=uName[iPosStart+1:uName.find("]",iPosStart+1)]
                aRet.append((uName,uIndex))
        if bSort:
            aRet = sorted(aRet)
    return aRet


def Var_DelArray(uVarName:str) -> None:
    """
    Deletes an var Array, the var name needs to end with []. No Triggers will be raised

    :param str uVarName: The array name
    """

    uKeyName:str = uVarName[:-1]
    aDelKeys:List[str] = []
    for uKey, uValue in ORCA.vars.Globals.dUserVars.items():
        if uKey.startswith(uKeyName):
            aDelKeys.append(uKey)
    for uKey in aDelKeys:
        del ORCA.vars.Globals.dUserVars[uKey]

def Var_Hex2Int(uVarName:str) -> str:
    """
    Converts a Variable which represents an hex value to a string of an Int value
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :return: The changed variable value
    """

    uValue: str = GetVar(uVarName=uVarName)
    try:
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
        LogError(uMsg=u'Var_Hex2Int: Invalid Argument (%s):' % uValue, oException=e)
        return u'0'


def Var_Int2Hex(uVarName:str, uFormat:str='{0:0>2X}') -> str:
    """
    Converts a Variable which represents an int value to a string of a hex value
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uFormat: The format to use for the conversion
    :return: The changed variable value
    """

    uValue: str = GetVar(uVarName=uVarName)
    try:

        if uValue == '':
            return u'0'
        if uValue == 'Error':
            return u'0'

        uValue = uFormat.format(int(uValue))
        uValue = ToUnicode(uValue)
        SetVar(uVarName=uVarName, oVarValue=uValue)
    except Exception as e:
        LogError(uMsg=u'Var_Int2Hex: Invalid Argument (%s):' % uValue, oException=e)
        return u'0'


def Var_LoadFile(uVarName:str, uFileName:str) -> str:
    """
    Loads the content a file into a var
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uFileName: The filename for the content to load
    :return: The changed variable value
    """

    try:
        oFileName:cFileName = cFileName('').ImportFullPath(uFileName)
        uValue:str = LoadFile(oFileName)
        SetVar(uVarName=uVarName, oVarValue=uValue)
        return uValue
    except Exception as e:
        LogError(uMsg=u'Var_LoadFile: Error Loading File Content (%s:%s)' % (uVarName, uFileName), oException=e)
        return u''


def Var_Format(uVarName:str, uFormat:str):
    """
    Formats a variable content to a given format
    The changed variable value will be return and stored in the user vars (Triggers raised if set)

    :param str uVarName: The variable name for the action, from where the value is pulled
    :param str uFormat: The format to use (python syntax)
    :return: The changed variable value
    """

    try:
        uValue:str = GetVar(uVarName=uVarName)
        if uValue is None:
            return u''
        uFormatToUse:str = ORCA.vars.Globals.dUserVars.get(uFormat)
        if uFormatToUse is None:
            uFormatToUse = uFormat

        if uFormatToUse.startswith('(int)'):
            uFormatToUse = uFormatToUse[5:]
            uValue = uFormatToUse.format(int(ToFloat(uValue)))
        elif uFormatToUse.startswith('(float)'):
            uFormatToUse = uFormatToUse[7:]
            uValue = uFormatToUse.format(ToFloat(uValue))

        SetVar(uVarName=uVarName, oVarValue=uValue)
    except Exception as e:
        LogError(uMsg=u'Var_Format: Invalid Argument', oException=e)
        return u''
