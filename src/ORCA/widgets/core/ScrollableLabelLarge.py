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

from kivy.lang                          import Builder
from kivy.uix.recycleview               import RecycleView
from kivy.uix.boxlayout                 import BoxLayout
from kivy.uix.widget                    import Widget
from kivy.metrics                       import dp
from kivy.uix.label                     import Label
from kivy.properties                    import StringProperty
from kivy.properties                    import Property
from kivy.properties                    import BoundedNumericProperty
from kivy.properties                    import NumericProperty
from kivy.properties                    import AliasProperty
# noinspection PyProtectedMember
from kivy.properties                    import dpi2px
from kivy.graphics.opengl               import GL_MAX_TEXTURE_SIZE

from ORCA.widgets.core.Label            import cLabel
from ORCA.widgets.core.TouchRectangle   import cTouchRectangle
from ORCA.utils.TypeConvert             import ToUnicode
from ORCA.utils.TypeConvert             import ToHex
from ORCA.utils.RemoveNoClassArgs       import RemoveNoClassArgs

__all__ = ['cScrollableLabelLarge']


Builder.load_string('''
<cScrollableLabelLargeInner>:
    RecycleBoxLayout:
        default_size_hint: 1, None
        size_hint: None,None
        height: self.minimum_height
''')


# noinspection PyUnusedLocal
class cScrollableLabelLarge(Widget):
    """ Main Widget to display a large text
       By default, x and y scrolling is enabled
       Horizontal scrolling can be disabled by passing
       noxscroll = False
       Supports background color for the Label
       As implementaion it is a Widget which contains a Background (if color is given)
       and a customized RecycleView
       """

    text       = StringProperty('')
    #font_size  = Property('20sp')
    def __init__(self, **kwargs):
        kwargsInner={}
        for k in kwargs:
            if k not in ["size_hint","size","pos","pos_hint"]:
                kwargsInner[k]=kwargs[k]
        self.oScrollableLabelLargeInner=cScrollableLabelLargeInner(**kwargsInner)
        super(self.__class__, self).__init__(**RemoveNoClassArgs(kwargs,Widget))

        self.oBackGround         = None
        if "background_color" in kwargs:
            self.oBackGround=cTouchRectangle(size=self.size,pos=self.pos, background_color=kwargs["background_color"])
            self.add_widget(self.oBackGround)
            del kwargs["background_color"]
        self.oScrollableLabelLargeInner.size = self.size
        self.oScrollableLabelLargeInner.pos  = self.pos
        self.add_widget(self.oScrollableLabelLargeInner)
        self.bind(pos=self.update_graphics_pos,size=self.update_graphics_size)

    def update_graphics_pos(self, instance, value):
        """ Updates the child widget position (Backgrund and Recycleview) """
        if self.oBackGround is not None:
            self.oBackGround.pos = value
        self.oScrollableLabelLargeInner.pos = value
    def update_graphics_size(self, instance, value):
        """ Updates the child widget size (Backgrund and Recycleview) """
        if self.oBackGround is not None:
            self.oBackGround.size = value
        self.oScrollableLabelLargeInner.size = value
    def IncreaseFontSize(self,*args):
        """ Pass through function for the Recycleview """
        self.oScrollableLabelLargeInner.IncreaseFontSize(args)
    def DecreaseFontSize(self,*args):
        """ Pass through function for the Recycleview """
        self.oScrollableLabelLargeInner.DecreaseFontSize(args)
    def on_text(self, instance, value):
        """ Pass through function for the Recycleview """
        self.oScrollableLabelLargeInner.text=value
    def on_oOrcaWidget(self, instance, value):
        """ Passes the OrcaWidget to the Childs """
        if self.oBackGround is not None:
            self.oBackGround.oOrcaWidget=value
        self.oScrollableLabelLargeInner.oOrcaWidget=value

    def _get_font_size(self):
        """Returns the Font Size """
        return self.oScrollableLabelLargeInner.fFontSize
    def _set_font_size(self, value):
        """Passes the change of font size """
        self.oScrollableLabelLargeInner.font_size = value

    font_size  = AliasProperty(_get_font_size, _set_font_size)


# noinspection PyUnusedLocal
class cLineLayoutBase(BoxLayout):
    """ embedded class to present a single line of text """
    text = StringProperty("")
    font_size = NumericProperty(0)
    def __init__(self, **kwargs):
        super(self.__class__,self).__init__(**RemoveNoClassArgs(kwargs,BoxLayout))
        self.oLabel         = cLabel(**self.oScrollableLabelLargeInner.kwFontArgs)
        if self.oScrollableLabelLargeInner.oOrcaWidget is not None:
            self.oLabel.oOrcaWidget = self.oScrollableLabelLargeInner.oOrcaWidget
        self.add_widget(self.oLabel)
    def on_size(self,*largs):
        """ Updates the child widget size (label) """
        self.oLabel.height      =  self.height
        self.oLabel.text_size   =  self.size
    def on_text(self,instance,value):
        """ sets the text """
        self.oLabel.text=value
    def on_font_size(self,instance,value):
        """ sets the font size """
        self.oLabel.font_size=value


# noinspection PyProtectedMember,PyUnusedLocal
class cScrollableLabelLargeInner(RecycleView):
    """ The "real' scrollable label (without background) """

    # to have similar properties as a Label
    font_size  = Property('20sp')
    text       = StringProperty('')
    oOrcaWidget = Property(None)
    # Internal Property which handles fonmt resizing (not working as RecycleView can't manage change of cached widget)
    fFontSize  = BoundedNumericProperty(dpi2px(20,'sp'), min=4.0, max=96.0,errorhandler=lambda x: 96.0 if x > 96.0 else 4.0)

    def __init__(self, **kwargs):

        #we create a new class on the fly top ass  the font args to the creation process, as the view adapter creates without arguments
        self.cLineLayout=type('cLineLayout', cLineLayoutBase.__bases__, dict(cLineLayoutBase.__dict__))
        # passes myself to the embedded class. Not good style but Recycleview limits passing customized parameters
        self.cLineLayout.oScrollableLabelLargeInner=self

        self.oOrcaWidget = kwargs.get('ORCAWIDGET',None)
        # maximal len (in chars) of a single ine of the given text
        self.iMaxLen                = 0
        # Setting the scrolltypes / bars for the Recycleview
        self.scroll_type            = ['bars', 'content']
        self.scroll_wheel_distance  = dp(114)
        self.bar_width              = dp(10)
        # The original passed Data array
        self.aData                  = []
        # Internal Flag to distinguish between first show and (re) setting text
        self.bInit                  = False
        # The maximum width of a char
        self.iMaxCharwidth          = 0
        # The maximum  characters per line
        self.iMaxCharsPerLine       = 0
        if "font_size" in kwargs:
            self.on_font_size(None,kwargs["font_size"])

        # Retieving the genuine font propertes of a label to pass only those arguments to the label (removing pos, hints, background colors , etc
        self.aFontProperties             = Label._font_properties+("background_color",)
        # standard font args, if nothing is given
        self.kwFontArgs                  = {"halign" : "left","valign": "top", "max_lines":1,"font_size":20}

        # add / update the font args to be passed to the Label
        for k in kwargs:
            if k in self.aFontProperties:
                self.kwFontArgs[k]=kwargs[k]
        self.kwFontArgs["font_size"]=self.fFontSize
        self.kwFontArgs.pop("text",None)

        # Parameter Flag to disable horizontal scrolling
        self.bNoXScroll = kwargs.get("noxscroll",False)
        self.bMarkup = kwargs.get("markup", False)
        #A dummy label to get th width a the larges character
        self.oLabel = Label(**RemoveNoClassArgs(self.kwFontArgs,Label))

        super(self.__class__, self).__init__(**RemoveNoClassArgs(kwargs,RecycleView))
        # This manages the distance between lines
        self.layout_manager.default_size = (None,self.oLabel._label.get_extents('W')[1])
        #self.layout_manager.default_size = (None, self.fFontSize*1.1)
        self.layout_manager.orientation  = 'vertical'

        # we need to handle size changes
        self.bind(size=self.update_size)
        self.bind(text=self.on_textinner)
        self.text = kwargs.get("text","")

    def on_fFontSize(self, instance, value):
        """ Will handle font size changes  """
        if self.layout_manager is not None:
            self.kwFontArgs["font_size"]=self.fFontSize
            self.oLabel.font_size = self.fFontSize
            self.layout_manager.default_size = (None,self.oLabel._label.get_extents('W')[1])
            self.SetData(self.aData)

    def on_font_size(self, instance, value):
        """Helper function to manage strings with metrics passed as arguments (eg '12dp') """
        try:
            fValue=float(value)
        except:
            fValue=dpi2px(value[:-2],value[-2:])
        self.fFontSize=fValue

    def on_textinner(self, instance, value):
        """ helper to have a Label like funtionality to set the caption """
        self.update_size(None,None)
    def IncreaseFontSize(self,*args):
        """ Increase the Font size """
        self.fFontSize        +=1.0
    def DecreaseFontSize(self,*args):
        """ Decrease the Font size """
        self.fFontSize        -=1.0
    def SetData(self, aData):
        """ Passes the data to the Recycle view and sets the layout manager size """
        self.data = [{'text': ToUnicode(x),"font_size":self.fFontSize} for x in aData]

        if self.bNoXScroll:
            self.layout_manager.width=self.width
        else:
            self.layout_manager.width= self.iMaxCharwidth * self.iMaxCharsPerLine
        self.viewclass              = self.cLineLayout
        self.refresh_from_data()


    def update_size(self, instance, value):
        """ Fits the text into layout_manager line.
        If noxscroll, all line with be split up to fit to the widget size.
        if x scrolling is enabled, we look, if the the maximum line lenght exceed the TEXTURE SIZE.
        In that case we split the lines as well and set the scrolling window size to the texture size.
        if x scrolling is enabled, and all lines fit to the texture size, we pass the unchanged array """

        if self.size==[100,100]:
            return

        aData                   = []
        bDoLineBreak            = False
        self.iMaxCharwidth      = self.oLabel._label.get_extents('W')[0]
        self.iMaxCharsPerLine   = int(self.width/self.iMaxCharwidth)

        if not self.bNoXScroll:
            self.aData = self.text.split('\n')

            self.iMaxLen=len(max(self.aData,key=len))
            if (self.iMaxCharwidth*self.iMaxLen)>GL_MAX_TEXTURE_SIZE:
                self.iMaxCharsPerLine=int(GL_MAX_TEXTURE_SIZE/self.iMaxCharwidth)
                bDoLineBreak = True
            else:
                self.iMaxCharsPerLine=self.iMaxLen
        else:
            bDoLineBreak = True

        if bDoLineBreak:
            if self.oLabel is not None:
                if len(self.text)>10000:
                    aData = self.text.split('\n')
                    i=0
                    iEnd=len(aData)

                    while i<iEnd:
                        if len(aData[i])>self.iMaxCharsPerLine:
                            aData.insert(i+1,aData[i][self.iMaxCharsPerLine:])
                            aData[i]=aData[i][:self.iMaxCharsPerLine]
                            iEnd+=1
                        i+=1
                else:
                    self.oLabel.size      = self.size
                    self.oLabel.text_size = (self.width,None)
                    self.oLabel.text      = self.text
                    self.oLabel._label.render()
                    aData=[]
                    for oLine in self.oLabel._label._cached_lines:
                        if len(oLine.words)>0:
                            uText= u''
                            for oWord in oLine.words:
                                if self.bMarkup:
                                    uText+=self.AddMarkUps(oWord)
                                else:
                                    uText+=oWord.text
                            aData.append(uText)
                        else:
                            aData.append(u'')
                    self.oLabel.text = ""

            self.aData = aData
            self.SetData(aData)
        else:
            self.SetData(self.aData)


    def AddMarkUps(self,oWord):

        uText=oWord.text
        if oWord.options["bold"]:
            uText=self.AddMarkUp(uText,"b")
        if oWord.options["italic"]:
            uText=self.AddMarkUp(uText,"i")
        if oWord.options["underline"]:
            uText=self.AddMarkUp(uText,"u")
        if oWord.options["strikethrough"]:
            uText=self.AddMarkUp(uText,"s")
        if oWord.options["font_name"] != "Roboto":
            uText=self.AddMarkUp(uText,"font",oWord.options["font_name"])
        if oWord.options["font_size"] != self.fFontSize:
            uText=self.AddMarkUp(uText,"size",ToUnicode(oWord.options["font_size"]))

        if oWord.options["color"] != [1,1,1,1]:
            uHexColor = u''
            for iColor in oWord.options["color"]:
                uHexColor+=ToHex(int(iColor*255))
            uText=self.AddMarkUp(uText,"color",'#'+uHexColor)

        return uText

    # noinspection PyMethodMayBeStatic
    def AddMarkUp(self,uText,uMarkUp,uValue=None):
        if uValue is None:
            return "[{1}]{0}[/{1}]".format(uText,uMarkUp)
        else:
            return "[{1}={2}]{0}[/{1}]".format(uText,uMarkUp,uValue)
