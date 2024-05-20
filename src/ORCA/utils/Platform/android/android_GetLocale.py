# -*- coding: utf-8 -*-

"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2024  Carsten Thielepape
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
# noinspection PyUnresolvedReferences
from jnius                  import autoclass

def GetLocale() -> str:
    """ gets the locale / language from the system """
    uCurrent:str = 'English'
    uOurlocale:str = 'en'

    try:
        Logger.debug('Attempting to get default locale from Java...')
        JavaUtilLocale = autoclass('java.util.Locale')
        jlocale = JavaUtilLocale
        uOurlocale = jlocale.getDefault().getLanguage()
    except Exception:
        Logger.debug('Unable to get locale from Java...')
    Logger.debug('Javalocale:'+uOurlocale)

    if uOurlocale == 'de':
        uCurrent='German'
    return uCurrent
