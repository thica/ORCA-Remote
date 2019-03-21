from kivy.logger import Logger
from kivy.compat import string_types

import ORCA.vars.Globals

__all__ = ['DumpVars',
           'DumpDefinitionVars'
          ]


def DumpDefinitionVars(dArray, uFilter=""):
    """
    Dumps definition vars as debug messages

    :rtype: None
    :param dict dArray: Dictonray of definition vars
    :param uFilter: A filter to just return vars, which CONTAINS the filter string
    """
    Logger.debug('Dumping Definition Vars')

    for uVarIdx in sorted(dArray):
        oTmp = dArray[uVarIdx]

        if uFilter == "":
            Logger.debug(u'DumpVar: DefVar:' + uVarIdx + '=' + oTmp)
        else:
            if uFilter in uVarIdx:
                Logger.debug(u'DumpVar: DefVar:' + uVarIdx + '=' + oTmp)


def DumpVars(uFilter=""):
    """
    Dumps user vars as debug messages

    :rtype: None
    :param uFilter: A filter to just return vars, which CONTAINS the filter string
    """

    Logger.debug('Dumping Vars')
    for uVarIdx in sorted(ORCA.vars.Globals.dUserVars):
        oTmp = u"Internal Object"
        if isinstance(ORCA.vars.Globals.dUserVars[uVarIdx], string_types):
            oTmp = ORCA.vars.Globals.dUserVars[uVarIdx]

        if uFilter == "":
            Logger.debug(u'DumpVar: Var:' + uVarIdx + '=' + oTmp)
        else:
            if uFilter in uVarIdx:
                Logger.debug(u'DumpVar: Var:' + uVarIdx + '=' + oTmp)
