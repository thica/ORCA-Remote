<?xml version='1.0' encoding='UTF-8'?>
<!-- Translates Orca Actions to Interface Commands action = Orca Action String -->
<includes  xmlns:xi="http://www.w3.org/2001/XInclude">

  <repositorymanager>
    <entry>
      <name>ELV Max</name>
      <description language='English'>Default commandset for ELV MAX</description>
      <description language='German'>Standard Kommandos für ELV MAX</description>
      <author>Carsten Thielepape</author>
      <version>3.70</version>
      <minorcaversion>3.7.0</minorcaversion>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/codesets/elv_max/CODESET_elv_max_DEFAULT.xml</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/codesets/CODESET_elv_max_DEFAULT.zip</sourcefile>
          <targetpath>codesets/elv_max</targetpath>
        </source>
      </sources>
      <dependencies>
        <dependency>
          <type>interfaces</type>
          <name>ELV MAX</name>
        </dependency>
      </dependencies>
    </entry>
  </repositorymanager>

  <action string="codeset" name='clearcache'                  cmd='{"method": "clearcache",             "params": {}}'  />
  <action string="codeset" name='getrooms'                    cmd='{"method": "getrooms",               "params": {}}'                       gdestvar='"elvmax_name","elvmax_rfaddress","elvmax_type"'  getvar='ORCAMULTI"name","rf_address","type"' />
  <action string="codeset" name='getroomdevices'              cmd='{"method": "getroomdevices",         "params": {"room": "$cvar(room)"}}'  gdestvar='"elvmax_name","elvmax_rfaddress","elvmax_type"'  getvar='ORCAMULTI"name","rf_address","type"' />
  <action string="codeset" name='getroomdevicesex'            cmd='{"method": "getroomdevicesex",       "params": {"room": "$cvar(room)"}}'  gdestvar='"elvmax_name","elvmax_rfaddress","elvmax_type"'  getvar='ORCAMULTI"name","rf_address","type"' />
  <action string="codeset" name='getattribute'                cmd='{"method": "getattribute",           "params": {"rf_address": "$cvar(rf_address)","attributename":"$cvar(attributename)"}}' ldestvar='elvmax_attribute' gdestvar='"elvmax_attribute"'  getvar='result' />
  <action string="codeset" name='getattributelist'            cmd='{"method": "getattributelist",       "params": {"rf_address": "$cvar(rf_address)","attributename":"$cvar(attributename)"}}' ldestvar='elvmax_attribute' gdestvar='"elvmax_attribute"'  getvar='resultlist' />
  <action string="codeset" name='getattributelistex'          cmd='{"method": "getattributelist",       "params": {"rf_address": "$cvar(rf_address)","attributename":"$cvar(attributename)"}}' ldestvar='elvmax_attribute' gdestvar='"elvmax_attribute"'  getvar='resultlist' />
  <action string="codeset" name='room_set_mode_auto'          cmd='{"method": "room_set_mode_auto",     "params": {"room": "$cvar(room)"}}'                                                              gdestvar='elvmax_result' getvar='result'  />
  <action string="codeset" name='room_set_mode_manual'        cmd='{"method": "room_set_mode_manual",   "params": {"room": "$cvar(room)","temperature": "$cvar(temperature)"}}'                          gdestvar='elvmax_result' getvar='result'  />
  <action string="codeset" name='room_set_mode_boost'         cmd='{"method": "room_set_mode_boost",    "params": {"room": "$cvar(room)"}}'                                                              gdestvar='elvmax_result' getvar='result'  />
  <action string="codeset" name='device_set_mode_auto'        cmd='{"method": "device_set_mode_auto",   "params": {"rf_address": "$cvar(rf_address)"}}'                                                  gdestvar='elvmax_result' getvar='result'  />
  <action string="codeset" name='device_set_mode_manual'      cmd='{"method": "device_set_mode_manual", "params": {"rf_address": "$cvar(rf_address)","temperature": "$cvar(temperature)"}}'              gdestvar='elvmax_result' getvar='result'  />
  <action string="codeset" name='device_set_mode_boost'       cmd='{"method": "device_set_mode_auto",   "params": {"rf_address": "$cvar(rf_address)"}}'                                                  gdestvar='elvmax_result' getvar='result'  />
  <action name="ping" type="alias" cmd="getrooms" />
</includes>

  <!--

  available attributes

  'c_boost_duration': u'5'
  'c_boost_raw': u'48',
  'c_boost_valve_setting': u'80'
  'c_comfort_temperature': u'22.5'
  'c_comfort_temperature_raw': u'45'
  'c_decalcification_day': u'0'
  'c_decalcification_hour': u'12'
  'c_decalcification_raw': u'12'
  'c_device_type': u'1'
  'c_eco_temperature': u'16.5'
  'c_eco_temperature_raw': u'33'
  'c_firmware_version': u'21'
  'c_max_set_point_temperature': u'23.0'
  'c_max_set_point_temperature_raw': u'46',
  'c_max_valve_raw': u'255'
  'c_max_valve_setting': u'100'
  'c_min_set_point_temperature': u'4.5'
  'c_min_set_point_temperature_raw': u'9'
  'c_room_id': u'1',
  'c_serial_number': u'JEQ018921'
  'c_temperature_offset': u'0.0'
  'c_temperature_offset_raw': u'7'
  'c_test_result': u'-1'
  'c_valve_offset_raw': u'0'
  'c_window_open_duration': u'15.0',
  'c_window_open_duration_raw': u'3'
  'c_window_open_temperature': u'12.0'
  'c_window_open_temperature_raw': u'24'
  'name': u'Wohnzimmer',
  'rf_address': '0270f0'
  's_actual_temperature': u'0.0'
  's_battery_low': u'False'
  's_boost_program': u'False'
  's_description': u'SingleLResponse: RF addr: 0270f0, program: (weekly: False, manual: True, vacation: False, boost_program: False
  's_dst_active': u'8'
  's_gateway_known': u'True'
  's_is_answer': u'False'
  's_is_error': u'False'
  's_is_valid': u'False',
  's_link_ok': u'True'
  's_manual_program': u'True'
  's_panel_locked': u'False'
  's_status_initialized': u'True'
  's_temperature': u'22.5'
  's_vacation_program': u'False'
  's_valve_position': u'60'
  's_weekly_program': u'False'
  'type': 'radiatorthermostat'
   actual_temperature: 0.0'
   battery_low: False
   gateway_known: True
   is_answer: False
   is_error: False
   is_valid: False
   link_ok: True
   panel_locked: False
   status_initialized: True
   temperature: 22.5
   time_until: 0:00:00
   valve_position: 60

  -->
