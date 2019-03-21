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


'''

CTH:

Code taken from Kivy garden and adjusted to match ORCA requierements

FileBrowser
===========

The :class:`FileBrowser` widget is an advanced file browser. You use it
similarly to FileChooser usage.

It provides a shortcut bar with links to special and system directories.
When touching next to a shortcut in the links bar, it'll expand and show
all the directories within that directory. It also facilitates specifying
custom paths to be added to the shortcuts list.

It provides a icon and list view to choose files from. And it also accepts
filter and filename inputs.

To create a FileBrowser which prints the currently selected file as well as
the current text in the filename field when 'Select' is pressed, with
a shortcut to the Documents directory added to the favorites bar::

    ffrom kivy.app import App
    from os.path import sep, expanduser, isdir, dirname

    class TestApp(App):

        def build(self):
            if platform == 'win':
                user_path = dirname(expanduser('~')) + sep + 'Documents'
            else:
                user_path = expanduser('~') + sep + 'Documents'
            browser = FileBrowser(select_string='Select',
                                  favorites=[(user_path, 'Documents')])
            browser.bind(
                        on_success=self._fbrowser_success,
                        on_canceled=self._fbrowser_canceled)
            return browser

        def _fbrowser_canceled(self, instance):
            print 'cancelled, Close self.'

        def _fbrowser_success(self, instance):
            print instance.selection

    TestApp().run()

:Events:
    `on_canceled`:
        Fired when the `Cancel` buttons `on_release` event is called.

    `on_success`:
        Fired when the `Select` buttons `on_release` event is called.

    `on_success`:
        Fired when a file has been selected with a double-tap.

.. image:: _static/filebrowser.png
    :align: right
'''

import string
from os.path import sep, dirname, expanduser, isdir
from os import walk
from functools import partial


from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeViewLabel, TreeView
from kivy.uix.filechooser import FileChooserIconView as IconView
from kivy.properties import (ObjectProperty, StringProperty, OptionProperty, ListProperty, BooleanProperty)
from kivy.lang import Builder
from kivy.utils import platform as core_platform
from kivy.clock import Clock
from kivy.uix.widget import Widget

__all__ = ('FileBrowser', )
__version__ = '1.1'


platform = core_platform

if platform == 'win':
    from ctypes import windll, create_unicode_buffer

class SettingSpacer(Widget):
    """ Internal class, not documented."""
    pass

def get_drives():
    """ returns a list of all available drives """
    drives = []
    if platform == 'win':
        bitmask = windll.kernel32.GetLogicalDrives()
        GetVolumeInformationW = windll.kernel32.GetVolumeInformationW
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                name = create_unicode_buffer(64)
                # get name of the drive
                drive = letter + u':'
                res = GetVolumeInformationW(drive + sep, name, 64, None,None, None, None, 0)
                drives.append((drive, name.value))
            bitmask >>= 1
    elif platform == 'linux':
        drives.append((sep, sep))
        drives.append((expanduser(u'~'), '~/'))
        places = (sep + u'mnt', sep + u'media')
        for place in places:
            if isdir(place):
                for directory in walk(place).next()[1]:
                    drives.append((place + sep + directory, directory))
    elif platform == 'macosx' or platform == 'ios':
        drives.append((expanduser(u'~'), '~/'))
        vol = sep + u'Volume'
        if isdir(vol):
            for drive in walk(vol).next()[1]:
                drives.append((vol + sep + drive, drive))
    return drives

class FileBrowserIconView(IconView):
    """ pass """
    pass

Builder.load_string('''
#:kivy 1.2.0
#:import metrics kivy.metrics
#:import abspath os.path.abspath

<TreeLabel>:
    on_touch_down:
        self.parent.browser.path = self.path if\
        self.collide_point(*args[1].pos) and self.path else\
        self.parent.browser.path
    on_is_open: self.is_open and self.parent.trigger_populate(self)

<FileBrowser>:
    orientation: 'vertical'
    spacing: 5
    padding: [6, 6, 6, 6]
    select_state: select_button.state
    cancel_state: cancel_button.state
    filename: file_text.text
    on_favorites: link_tree.reload_favs(self.favorites)
    BoxLayout:
        orientation: 'horizontal'
        spacing: 5
        id: box_left
        Splitter:
            sizable_from: 'right'
            min_size: '153sp'
            size_hint: (.2, 1)
            id: splitter
            ScrollView:
                LinkTree:
                    id: link_tree
                    browser: list_view
                    size_hint_y: None
                    height: self.minimum_height
        BoxLayout:
            id: box_right
            size_hint_x: .8
            orientation: 'vertical'
            Label:
                size_hint_y: None
                height: '22dp'
                text_size: self.size
                padding_x: '10dp'
                text: abspath(root.path)
                valign: 'middle'
            ScreenManager:
                id:sm
                Screen:
                    id: page_listview
                    name: 'list_view'
                    FileChooserListView:
                        id: list_view
                        path: root.path
                        filters: root.filters
                        filter_dirs: root.filter_dirs
                        show_hidden: root.show_hidden
                        multiselect: root.multiselect
                        dirselect: root.dirselect
                        rootpath: root.rootpath
                        on_submit: root.dispatch('on_submit')
                Screen:
                    id: page_listview
                    name: 'icon_view'
                    FileBrowserIconView:
                        id: icon_view
                        path: root.path
                        filters: root.filters
                        filter_dirs: root.filter_dirs
                        show_hidden: root.show_hidden
                        multiselect: root.multiselect
                        dirselect: root.dirselect
                        rootpath: root.rootpath
                        on_submit: root.dispatch('on_submit')

    SettingSpacer:
        id: spacer1
        height: 0

    BoxLayout:
        id: box_text
        size_hint: (1, None)
        height: (file_text.line_height * 4) if (root.show_fileinput and root.show_filterinput) else (file_text.line_height * 2)
        spacing: '5dp'
        orientation: 'vertical'
        TextInput:
            id: file_text
            text: (root.selection and (root._shorten_filenames(\
            root.selection) if root.multiselect else root.selection[0])) or ''
            hint_text: 'Filename'
            multiline: False
        TextInput:
            id: filt_text
            hint_text: '*.*'
            on_text_validate:
                root.filters = self.text.split(',') if self.text else []
            multiline: False
            text: ','.join(root.filters)

    SettingSpacer:
        id: spacer2
        height: 0

    BoxLayout:
        size_hint: (1, None)
        height: metrics.dp(40)
        spacing: '2dp'
        Button:
            id: select_button
            text: root.select_string
            on_release: root.dispatch('on_success')
        Button:
            id: cancel_button
            text: root.cancel_string
            on_release: root.dispatch('on_canceled')
        Button:
            id: showlistview_button
            text: root.listview_string
            on_release: 
                link_tree.browser = list_view
                sm.current='list_view' 
        Button:
            id: showiconview_button
            text: root.iconview_string
            on_release: 
                link_tree.browser = icon_view
                sm.current='icon_view' 

''')


class TreeLabel(TreeViewLabel):
    """Full path to the location this node points to.
    :class:`~kivy.properties.StringProperty`, defaults to ''
    """
    path = StringProperty('')

class LinkTree(TreeView):
    """ link to the favorites section of link bar """
    _favs = ObjectProperty(None)
    _computer_node = None

    favorites_string = StringProperty('')
    libraries_string = StringProperty('')
    computer_string = StringProperty('')

    def fill_tree(self, fav_list):
        if platform == 'win':
            user_path = expanduser(u'~')
            if not isdir(user_path + sep + 'Desktop'):
                user_path = dirname(user_path) + sep
            else:
                user_path += sep
        else:
            user_path = expanduser(u'~') + sep
        self._favs = self.add_node(TreeLabel(text=self.favorites_string, is_open=True,
                                             no_selection=True))
        self.reload_favs(fav_list)

        libs = self.add_node(TreeLabel(text=self.libraries_string, is_open=True,
                                       no_selection=True))
        places = ('Documents', 'Music', 'Pictures', 'Videos')
        for place in places:
            if isdir(user_path + place):
                self.add_node(TreeLabel(text=place, path=user_path +
                                        place), libs)
        self._computer_node = self.add_node(TreeLabel(text=self.computer_string,is_open=True, no_selection=True))
        self._computer_node.bind(on_touch_down=self._drives_touch)
        self.reload_drives()

    def _drives_touch(self, obj, touch):
        if obj.collide_point(*touch.pos):
            self.reload_drives()

    def reload_drives(self):
        nodes = [(node, node.text + node.path) for node in\
                 self._computer_node.nodes if isinstance(node, TreeLabel)]
        sigs = [s[1] for s in nodes]
        nodes_new = []
        sig_new = []
        for path, name in get_drives():
            if platform == 'win':
                text = u'{}({})'.format((name + ' ') if name else '', path)
            else:
                text = name
            nodes_new.append((text, path))
            sig_new.append(text + path + sep)
        for node, sig in nodes:
            if sig not in sig_new:
                self.remove_node(node)
        for text, path in nodes_new:
            if text + path + sep not in sigs:
                self.add_node(TreeLabel(text=text, path=path + sep),
                              self._computer_node)

    def reload_favs(self, fav_list):
        if platform == 'win':
            user_path = expanduser(u'~')
            if not isdir(user_path + sep + 'Desktop'):
                user_path = dirname(user_path) + sep
            else:
                user_path += sep
        else:
            user_path = expanduser('~') + sep
        favs = self._favs
        remove = []
        for node in self.iterate_all_nodes(favs):
            if node != favs:
                remove.append(node)
        for node in remove:
            self.remove_node(node)
        places = ('Desktop', 'Downloads')
        for place in places:
            if isdir(user_path + place):
                self.add_node(TreeLabel(text=place, path=user_path +
                                        place), favs)
        for path, name in fav_list:
            if isdir(path):
                self.add_node(TreeLabel(text=name, path=path), favs)

    def trigger_populate(self, node):
        if not node.path or node.nodes:
            return
        parent = node.path
        next = walk(parent).next()
        if next:
            for path in next[1]:
                self.add_node(TreeLabel(text=path, path=parent + sep + path),
                              node)


class FileBrowser(BoxLayout):
    """FileBrowser class, see module documentation for more information.
    """

    __events__ = ('on_canceled', 'on_success', 'on_submit')

    select_state = OptionProperty('normal', options=('normal', 'down'))
    '''State of the 'select' button, must be one of 'normal' or 'down'.
    The state is 'down' only when the button is currently touched/clicked,
    otherwise 'normal'. This button functions as the typical Ok/Select/Save
    button.

    :data:`select_state` is an :class:`~kivy.properties.OptionProperty`.
    '''
    cancel_state = OptionProperty('normal', options=('normal', 'down'))
    '''State of the 'cancel' button, must be one of 'normal' or 'down'.
    The state is 'down' only when the button is currently touched/clicked,
    otherwise 'normal'. This button functions as the typical cancel button.

    :data:`cancel_state` is an :class:`~kivy.properties.OptionProperty`.
    '''

    select_string = StringProperty('Ok')
    '''Label of the 'select' button.

    :data:`select_string` is an :class:`~kivy.properties.StringProperty`,
    defaults to 'Ok'.
    '''

    cancel_string = StringProperty('Cancel')
    '''Label of the 'cancel' button.

    :data:`cancel_string` is an :class:`~kivy.properties.StringProperty`,
    defaults to 'Cancel'.
    '''

    listview_string = StringProperty('List View')
    '''Label of the 'list view' button.

    :data:`listview_string` is an :class:`~kivy.properties.StringProperty`,
    defaults to 'List View'.
    '''

    iconview_string = StringProperty('Icon View')
    '''Label of the 'icon view' button.

    :data:`iconview_string` is an :class:`~kivy.properties.StringProperty`,
    defaults to 'Icon View'.
    '''

    favorites_string = StringProperty('Favorites')
    '''Label of the 'Favorites' Section

    :data:`favorites_string` is an :class:`~kivy.properties.StringProperty`,
    defaults to 'Favorites'.
    '''

    libraries_string = StringProperty('Libraries')
    '''Label of the 'Libraries' Section

    :data:`libraries_string` is an :class:`~kivy.properties.StringProperty`,
    defaults to 'Libraries'.
    '''

    computer_string = StringProperty('Computer')
    '''Label of the 'Computer' Section

    :data:`computer_string` is an :class:`~kivy.properties.StringProperty`,
    defaults to 'Computer'.
    '''

    location_string = StringProperty('Locations')
    '''Label of the 'Locations' Section

    :data:`Locations_string` is an :class:`~kivy.properties.StringProperty`,
    defaults to 'Locations'.
    '''

    filename = StringProperty('')
    '''The current text in the filename field. Read only. When multiselect is
    True, the list of selected filenames is shortened. If shortened, filename
    will contain an ellipsis.

    :data:`filename` is an :class:`~kivy.properties.StringProperty`,
    defaults to ''.

    .. versionchanged:: 1.1
    '''

    selection = ListProperty([])
    '''Read-only :class:`~kivy.properties.ListProperty`.
    Contains the list of files that are currently selected in the current tab.
    See :kivy_fchooser:`kivy.uix.filechooser.FileChooserController.selection`.

    .. versionchanged:: 1.1
    '''

    path = StringProperty(u'/')
    '''
    :class:`~kivy.properties.StringProperty`, defaults to the current working
    directory as a unicode string. It specifies the path on the filesystem that
    browser should refer to.
    See :kivy_fchooser:`kivy.uix.filechooser.FileChooserController.path`.

    .. versionadded:: 1.1
    '''

    filters = ListProperty([])
    ''':class:`~kivy.properties.ListProperty`, defaults to []
    Specifies the filters to be applied to the files in the directory.
    See :kivy_fchooser:`kivy.uix.filechooser.FileChooserController.filters`.

    Filering keywords that the user types into the filter field as a comma
    separated list will be reflected here.

    .. versionadded:: 1.1
    '''

    filter_dirs = BooleanProperty(False)
    '''
    :class:`~kivy.properties.BooleanProperty`, defaults to False.
    Indicates whether filters should also apply to directories.
    See
    :kivy_fchooser:`kivy.uix.filechooser.FileChooserController.filter_dirs`.

    .. versionadded:: 1.1
    '''

    show_hidden = BooleanProperty(False)
    '''
    :class:`~kivy.properties.BooleanProperty`, defaults to False.
    Determines whether hidden files and folders should be shown.
    See
    :kivy_fchooser:`kivy.uix.filechooser.FileChooserController.show_hidden`.

    .. versionadded:: 1.1
    '''

    show_fileinput = BooleanProperty(True)
    '''
    :class:`~kivy.properties.BooleanProperty`, defaults to True.
    Determines whether the file name input field should be shown.

    .. versionadded:: 1.2
    '''

    show_filterinput = BooleanProperty(True)
    '''
    :class:`~kivy.properties.BooleanProperty`, defaults to True.
    Determines whether the filter input filed should be shown.

    .. versionadded:: 1.2
    '''


    multiselect = BooleanProperty(False)
    '''
    :class:`~kivy.properties.BooleanProperty`, defaults to False.
    Determines whether the user is able to select multiple files or not.
    See
    :kivy_fchooser:`kivy.uix.filechooser.FileChooserController.multiselect`.

    .. versionadded:: 1.1
    '''

    dirselect = BooleanProperty(False)
    '''
    :class:`~kivy.properties.BooleanProperty`, defaults to False.
    Determines whether directories are valid selections or not.
    See
    :kivy_fchooser:`kivy.uix.filechooser.FileChooserController.dirselect`.

    .. versionadded:: 1.1
    '''

    rootpath = StringProperty(None, allownone=True)
    '''
    Root path to use instead of the system root path. If set, it will not show
    a ".." directory to go up to the root path. For example, if you set
    rootpath to /users/foo, the user will be unable to go to /users or to any
    other directory not starting with /users/foo.
    :class:`~kivy.properties.StringProperty`, defaults to None.
    See :kivy_fchooser:`kivy.uix.filechooser.FileChooserController.rootpath`.

    .. versionadded:: 1.1
    '''

    favorites = ListProperty([])
    '''A list of the paths added to the favorites link bar. Each element
    is a tuple where the first element is a string containing the full path
    to the location, while the second element is a string with the name of
    path to be displayed.

    :data:`favorites` is an :class:`~kivy.properties.ListProperty`,
    defaults to '[]'.
    '''

    transition = ObjectProperty(None)
    '''
    :class:`~kivy.propertiesObjectProperty`, defaults to False.
    sets the transition type between icon view and list view
    If not set, the screenmananager default transition is used (slide)
    .. versionadded:: 1.2
    '''


    def on_success(self):
        pass

    def on_canceled(self):
        pass

    def on_submit(self):
        pass

    def __init__(self, **kwargs):
        super(FileBrowser, self).__init__(**kwargs)
        Clock.schedule_once(self._post_init)

    def _post_init(self, *largs):
        self.ids.icon_view.bind(selection=partial(self._attr_callback, 'selection'),
                                path=partial(self._attr_callback, 'path'),
                                filters=partial(self._attr_callback, 'filters'),
                                filter_dirs=partial(self._attr_callback, 'filter_dirs'),
                                show_hidden=partial(self._attr_callback, 'show_hidden'),
                                multiselect=partial(self._attr_callback, 'multiselect'),
                                dirselect=partial(self._attr_callback, 'dirselect'),
                                rootpath=partial(self._attr_callback, 'rootpath'))
        self.ids.list_view.bind(selection=partial(self._attr_callback, 'selection'),
                                path=partial(self._attr_callback, 'path'),
                                filters=partial(self._attr_callback, 'filters'),
                                filter_dirs=partial(self._attr_callback, 'filter_dirs'),
                                show_hidden=partial(self._attr_callback, 'show_hidden'),
                                multiselect=partial(self._attr_callback, 'multiselect'),
                                dirselect=partial(self._attr_callback, 'dirselect'),
                                rootpath=partial(self._attr_callback, 'rootpath'))

        if not self.show_fileinput:
            self.ids.box_text.remove_widget(self.ids.file_text)
        if not self.show_filterinput:
            self.ids.box_text.remove_widget(self.ids.filt_text)
        if (not self.show_fileinput) and (not self.show_filterinput):
            self.remove_widget(self.ids.spacer1)
            self.remove_widget(self.ids.box_text)

        self.ids.link_tree.libraries_string = self.libraries_string
        self.ids.link_tree.favorites_string = self.favorites_string
        self.ids.link_tree.computer_string = self.computer_string
        self.ids.link_tree.fill_tree(self.favorites)
        self.ids.link_tree.root_options= {'text': self.location_string, 'no_selection':True}

        if self.transition:
            self.ids.sm.transition=self.transition

    def _shorten_filenames(self, filenames):
        if not len(filenames):
            return ''
        elif len(filenames) == 1:
            return filenames[0]
        elif len(filenames) == 2:
            return filenames[0] + ', ' + filenames[1]
        else:
            return filenames[0] + ', _..._, ' + filenames[-1]

    def _attr_callback(self, attr, obj, value):
        setattr(self, attr, getattr(obj, attr))

