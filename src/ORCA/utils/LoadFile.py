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
from ORCA.utils.FileName    import cFileName

import codecs

__all__ = ['LoadFile']


def LoadFile(oFileName):
    """ returns a content of file as string (unicode on Py3)
    :rtype: string
    :param cFileName oFileName: the FileName to load
    :return: The File Content as string
    """

    if isinstance(oFileName,str):
        Logger.warning("Please pass a cFileName to LoadFile:"+oFileName)
        oFileName=cFileName('').ImportFullPath(oFileName)


    try:
        f = None
        try:
            #should work for all xml files
            f= codecs.open(oFileName.string, 'r', encoding='utf-8')
            read_data = f.read()
        except Exception:
            if f is not None:
                f.close()
            # should work for common other files
            try:
                f = codecs.open(oFileName.string, 'r', encoding='latin1')
                read_data = f.read()
            except Exception:
                #fallback
                if f is not None:
                    f.close()
                f = codecs.open(oFileName.string, 'r', encoding='utf-8', errors='ignore')
                read_data = f.read()
        f.close()
        return read_data
    except Exception as e:
        uMsg=u'can\'t load file [%s] : %s  ' % (oFileName.string,e)
        Logger.error (uMsg)
        return ''


