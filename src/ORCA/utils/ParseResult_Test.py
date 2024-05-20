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


from kivy.logger             import Logger
from ORCA.utils.TypeConvert  import ToUnicode
from ORCA.utils.ParseResult  import cResultParser


# noinspection PyUnusedLocal
def ResultParser_Test():
    dTest:dict = {
                  "destination_addresses":
                    [
                        "Philadelphia, PA, USA",
                        "Street without name"
                    ],
                  "origin_addresses":"New York, NY, USA",
                  "rows":
                    [
                        {
                          "elements":
                            [
                                {
                                    "distance":
                                    {
                                        "text": "94.6 mi",
                                        "value": 152193
                                    },
                                    "duration":
                                    {
                                        "text": "1 hour 44 mins",
                                        "value": 6227
                                    },
                                "status": "OK"
                                }
                             ]
                        }
                    ],
                    "status": "OK"
                }



    uXml = '''<?xml version="1.0"?> 
        <?xml-stylesheet href="catalog.xsl" type="text/xsl"?>
        <!DOCTYPE catalog SYSTEM "catalog.dtd">
        <catalog>
           <product description="Cardigan Sweater" product_image="cardigan.jpg">
              <catalog_item gender="Men's">
                 <item_number>QWZ5671</item_number>
                 <price>39.95</price>
                 <size description="Medium">
                    <color_swatch image="red_cardigan.jpg">Red</color_swatch>
                    <color_swatch image="burgundy_cardigan.jpg">Burgundy</color_swatch>
                 </size>
                 <size description="Large">
                    <color_swatch image="red_cardigan.jpg">Red</color_swatch>
                    <color_swatch image="burgundy_cardigan.jpg">Burgundy</color_swatch>
                 </size>
              </catalog_item>
              <catalog_item gender="Women's">
                 <item_number>RRX9856</item_number>
                 <price>42.50</price>
                 <size description="Small">
                    <color_swatch image="red_cardigan.jpg">Red</color_swatch>
                    <color_swatch image="navy_cardigan.jpg">Navy</color_swatch>
                    <color_swatch image="burgundy_cardigan.jpg">Burgundy</color_swatch>
                 </size>
                 <size description="Medium">
                    <color_swatch image="red_cardigan.jpg">Red</color_swatch>
                    <color_swatch image="navy_cardigan.jpg">Navy</color_swatch>
                    <color_swatch image="burgundy_cardigan.jpg">Burgundy</color_swatch>
                    <color_swatch image="black_cardigan.jpg">Black</color_swatch>
                 </size>
                 <size description="Large">
                    <color_swatch image="navy_cardigan.jpg">Navy</color_swatch>
                    <color_swatch image="black_cardigan.jpg">Black</color_swatch>
                 </size>
                 <size description="Extra Large">
                    <color_swatch image="burgundy_cardigan.jpg">Burgundy</color_swatch>
                    <color_swatch image="black_cardigan.jpg">Black</color_swatch>
                 </size>
              </catalog_item>
           </product>
        </catalog>
    '''

    ''' 
    This XML would be converted into the following dict to parse

   {
    'catalog': 
    {
     'product': 
     {
      'attributes': 
      {
       'description': 'Cardigan Sweater', 
       'description[0]': 'Cardigan Sweater', 
       'product_image': 'cardigan.jpg', 
       'product_image[0]': 'cardigan.jpg'
      }, 
      'catalog_item': 
      [
       {
        'attributes': 
        {
         'gender': "Men's", 
         'gender[0]': "Men's"
        }, 
        'item_number': 'QWZ5671', 
        'price': '39.95', 
        'size': 
        [
         {
          'attributes': 
          {
           'description': 'Medium', 
           'description[0]': 'Medium', 
           'image[0]': 'red_cardigan.jpg', 
           'image[1]': 'burgundy_cardigan.jpg'
          }, 
          'color_swatch': 
          [
           'Red', 
           'Burgundy'
          ]
         }, 
         {
          'attributes': 
          {
           'description': 'Large', 
           'description[0]': 'Large', 
           'image[0]': 'red_cardigan.jpg', 
           'image[1]': 'burgundy_cardigan.jpg'
          }, 
        'color_swatch': 
        [
         'Red', 
         'Burgundy'
        ]
       }
      ]
     }, 
     {
      'attributes': 
      {
       'gender': "Women's", 
       'gender[0]': "Women's"
      }, 
      'item_number': 'RRX9856', 
      'price': '42.50', 
      'size': 
      [
       {
        'attributes': 
        {
         'description': 'Small', 
         'description[0]': 'Small', 
         'image[0]': 'red_cardigan.jpg', 
         'image[1]': 'navy_cardigan.jpg', 
         'image[2]': 'burgundy_cardigan.jpg'
        }, 
        'color_swatch': 
        [
         'Red', 
         'Navy', 
         'Burgundy'
        ]
       }, 
       {
        'attributes': 
        {
         'description': 'Medium', 
         'description[0]': 'Medium', 
         'image[0]': 'red_cardigan.jpg', 
         'image[1]': 'navy_cardigan.jpg', 
         'image[2]': 'burgundy_cardigan.jpg', 
         'image[3]': 'black_cardigan.jpg'
        }, 
        'color_swatch': 
        [
         'Red', 
         'Navy', 
         'Burgundy', 
         'Black'
        ]
       }, 
       {
        'attributes': 
        {
         'description': 'Large',
         'description[0]': 'Large',
         'image[0]': 'navy_cardigan.jpg', 
         'image[1]': 'black_cardigan.jpg'}, 
         'color_swatch': 
         [
          'Navy', 
          'Black'
         ]
        }, 
        {
         'attributes': 
         {
          'description': 'Extra Large',
          'description[0]': 'Extra Large', 
          'image[0]': 'burgundy_cardigan.jpg', 
          'image[1]': 'black_cardigan.jpg'
         }, 
         'color_swatch': 
         [
          'Burgundy',
          'Black'
         ]
        }
       ]
      }
     ]
    }
   }
  }
  
    '''

    oResultParser       = cResultParser()
    uResponse           = ToUnicode(dTest)
    uLocalDestVar       = ''
    uTokenizeString     = ''
    uParseResultOption  = 'dict'

    Logger.debug('Example 1: Simple Pick from dict')
    uGetVar             = 'destination_addresses'
    uGlobalDestVar      = 'MyVar'
    uParseResultFlags   = ''
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 2: Pick as array from dict')
    uGetVar             = 'destination_addresses'
    uGlobalDestVar      = 'MyVar'
    uParseResultFlags   = 'A'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 3: Unsuccessful pick from dict')
    uGetVar             = 'text'
    uGlobalDestVar      = 'MyVar'
    uParseResultFlags   = ''
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 4: simple unique pick from dict')
    uGetVar             = 'text'
    uGlobalDestVar      = 'MyVar'
    uParseResultFlags   = 'U'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 5: Direct pick from structure from dict')
    uGetVar             = 'rows,elements,duration,value'
    uGlobalDestVar      = 'MyVar'
    uParseResultFlags   = ''
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 6: Multivar pick from dict')
    uGetVar             = '"destination_addresses","rows,elements,duration,value"'
    uGlobalDestVar      = '"MyResult_Address","MyResult_Duration"'
    uParseResultFlags   = 'L'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 7: Multivar unique pick from dict')
    uGetVar             = '"destination_addresses","value"'
    uGlobalDestVar      = '"MyResult_Address","MyResult_Duration"'
    uParseResultFlags   = 'UL'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 8: Multivar, Array unique pick from dict')
    uGetVar             = '"destination_addresses","value"'
    uGlobalDestVar      = '"MyResult_Address","MyResult_Duration"'
    uParseResultFlags   = 'ULA'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 9: Multivar, Array unique pick, with not enough values from dict')
    uGetVar             = '"destination_addresses","origin_addresses"'
    uGlobalDestVar      = '"MyResult_Address","MyResult_Origin"'
    uParseResultFlags   = 'ULA'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)


    Logger.debug('Example 10: Get everything values')
    uGlobalDestVar      = 'MyResult'
    uParseResultFlags   = 'E'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    uResponse = '{"locations": [{"id": "875f468b-18b7-4861-92d3-463a4bc1c7db","name": "My Garden","authorized_at": "2020-03-14T10:22:24.682Z","authorized_user_ids": [],"device_flashing": {},"devices": ["8a0afcf8-8d0a-4bbb-acd6-425aa6720295","4f967509-2c86-406e-bd1d-03bd88bf6fe0","b0305931-17e1-4701-b7d4-d3f5b59b4bbf","1efc9553-3dec-4a72-b6e8-2843a30666ff"],"geo_position": {"latitude": 51.2742326,"longitude": 6.790471400000001,"address": "Am Klosterhof, 40472 Düsseldorf, Deutschland","city": "Düsseldorf","gateway_time_zone": "Europe/Berlin","gateway_time_zone_offset": 7200000,"id": "9189c5e2-ede2-4f74-ba61-7101876cf774","sunrise": "06:32","sunset": "20:33","time_zone": "Europe/Berlin","time_zone_offset": 7200000},"zones": []}]}'

    Logger.debug('Example 10a: Get everything values')
    uGlobalDestVar      = 'MyResult'
    uParseResultFlags   = 'E'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)


    Logger.debug('Example 10b: a further test')
    uGlobalDestVar      = 'MyResult'
    uParseResultFlags   = 'E'
    uVarName, uVarValue = oResultParser.Parse(uResponse="{'Fruit1':'Apple','Fruit2':'Peach','Metal':{'Gold':'Not Platin'}}",uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)
    uVarName, uVarValue = oResultParser.Parse(uResponse='{"sessions": {"token": "13554183-66a9-44a7-92a1-0c7e3c6eb100","user_id": "076825b3-d33b-4431-9b04-4ab9e6d0556b","refresh_token": "5a239f50-706c-4f9a-97d9-878a58571328"}}',uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 11: Get a List')
    uGlobalDestVar = 'MyResult'
    uParseResultFlags = ''
    uParseResultOption = 'list'
    uVarName, uVarValue = oResultParser.Parse(uResponse="['apple','pear','Cherry']", uGetVar=uGetVar, uParseResultOption=uParseResultOption, uGlobalDestVar=uGlobalDestVar, uLocalDestVar=uLocalDestVar, uTokenizeString='',
                                              uParseResultFlags=uParseResultFlags)

    # '{"sessions": {"token": "13554183-66a9-44a7-92a1-0c7e3c6eb100","user_id": "076825b3-d33b-4431-9b04-4ab9e6d0556b","refresh_token": "5a239f50-706c-4f9a-97d9-878a58571328"}}'

    exit(0)

    uResponse          = uXml
    uParseResultOption = 'xml'

    Logger.debug('Example 10: Simple Unique Value Pick from xml')
    uGetVar             = 'item_number'
    uGlobalDestVar      = 'MyVar'
    uParseResultFlags   = 'U'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 11: Simple Unique Attribute Pick from xml')
    uGetVar             = 'gender'
    uGlobalDestVar      = 'MyVar'
    uParseResultFlags   = 'U'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 12: Simple Direct Value Pick from xml')
    uGetVar             = 'catalog,product,catalog_item,size,color_swatch'
    uGlobalDestVar      = 'MyVar'
    uParseResultFlags   = ''
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)

    Logger.debug('Example 13: Wildcard list pick')
    uGetVar             = 'catalog,product,catalog_item,size,attributes,image*'
    uGetVar             = 'catalog,product,attributes,product_image*'
    uGlobalDestVar      = 'MyVar'
    uParseResultFlags   = 'A'
    uVarName, uVarValue = oResultParser.Parse(uResponse=uResponse,uGetVar=uGetVar,uParseResultOption=uParseResultOption,uGlobalDestVar=uGlobalDestVar,uLocalDestVar=uLocalDestVar,uTokenizeString=uTokenizeString,uParseResultFlags=uParseResultFlags)
