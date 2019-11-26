from typing import Dict
from kivy.logger import Logger

import ORCA.vars.Globals

__all__ = ['DumpVars',
           'DumpDefinitionVars'
          ]

def DumpDefinitionVars(dArray:Dict[str,str], uFilter:str="") -> None:
    """
    Dumps definition vars as debug messages

    :param Dict dArray: Dictonray of definition vars
    :param str uFilter: A filter to just return vars, which CONTAINS the filter string
    """
    Logger.debug('Dumping Definition Vars')

    uVarIdx:str
    uTmp:str

    for uVarIdx in sorted(dArray):
        uTmp = dArray[uVarIdx]
        if uFilter == "":
            Logger.debug(u'DumpVar: DefVar:' + uVarIdx + '=' + uTmp)
        else:
            if uFilter in uVarIdx:
                Logger.debug(u'DumpVar: DefVar:' + uVarIdx + '=' + uTmp)


def DumpVars(uFilter:str="") -> None:
    """
    Dumps user vars as debug messages
    :param str uFilter: A filter to just return vars, which CONTAINS the filter string
    """

    uTmp:str

    Logger.debug('Dumping Vars')
    for uVarIdx in sorted(ORCA.vars.Globals.dUserVars):
        uTmp = u"Internal Object"
        if isinstance(ORCA.vars.Globals.dUserVars[uVarIdx], str):
            uTmp = ORCA.vars.Globals.dUserVars[uVarIdx]
        if uFilter == "":
            Logger.debug(u'DumpVar: Var:' + uVarIdx + '=' + uTmp)
        else:
            if uFilter in uVarIdx:
                Logger.debug(u'DumpVar: Var:' + uVarIdx + '=' + uTmp)
