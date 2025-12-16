import cx_Oracle
from datetime import datetime
import loggerutility as logger
import re
from loggerutility import deployment_log

class Obj_Actions:

    sql_models = []
    event_context = 1
    
    def insert_or_update_actions(self, actions, connection, con_type):

        required_keys = [
            'obj_name', 'line_no', 'title'
        ]

        missing_keys = [key for key in required_keys if key not in actions]

        if missing_keys:
            deployment_log(f"Missing required keys for obj_actions table: {', '.join(missing_keys)}")
            raise KeyError(f"Missing required keys for obj_actions table: {', '.join(missing_keys)}")
        else:
            obj_name = actions.get('obj_name', '') or None
            line_no = actions.get('line_no', '') or None
            image = actions.get('image', '') or None
            service_code_from_action_json = actions.get('service_code', '') or None
            interactive = actions.get('interactive', '') or None
            rights_char = actions.get('rights_char', '') or None
            title = actions.get('title', '') or None
            form_no = actions.get('form_no', '') or None
            service_handler = actions.get('service_handler', '') or None
            placement = actions.get('placement', '') or None
            action_type = actions.get('action_type', '') or None
            tran_type = actions.get('tran_type', '') or None
            chg_date = datetime.now().strftime('%d-%m-%y')
            chg_term = actions.get('chg_term', '').strip() or 'System'
            chg_user = actions.get('chg_user', '').strip() or 'System'
            is_confirmation_req = actions.get('confirmation_req', '') or None
            sep_duty_opt = actions.get('sep_duty_opt', '') or None
            re_auth_opt = actions.get('re_auth_opt', '') or None
            show_in_panel = actions.get('show_in_panel', '') or None
            page_context = actions.get('page_context', '') or None
            type_ = actions.get('type', '') or None
            action_arg = actions.get('action_arg', '') or None
            swipe_position = actions.get('swipe_position', '') or None
            multi_row_opt = actions.get('multi_row_opt', '') or None
            action_id = actions.get('id', '') or None
            def_nodata = actions.get('def_no_data', '') or None
            in_proc_intrupt = actions.get('in_proc_intrupt', '') or None
            estimated_time = actions.get('estimated_time', '') or None
            action_group = actions.get('action_group', '') or None
            display_opt = actions.get('display_opt', '') or None
            display_mode = actions.get('display_mode', '') or None
            show_confirm = actions.get('show_confirm', '') or None
            rec_specific = actions.get('rec_specific', '') or None
            
            arg_list = actions.get('arg_list', []) or []
            function_name = actions.get('function_name', '') or None
            function_desc = actions.get('function_desc', '') or None

            service_code = f"{obj_name}_{function_name}"
            description = function_desc

            # cursor = connection.cursor()
            # cursor.execute(f"SELECT COUNT(*) FROM obj_actions WHERE OBJ_NAME = '{obj_name}' AND LINE_NO = '{line_no}'")
            # count = cursor.fetchone()[0]
            # cursor.close()
            # if count > 0:
            #     event_code = service_code

            #     cursor = connection.cursor()
            #     cursor.execute(f"""
            #         SELECT COUNT(*) FROM SYSTEM_EVENTS 
            #         WHERE OBJ_NAME = '{obj_name}' and EVENT_CODE = '{event_code}'
            #     """)

            #     count_system_events = cursor.fetchone()[0]
            #     logger.log(f"Count SYSTEM_EVENTS {count_system_events}")
            #     cursor.close()
            #     if count_system_events > 0:
            #         cursor = connection.cursor()
            #         delete_query = f"""
            #             DELETE FROM SYSTEM_EVENTS 
            #             WHERE OBJ_NAME = '{obj_name}' and EVENT_CODE = '{event_code}'
            #         """
            #         logger.log(f"Class Obj_Actions delete_query ::: {delete_query}")
            #         cursor.execute(delete_query)

            #         cursor.close()
            #         logger.log("Data deleted from SYSTEM_EVENTS") 

            #     cursor = connection.cursor()
            #     if con_type == 'Oracle':
            #         insert_query = """
            #             INSERT INTO SYSTEM_EVENTS (
            #                 OBJ_NAME, EVENT_CODE, EVENT_CONTEXT, SERVICE_CODE, METHOD_RULE, OVERWRITE_CORE, 
            #                 CHG_DATE, CHG_USER, CHG_TERM, RESULT_HANDLE, COMP_TYPE, COMP_NAME, COMM_FORMAT, FIELD_NAME
            #             ) VALUES (
            #                 :obj_name, :event_code, :event_context, :service_code, :method_rule, :overwrite_core, 
            #                 TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :result_handle, :comp_type, 
            #                 :comp_name, :comm_format, :field_name
            #             )
            #         """
            #         values = {
            #             'obj_name': obj_name,
            #             'event_code': event_code,
            #             'event_context': self.event_context,
            #             'service_code': service_code,
            #             'method_rule': None,
            #             'overwrite_core': '0',
            #             'chg_date': datetime.now().strftime('%d-%m-%y'),  
            #             'chg_user': 'System',
            #             'chg_term': 'System',
            #             'result_handle': '2',
            #             'comp_type': 'DB',
            #             'comp_name': function_name,
            #             'comm_format': None,
            #             'field_name': ''
            #         }
            #         logger.log(f"\n--- Class Obj_Actions ---\n")
            #         logger.log(f"insert_query values :: {values}")
            #         cursor.execute(insert_query, values)
            #         logger.log(f"Successfully inserted row.")
            #     else:
            #         insert_query = """
            #             INSERT INTO SYSTEM_EVENTS (
            #                 OBJ_NAME, EVENT_CODE, EVENT_CONTEXT, SERVICE_CODE, METHOD_RULE, OVERWRITE_CORE, 
            #                 CHG_DATE, CHG_USER, CHG_TERM, RESULT_HANDLE, COMP_TYPE, COMP_NAME, COMM_FORMAT, FIELD_NAME
            #             ) VALUES (
            #                 %s, %s, %s, %s, %s, %s, 
            #                 TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s, %s, 
            #                 %s, %s, %s
            #             )
            #         """
            #         values = (
            #             obj_name,
            #             event_code,
            #             self.event_context,
            #             service_code,
            #             None,  
            #             '0',
            #             datetime.now().strftime('%d-%m-%Y'),  
            #             'System',
            #             'System',
            #             '2',
            #             'DB',
            #             function_name,
            #             None, 
            #             ''  
            #         )
            #         logger.log(f"\n--- Class Obj_Actions ---\n")
            #         logger.log(f"insert_query values :: {values}")
            #         cursor.execute(insert_query, values)
            #         logger.log(f"Successfully inserted row.")
            #     cursor.close()
            #     logger.log("Data inserted from SYSTEM_EVENTS")  
            #     logger.log(f"{service_code}") 

            #     # -------------------------------------------------------------------------------------

            #     cursor = connection.cursor()
            #     cursor.execute(f"""
            #         SELECT COUNT(*) 
            #         FROM SYSTEM_EVENT_SERVICES 
            #         WHERE SERVICE_CODE = '{service_code}'
            #     """)
            #     count_system_services = cursor.fetchone()[0]
            #     logger.log(f"Count SYSTEM_EVENT_SERVICES {count_system_services}")
            #     cursor.close()
            #     if count_system_services > 0:
            #         cursor = connection.cursor()
            #         delete_query = f"DELETE FROM SYSTEM_EVENT_SERVICES WHERE SERVICE_CODE = '{service_code}'"
            #         logger.log(f"Class Obj_Actions delete_query ::: {delete_query}")
            #         cursor.execute(delete_query)
            #         cursor.close()
            #         logger.log("Data deleted from SYSTEM_EVENT_SERVICES") 

            #     cursor = connection.cursor()
            #     if con_type == 'Oracle':
            #         insert_query = """
            #             INSERT INTO SYSTEM_EVENT_SERVICES (
            #                 SERVICE_CODE, SERVICE_DESCR, SERVICE_URI, SERVICE_PROVIDER, METHOD_NAME, 
            #                 RETURN_VALUE, RETURN_TYPE, RETURN_DESCR, RETURN_XFRM, CHG_DATE, 
            #                 CHG_USER, CHG_TERM, SERVICE_NAMESPACE, RES_ELEM, SOAP_ACTION
            #             ) VALUES (
            #                 :service_code, :service_descr, :service_uri, :service_provider, :method_name, 
            #                 :return_value, :return_type, :return_descr, :return_xfrm, 
            #                 TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, 
            #                 :service_namespace, :res_elem, :soap_action
            #             )
            #         """
            #         values = {
            #             'service_code': service_code,
            #             'service_descr': function_desc,
            #             'service_uri': function_name,
            #             'service_provider': '',
            #             'method_name': ' ',
            #             'return_value': '',
            #             'return_type': '',
            #             'return_descr': '',
            #             'return_xfrm': '',
            #             'chg_date': datetime.now().strftime('%d-%m-%Y'),  
            #             'chg_user': 'System',
            #             'chg_term': 'System',
            #             'service_namespace': '',
            #             'res_elem': '',
            #             'soap_action': ''
            #         }
            #         logger.log(f"\n--- Class Obj_Actions ---\n")
            #         logger.log(f"insert_query values :: {values}")
            #         cursor.execute(insert_query, values)
            #         logger.log(f"Successfully inserted row.")
            #     else:
            #         insert_query = """
            #             INSERT INTO SYSTEM_EVENT_SERVICES (
            #                 SERVICE_CODE, SERVICE_DESCR, SERVICE_URI, SERVICE_PROVIDER, METHOD_NAME, 
            #                 RETURN_VALUE, RETURN_TYPE, RETURN_DESCR, RETURN_XFRM, CHG_DATE, 
            #                 CHG_USER, CHG_TERM, SERVICE_NAMESPACE, RES_ELEM, SOAP_ACTION
            #             ) VALUES (
            #                 %s, %s, %s, %s, %s, 
            #                 %s, %s, %s, %s, 
            #                 TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, 
            #                 %s, %s, %s
            #             )
            #         """
            #         values = (
            #             service_code,
            #             function_desc,
            #             function_name,
            #             None,  
            #             ' ',  
            #             None,
            #             None,
            #             None,
            #             None,
            #             datetime.now().strftime('%d-%m-%Y'),  
            #             'System',
            #             'System',
            #             None,
            #             None,
            #             None
            #         )
            #         logger.log(f"\n--- Class Obj_Actions ---\n")
            #         logger.log(f"insert_query values :: {values}")
            #         cursor.execute(insert_query, values)
            #         logger.log(f"Successfully inserted row.")
            #     cursor.close()
            #     logger.log("Data inserted from SYSTEM_EVENT_SERVICES") 
            #     logger.log(f"{service_code}") 

            #     # -------------------------------------------------------------------------------------
                
            #     cursor = connection.cursor()
            #     cursor.execute(f"""SELECT COUNT(*) FROM SYSTEM_SERVICE_ARGS WHERE SERVICE_CODE = '{service_code}'""")

            #     count_system_services_args = cursor.fetchone()[0]
            #     logger.log(f"Count SYSTEM_SERVICE_ARGS {count_system_services_args}")
            #     cursor.close()
            #     if count_system_services_args > 0:
            #         cursor = connection.cursor()
            #         delete_query = f"DELETE FROM SYSTEM_SERVICE_ARGS WHERE SERVICE_CODE = '{service_code}'"
            #         logger.log(f"Class Obj_Actions delete_query ::: {delete_query}")
            #         cursor.execute(delete_query)
            #         cursor.close()
            #         logger.log("Data deleted from SYSTEM_SERVICE_ARGS") 
                
            #     # --------------------------------

            #     cursor = connection.cursor()
            #     if con_type == 'Oracle':
            #         insert_query = """
            #             INSERT INTO SYSTEM_SERVICE_ARGS (
            #                 SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
            #                 ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
            #             ) VALUES (
            #                 :service_code, :line_no, :arg_name, :arg_mode, :descr, :arg_type, 
            #                 :arg_xfrm, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :arg_value
            #             )
            #         """
            #         values = {
            #             "service_code": service_code,
            #             "line_no": 1,
            #             "arg_name": "COMPONENT_TYPE",
            #             "arg_mode": "I",
            #             "descr": "",
            #             "arg_type": "S",
            #             "arg_xfrm": "",
            #             "chg_date": datetime.now().strftime('%d-%m-%Y'),
            #             "chg_user": "System",
            #             "chg_term": "System",
            #             "arg_value": "DB",
            #         }
            #         logger.log(f"\n--- Class Obj_Itemchange ---\n")
            #         logger.log(f"insert_query values :: {values}")
            #         cursor.execute(insert_query, values)
            #         logger.log(f"Successfully inserted row.")
            #     else:
            #         insert_query = """
            #             INSERT INTO SYSTEM_SERVICE_ARGS (
            #                 SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
            #                 ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
            #             ) VALUES (
            #                 %s, %s, %s, %s, %s, %s, 
            #                 %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s
            #             )
            #         """
            #         values = (
            #             service_code, 1, "COMPONENT_TYPE", "I", None, "S", 
            #             None, datetime.now().strftime('%d-%m-%Y'), "System", "System", "DB"
            #         )
            #         logger.log(f"\n--- Class Obj_Itemchange ---\n")
            #         logger.log(f"insert_query values :: {values}")
            #         cursor.execute(insert_query, values)
            #         logger.log(f"Successfully inserted row.")                                                                                                       
            #     cursor.close()

            #     cursor = connection.cursor()
            #     if con_type == 'Oracle':
            #         insert_query = """
            #             INSERT INTO SYSTEM_SERVICE_ARGS (
            #                 SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
            #                 ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
            #             ) VALUES (
            #                 :service_code, :line_no, :arg_name, :arg_mode, :descr, :arg_type, 
            #                 :arg_xfrm, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :arg_value
            #             )
            #         """
            #         values = {
            #             "service_code": service_code,
            #             "line_no": 2,
            #             "arg_name": "COMPONENT_NAME",
            #             "arg_mode": "I",
            #             "descr": "",  
            #             "arg_type": "S",
            #             "arg_xfrm": "",  
            #             "chg_date": datetime.now().strftime('%d-%m-%Y'),
            #             "chg_user": "System",
            #             "chg_term": "System",
            #             "arg_value": function_name
            #         }
            #         logger.log(f"\n--- Class Obj_Itemchange ---\n")
            #         logger.log(f"insert_query values :: {values}")
            #         cursor.execute(insert_query, values)
            #         logger.log(f"Successfully inserted row.")
            #     else:
            #         insert_query = """
            #             INSERT INTO SYSTEM_SERVICE_ARGS (
            #                 SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
            #                 ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
            #             ) VALUES (
            #                 %s, %s, %s, %s, %s, %s, 
            #                 %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s
            #             )
            #         """
            #         values = (
            #             service_code, 2, "COMPONENT_NAME", "I", None,  
            #             "S", None,  
            #             datetime.now().strftime('%d-%m-%Y'), "System", "System", function_name
            #         )
            #         logger.log(f"\n--- Class Obj_Itemchange ---\n")
            #         logger.log(f"insert_query values :: {values}")
            #         cursor.execute(insert_query, values)
            #         logger.log(f"Successfully inserted row.")
            #     cursor.close()

            #     # --------------------------------

            #     for index, args in enumerate(arg_list):
            #         args_line_no = str(index+3)
            #         cursor = connection.cursor()
            #         if con_type == 'Oracle':
            #             insert_query = """
            #                 INSERT INTO SYSTEM_SERVICE_ARGS (
            #                     SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
            #                     ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
            #                 ) VALUES (
            #                     :service_code, :line_no, :arg_name, :arg_mode, :descr, :arg_type, 
            #                     :arg_xfrm, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :arg_value
            #                 )
            #             """
            #             values = {
            #                 'service_code': service_code,
            #                 'line_no': args_line_no,
            #                 'arg_name': args.lower(),
            #                 'arg_mode': 'I',
            #                 'descr': '',
            #                 'arg_type': 'S',
            #                 'arg_xfrm': '',
            #                 'chg_date': datetime.now().strftime('%d-%m-%Y'),
            #                 'chg_user': 'System',
            #                 'chg_term': 'System',
            #                 'arg_value': ''
            #             }
            #             logger.log(f"\n--- Class Obj_Actions ---\n")
            #             logger.log(f"insert_query values :: {values}")
            #             cursor.execute(insert_query, values)
            #             logger.log(f"Successfully inserted row.")
            #         else:
            #             insert_query = """
            #                 INSERT INTO SYSTEM_SERVICE_ARGS (
            #                     SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
            #                     ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
            #                 ) VALUES (
            #                     %s, %s, %s, %s, %s, %s, 
            #                     %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s
            #                 )
            #             """
            #             values = (
            #                 service_code,
            #                 args_line_no,
            #                 args.lower(),
            #                 'I',
            #                 None,  
            #                 'S',
            #                 None,  
            #                 datetime.now().strftime('%d-%m-%Y'),
            #                 'System',
            #                 'System',
            #                 None   
            #             )
            #             logger.log(f"\n--- Class Obj_Actions ---\n")
            #             logger.log(f"insert_query values :: {values}")
            #             cursor.execute(insert_query, values)
            #             logger.log(f"Successfully inserted row.")
            #         cursor.close()
            #         logger.log("Data inserted from SYSTEM_SERVICE_ARGS")  
            #         logger.log(f"{service_code}") 

            #     # -------------------------------------------------------------------------------------

            #     if service_code_from_action_json.lower() == 'default': 
            #         logger.log("\nDefault Title")  
            #         logger.log(f"{title}") 

            #         cursor = connection.cursor()
            #         logger.log(f"Inside Obj_actions maxid")
            #         cursor = connection.cursor()
            #         max_queryy = f"""
            #             SELECT MAX(TO_NUMBER(RIGHTS_CHAR)) 
            #             FROM obj_actions 
            #             WHERE REGEXP_LIKE(RIGHTS_CHAR, '^[0-9]$') 
            #             AND OBJ_NAME = '{obj_name}' 
            #             AND FORM_NO = '{form_no}'
            #         """
            #         logger.log(f"rights_char max_queryy ::: {max_queryy}")
            #         cursor.execute(max_queryy)
            #         rights_char_val = cursor.fetchone()[0]
            #         logger.log(f"rights_char_from_DB ::: {rights_char_val}")
            #         cursor.close()

            #         service_handler = 2
            #         rights_char = 0
            #         logger.log(f"rights_char_val ::: {rights_char_val}")
            #         if rights_char_val != None:
            #             rights_char = int(rights_char_val) + 1
            #         else:
            #             rights_char = int(rights_char) + 1
            #         logger.log(f"actions rights_char ::: {rights_char}")

            #     # -------------------------------------------------------------------------------------

            #     cursor = connection.cursor()
            #     if con_type == 'Oracle':
            #         update_query = """
            #             UPDATE obj_actions SET
            #             IMAGE = :image, DESCRIPTION = :description, SERVICE_CODE = :service_code,
            #             INTERACTIVE = :interactive, RIGHTS_CHAR = :rights_char, TITLE = :title,
            #             FORM_NO = :form_no, SERVICE_HANDLER = :service_handler, PLACEMENT = :placement,
            #             ACTION_TYPE = :action_type, TRAN_TYPE = :tran_type, 
            #             CHG_DATE = TO_DATE(:chg_date, 'DD-MM-YYYY'), CHG_TERM = :chg_term, CHG_USER = :chg_user,
            #             IS_CONFIRMATION_REQ = :is_confirmation_req, SEP_DUTY_OPT = :sep_duty_opt,
            #             RE_AUTH_OPT = :re_auth_opt, SHOW_IN_PANEL = :show_in_panel,
            #             PAGE_CONTEXT = :page_context, TYPE = :type, ACTION_ARG = :action_arg,
            #             SWIPE_POSITION = :swipe_position, MULTI_ROW_OPT = :multi_row_opt,
            #             ACTION_ID = :action_id, DEF_NODATA = :def_nodata, 
            #             IN_PROC_INTRUPT = :in_proc_intrupt, ESTIMATED_TIME = :estimated_time,
            #             ACTION_GROUP = :action_group, DISPLAY_OPT = :display_opt,
            #             DISPLAY_MODE = :display_mode, SHOW_CONFIRM = :show_confirm,
            #             REC_SPECIFIC = :rec_specific
            #             WHERE OBJ_NAME = :obj_name AND LINE_NO = :line_no
            #         """
            #         values = {
            #             "obj_name": obj_name, "line_no": line_no, "image": image, "description": description, "service_code": str(service_code),
            #             "interactive": interactive, "rights_char": rights_char, "title": title, "form_no": form_no, "service_handler": service_handler,
            #             "placement": placement, "action_type": action_type, "tran_type": tran_type, "chg_date": chg_date, "chg_term": chg_term,
            #             "chg_user": chg_user, "is_confirmation_req": is_confirmation_req, "sep_duty_opt": sep_duty_opt, "re_auth_opt": re_auth_opt,
            #             "show_in_panel": show_in_panel, "page_context": page_context, "type": type_, "action_arg": action_arg, "swipe_position": swipe_position,
            #             "multi_row_opt": multi_row_opt, "action_id": action_id, "def_nodata": def_nodata, "in_proc_intrupt": in_proc_intrupt, 
            #             "estimated_time": estimated_time, "action_group": action_group, "display_opt": display_opt, "display_mode": display_mode,
            #             "show_confirm": show_confirm, "rec_specific": rec_specific
            #         }
            #         logger.log(f"\n--- Class Obj_Actions ---\n")
            #         logger.log(f"update_query values :: {values}")
            #         cursor.execute(update_query, values)
            #         logger.log(f"Successfully updated row.")
            #     else:
            #         update_query = """
            #             UPDATE obj_actions SET
            #                 IMAGE = %s, DESCRIPTION = %s, SERVICE_CODE = %s,
            #                 INTERACTIVE = %s, RIGHTS_CHAR = %s, TITLE = %s,
            #                 FORM_NO = %s, SERVICE_HANDLER = %s, PLACEMENT = %s,
            #                 ACTION_TYPE = %s, TRAN_TYPE = %s, 
            #                 CHG_DATE = TO_DATE(%s, 'DD-MM-YYYY'), CHG_TERM = %s, CHG_USER = %s,
            #                 IS_CONFIRMATION_REQ = %s, SEP_DUTY_OPT = %s,
            #                 RE_AUTH_OPT = %s, SHOW_IN_PANEL = %s,
            #                 PAGE_CONTEXT = %s, TYPE = %s, ACTION_ARG = %s,
            #                 SWIPE_POSITION = %s, MULTI_ROW_OPT = %s,
            #                 ACTION_ID = %s, DEF_NODATA = %s, 
            #                 IN_PROC_INTRUPT = %s, ESTIMATED_TIME = %s,
            #                 ACTION_GROUP = %s, DISPLAY_OPT = %s,
            #                 DISPLAY_MODE = %s, SHOW_CONFIRM = %s,
            #                 REC_SPECIFIC = %s
            #             WHERE OBJ_NAME = %s AND LINE_NO = %s
            #         """
            #         values = (
            #             image, description, str(service_code),
            #             interactive, rights_char, title, form_no, service_handler,
            #             placement, action_type, tran_type, chg_date, chg_term,
            #             chg_user, is_confirmation_req, sep_duty_opt, re_auth_opt,
            #             show_in_panel, page_context, type_, action_arg, swipe_position,
            #             multi_row_opt, action_id, def_nodata, in_proc_intrupt,
            #             estimated_time, action_group, display_opt, display_mode,
            #             show_confirm, rec_specific, obj_name, line_no
            #         )
            #         logger.log(f"\n--- Class Obj_Actions ---\n")
            #         logger.log(f"update_query values :: {values}")
            #         cursor.execute(update_query, values)
            #         logger.log(f"Successfully updated row.")            
            #     cursor.close()
            # else:

            event_code = service_code
            
            if title not in ['Edit', 'Add', 'View']:
                cursor = connection.cursor()
                deployment_log(f"SYSTEM_EVENTS table select query ::: SELECT COUNT(*) FROM SYSTEM_EVENTS WHERE OBJ_NAME = '{obj_name}' and EVENT_CODE = '{event_code}'")
                cursor.execute(f"""
                    SELECT COUNT(*) FROM SYSTEM_EVENTS 
                    WHERE OBJ_NAME = '{obj_name}' and EVENT_CODE = '{event_code}'
                """)

                count_system_events = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_EVENTS {count_system_events}")
                deployment_log(f"SYSTEM_EVENTS table select query result ::: {count_system_events}")
                cursor.close()
                if count_system_events > 0:
                    cursor = connection.cursor()
                    delete_query = f"""
                        DELETE FROM SYSTEM_EVENTS 
                        WHERE OBJ_NAME = '{obj_name}' and EVENT_CODE = '{event_code}'
                    """
                    logger.log(f"Class Obj_Actions delete_query ::: {delete_query}")
                    deployment_log(f"SYSTEM_EVENTS table delete query ::: {delete_query}")
                    cursor.execute(delete_query)

                    cursor.close()
                    logger.log("Data deleted from SYSTEM_EVENTS") 
                    deployment_log("Data deleted from SYSTEM_EVENTS") 

                cursor = connection.cursor()
                if con_type == 'Oracle':
                    insert_query = """
                        INSERT INTO SYSTEM_EVENTS (
                            OBJ_NAME, EVENT_CODE, EVENT_CONTEXT, SERVICE_CODE, METHOD_RULE, OVERWRITE_CORE, 
                            CHG_DATE, CHG_USER, CHG_TERM, RESULT_HANDLE, COMP_TYPE, COMP_NAME, COMM_FORMAT, FIELD_NAME
                        ) VALUES (
                            :obj_name, :event_code, :event_context, :service_code, :method_rule, :overwrite_core, 
                            TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :result_handle, :comp_type, 
                            :comp_name, :comm_format, :field_name
                        )
                    """
                    values = {
                        'obj_name': obj_name,
                        'event_code': event_code,
                        'event_context': self.event_context,
                        'service_code': service_code,
                        'method_rule': None,
                        'overwrite_core': '0',
                        'chg_date': datetime.now().strftime('%d-%m-%y'),  
                        'chg_user': 'System',
                        'chg_term': 'System',
                        'result_handle': '2',
                        'comp_type': 'DB',
                        'comp_name': function_name,
                        'comm_format': None,
                        'field_name': ''
                    }
                    logger.log(f"\n--- Class Obj_Actions ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_EVENTS table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"SYSTEM_EVENTS table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_EVENTS table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO SYSTEM_EVENTS (
                            OBJ_NAME, EVENT_CODE, EVENT_CONTEXT, SERVICE_CODE, METHOD_RULE, OVERWRITE_CORE, 
                            CHG_DATE, CHG_USER, CHG_TERM, RESULT_HANDLE, COMP_TYPE, COMP_NAME, COMM_FORMAT, FIELD_NAME
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, 
                            TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s, %s, 
                            %s, %s, %s
                        )
                    """
                    values = (
                        obj_name,
                        event_code,
                        self.event_context,
                        service_code,
                        None,  
                        '0',
                        datetime.now().strftime('%d-%m-%Y'),  
                        'System',
                        'System',
                        '2',
                        'DB',
                        function_name,
                        None, 
                        ''  
                    )
                    logger.log(f"\n--- Class Obj_Actions ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_EVENTS table insert query for Other database ::: {insert_query}")
                    deployment_log(f"SYSTEM_EVENTS table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_EVENTS table for Other database.")
                cursor.close()
                logger.log("Data inserted from SYSTEM_EVENTS")  
                logger.log(f"{service_code}") 

                # -------------------------------------------------------------------------------------

                cursor = connection.cursor()
                deployment_log(f"SYSTEM_EVENT_SERVICES table select query ::: SELECT COUNT(*) FROM SYSTEM_EVENT_SERVICES WHERE SERVICE_CODE = '{service_code}'")
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM SYSTEM_EVENT_SERVICES 
                    WHERE SERVICE_CODE = '{service_code}'
                """)
                count_system_services = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_EVENT_SERVICES {count_system_services}")
                deployment_log(f"SYSTEM_EVENT_SERVICES table select query result ::: {count_system_services}")
                cursor.close()
                if count_system_services > 0:
                    cursor = connection.cursor()
                    delete_query = f"DELETE FROM SYSTEM_EVENT_SERVICES WHERE SERVICE_CODE = '{service_code}'"
                    logger.log(f"Class Obj_Actions delete_query ::: {delete_query}")
                    deployment_log(f"SYSTEM_EVENT_SERVICES table delete query ::: {delete_query}")
                    cursor.execute(delete_query)
                    cursor.close()
                    logger.log("Data deleted from SYSTEM_EVENT_SERVICES") 
                    deployment_log("Data deleted from SYSTEM_EVENT_SERVICES") 

                cursor = connection.cursor()
                if con_type == 'Oracle':
                    insert_query = """
                        INSERT INTO SYSTEM_EVENT_SERVICES (
                            SERVICE_CODE, SERVICE_DESCR, SERVICE_URI, SERVICE_PROVIDER, METHOD_NAME, 
                            RETURN_VALUE, RETURN_TYPE, RETURN_DESCR, RETURN_XFRM, CHG_DATE, 
                            CHG_USER, CHG_TERM, SERVICE_NAMESPACE, RES_ELEM, SOAP_ACTION
                        ) VALUES (
                            :service_code, :service_descr, :service_uri, :service_provider, :method_name, 
                            :return_value, :return_type, :return_descr, :return_xfrm, 
                            TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, 
                            :service_namespace, :res_elem, :soap_action
                        )
                    """
                    values = {
                        'service_code': service_code,
                        'service_descr': function_desc,
                        'service_uri': function_name,
                        'service_provider': '',
                        'method_name': ' ',
                        'return_value': '',
                        'return_type': '',
                        'return_descr': '',
                        'return_xfrm': '',
                        'chg_date': datetime.now().strftime('%d-%m-%Y'),  
                        'chg_user': 'System',
                        'chg_term': 'System',
                        'service_namespace': '',
                        'res_elem': '',
                        'soap_action': ''
                    }
                    logger.log(f"\n--- Class Obj_Actions ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_EVENT_SERVICES table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"SYSTEM_EVENT_SERVICES table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_EVENT_SERVICES table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO SYSTEM_EVENT_SERVICES (
                            SERVICE_CODE, SERVICE_DESCR, SERVICE_URI, SERVICE_PROVIDER, METHOD_NAME, 
                            RETURN_VALUE, RETURN_TYPE, RETURN_DESCR, RETURN_XFRM, CHG_DATE, 
                            CHG_USER, CHG_TERM, SERVICE_NAMESPACE, RES_ELEM, SOAP_ACTION
                        ) VALUES (
                            %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, 
                            TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, 
                            %s, %s, %s
                        )
                    """
                    values = (
                        service_code,
                        function_desc,
                        function_name,
                        None,  
                        ' ',  
                        None,
                        None,
                        None,
                        None,
                        datetime.now().strftime('%d-%m-%Y'),  
                        'System',
                        'System',
                        None,
                        None,
                        None
                    )
                    logger.log(f"\n--- Class Obj_Actions ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_EVENT_SERVICES table insert query for Other database ::: {insert_query}")
                    deployment_log(f"SYSTEM_EVENT_SERVICES table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_EVENT_SERVICES table for Other database.")
                cursor.close()
                logger.log("Data inserted from SYSTEM_EVENT_SERVICES") 
                logger.log(f"{service_code}") 

                # -------------------------------------------------------------------------------------
                
                cursor = connection.cursor()
                deployment_log(f"SYSTEM_SERVICE_ARGS table select query ::: SELECT COUNT(*) FROM SYSTEM_SERVICE_ARGS WHERE SERVICE_CODE = '{service_code}'")
                cursor.execute(f"""SELECT COUNT(*) FROM SYSTEM_SERVICE_ARGS WHERE SERVICE_CODE = '{service_code}'""")

                count_system_services_args = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_SERVICE_ARGS {count_system_services_args}")
                deployment_log(f"SYSTEM_SERVICE_ARGS table select query result ::: {count_system_services_args}")
                cursor.close()
                if count_system_services_args > 0:
                    cursor = connection.cursor()
                    delete_query = f"DELETE FROM SYSTEM_SERVICE_ARGS WHERE SERVICE_CODE = '{service_code}'"
                    logger.log(f"Class Obj_Actions delete_query ::: {delete_query}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table delete query ::: {delete_query}")
                    cursor.execute(delete_query)
                    cursor.close()
                    logger.log("Data deleted from SYSTEM_SERVICE_ARGS") 
                    deployment_log("Data deleted from SYSTEM_SERVICE_ARGS") 
                    
                # --------------------------------

                cursor = connection.cursor()
                if con_type == 'Oracle':
                    insert_query = """
                        INSERT INTO SYSTEM_SERVICE_ARGS (
                            SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
                            ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
                        ) VALUES (
                            :service_code, :line_no, :arg_name, :arg_mode, :descr, :arg_type, 
                            :arg_xfrm, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :arg_value
                        )
                    """
                    values = {
                        "service_code": service_code,
                        "line_no": 1,
                        "arg_name": "COMPONENT_TYPE",
                        "arg_mode": "I",
                        "descr": "",
                        "arg_type": "S",
                        "arg_xfrm": "",
                        "chg_date": datetime.now().strftime('%d-%m-%Y'),
                        "chg_user": "System",
                        "chg_term": "System",
                        "arg_value": "DB",
                    }
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_SERVICE_ARGS table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO SYSTEM_SERVICE_ARGS (
                            SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
                            ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, 
                            %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s
                        )
                    """
                    values = (
                        service_code, 1, "COMPONENT_TYPE", "I", None, "S", 
                        None, datetime.now().strftime('%d-%m-%Y'), "System", "System", "DB"
                    )
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query for Other database ::: {insert_query}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")  
                    deployment_log(f"Data inserted successfully in SYSTEM_SERVICE_ARGS table for Other database.")                                                                                                     
                cursor.close()

                cursor = connection.cursor()
                if con_type == 'Oracle':
                    insert_query = """
                        INSERT INTO SYSTEM_SERVICE_ARGS (
                            SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
                            ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
                        ) VALUES (
                            :service_code, :line_no, :arg_name, :arg_mode, :descr, :arg_type, 
                            :arg_xfrm, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :arg_value
                        )
                    """
                    values = {
                        "service_code": service_code,
                        "line_no": 2,
                        "arg_name": "COMPONENT_NAME",
                        "arg_mode": "I",
                        "descr": "",  
                        "arg_type": "S",
                        "arg_xfrm": "",  
                        "chg_date": datetime.now().strftime('%d-%m-%Y'),
                        "chg_user": "System",
                        "chg_term": "System",
                        "arg_value": function_name
                    }
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_SERVICE_ARGS table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO SYSTEM_SERVICE_ARGS (
                            SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
                            ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, 
                            %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s
                        )
                    """
                    values = (
                        service_code, 2, "COMPONENT_NAME", "I", None,  
                        "S", None,  
                        datetime.now().strftime('%d-%m-%Y'), "System", "System", function_name
                    )
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query for Other database ::: {insert_query}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_SERVICE_ARGS table for Other database.")
                cursor.close()

                # --------------------------------

                for index, args in enumerate(arg_list):
                    args_line_no = str(index+3)
                    cursor = connection.cursor()
                    if con_type == 'Oracle':
                        insert_query = """
                            INSERT INTO SYSTEM_SERVICE_ARGS (
                                SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
                                ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
                            ) VALUES (
                                :service_code, :line_no, :arg_name, :arg_mode, :descr, :arg_type, 
                                :arg_xfrm, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :arg_value
                            )
                        """
                        values = {
                            'service_code': service_code,
                            'line_no': args_line_no,
                            'arg_name': args.lower(),
                            'arg_mode': 'I',
                            'descr': '',
                            'arg_type': 'S',
                            'arg_xfrm': '',
                            'chg_date': datetime.now().strftime('%d-%m-%Y'),
                            'chg_user': 'System',
                            'chg_term': 'System',
                            'arg_value': ''
                        }
                        logger.log(f"\n--- Class Obj_Actions ---\n")
                        logger.log(f"insert_query values :: {values}")
                        deployment_log(f"SYSTEM_SERVICE_ARGS table insert query for Oracle database ::: {insert_query}")
                        deployment_log(f"SYSTEM_SERVICE_ARGS table insert query values for Oracle database ::: {values}")
                        cursor.execute(insert_query, values)
                        logger.log(f"Successfully inserted row.")
                        deployment_log(f"Data inserted successfully in SYSTEM_SERVICE_ARGS table for Oracle database.")
                    else:
                        insert_query = """
                            INSERT INTO SYSTEM_SERVICE_ARGS (
                                SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
                                ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, 
                                %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s
                            )
                        """
                        values = (
                            service_code,
                            args_line_no,
                            args.lower(),
                            'I',
                            None,  
                            'S',
                            None,  
                            datetime.now().strftime('%d-%m-%Y'),
                            'System',
                            'System',
                            None   
                        )
                        logger.log(f"\n--- Class Obj_Actions ---\n")
                        logger.log(f"insert_query values :: {values}")
                        deployment_log(f"SYSTEM_SERVICE_ARGS table insert query for Other database ::: {insert_query}")
                        deployment_log(f"SYSTEM_SERVICE_ARGS table insert query values for Other database ::: {values}")
                        cursor.execute(insert_query, values)
                        logger.log(f"Successfully inserted row.")
                        deployment_log(f"Data inserted successfully in SYSTEM_SERVICE_ARGS table for Other database.")
                    cursor.close()
                    logger.log("Data inserted from SYSTEM_SERVICE_ARGS")  
                    logger.log(f"{service_code}")  

            # -------------------------------------------------------------------------------------

            if service_code_from_action_json.lower() == 'default': 
                logger.log("\nDefault Title")  
                logger.log(f"{title}") 
                deployment_log(f"Default Title ::: {title}")

                cursor = connection.cursor()
                logger.log(f"Inside Obj_actions maxid")
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    max_queryy = f"""
                        SELECT MAX(TO_NUMBER(RIGHTS_CHAR)) 
                        FROM obj_actions 
                        WHERE REGEXP_LIKE(RIGHTS_CHAR, '^[0-9]$') 
                        AND OBJ_NAME = '{obj_name}' 
                        AND FORM_NO = '{form_no}'
                    """
                else:             
                    max_queryy = f"""
                        SELECT MAX(CAST(RIGHTS_CHAR AS INTEGER))
                        FROM obj_actions 
                        WHERE REGEXP_LIKE(RIGHTS_CHAR, '^[0-9]$') 
                        AND OBJ_NAME = '{obj_name}' 
                        AND FORM_NO = '{form_no}'
                    """
                deployment_log(f"OBJ_ACTIONS table select max query ::: {max_queryy}")
                cursor.execute(max_queryy)
                rights_char_val = cursor.fetchone()[0]
                logger.log(f"rights_char_from_DB ::: {rights_char_val}")
                deployment_log(f"OBJ_ACTIONS table select max query result ::: {rights_char_val}")
                cursor.close()

                service_handler = 2
                rights_char = 0
                logger.log(f"rights_char_val ::: {rights_char_val}")
                if rights_char_val != None:
                    rights_char = int(rights_char_val) + 1
                else:
                    rights_char = int(rights_char) + 1
                logger.log(f"actions rights_char ::: {rights_char}")
                deployment_log(f"OBJ_ACTIONS final rights_char ::: {rights_char}")

            # --------------------------------

            cursor = connection.cursor()
            if con_type == 'Oracle':
                insert_query = """
                    INSERT INTO obj_actions (
                    OBJ_NAME, LINE_NO, IMAGE, DESCRIPTION, SERVICE_CODE, INTERACTIVE,
                    RIGHTS_CHAR, TITLE, FORM_NO, SERVICE_HANDLER, PLACEMENT, ACTION_TYPE,
                    TRAN_TYPE, CHG_DATE, CHG_TERM, CHG_USER, IS_CONFIRMATION_REQ,
                    SEP_DUTY_OPT, RE_AUTH_OPT, SHOW_IN_PANEL, PAGE_CONTEXT, TYPE,
                    ACTION_ARG, SWIPE_POSITION, MULTI_ROW_OPT, ACTION_ID, DEF_NODATA,
                    IN_PROC_INTRUPT, ESTIMATED_TIME, ACTION_GROUP, DISPLAY_OPT,
                    DISPLAY_MODE, SHOW_CONFIRM, REC_SPECIFIC
                    ) VALUES (
                    :obj_name, :line_no, :image, :description, :service_code, :interactive,
                    :rights_char, :title, :form_no, :service_handler, :placement, :action_type,
                    :tran_type, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_term, :chg_user, :is_confirmation_req,
                    :sep_duty_opt, :re_auth_opt, :show_in_panel, :page_context, :type,
                    :action_arg, :swipe_position, :multi_row_opt, :action_id, :def_nodata,
                    :in_proc_intrupt, :estimated_time, :action_group, :display_opt,
                    :display_mode, :show_confirm, :rec_specific)
                """
                values = {
                    'obj_name': obj_name, 'line_no': line_no, 'image': image, 'description': description, 'service_code': str(service_code),
                    'interactive': interactive, 'rights_char': rights_char, 'title': title, 'form_no': form_no, 'service_handler': service_handler,
                    'placement': placement, 'action_type': action_type, 'tran_type': tran_type, 'chg_date': chg_date, 'chg_term': chg_term,
                    'chg_user': chg_user, 'is_confirmation_req': is_confirmation_req, 'sep_duty_opt': sep_duty_opt, 're_auth_opt': re_auth_opt,
                    'show_in_panel': show_in_panel, 'page_context': page_context, 'type': type_, 'action_arg': action_arg, 'swipe_position': swipe_position,
                    'multi_row_opt': multi_row_opt, 'action_id': action_id, 'def_nodata': def_nodata, 'in_proc_intrupt': in_proc_intrupt, 
                    'estimated_time': estimated_time, 'action_group': action_group, 'display_opt': display_opt, 'display_mode': display_mode,
                    'show_confirm': show_confirm, 'rec_specific': rec_specific
                }
                logger.log(f"\n--- Class Obj_Actions ---\n")
                logger.log(f"insert_query values :: {values}")
                deployment_log(f"OBJ_ACTIONS table insert query for Oracle database ::: {insert_query}")
                deployment_log(f"OBJ_ACTIONS table insert query values for Oracle database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in OBJ_ACTIONS table for Oracle database.")
            else:
                insert_query = """
                    INSERT INTO obj_actions (
                        OBJ_NAME, LINE_NO, IMAGE, DESCRIPTION, SERVICE_CODE, INTERACTIVE,
                        RIGHTS_CHAR, TITLE, FORM_NO, SERVICE_HANDLER, PLACEMENT, ACTION_TYPE,
                        TRAN_TYPE, CHG_DATE, CHG_TERM, CHG_USER, IS_CONFIRMATION_REQ,
                        SEP_DUTY_OPT, RE_AUTH_OPT, SHOW_IN_PANEL, PAGE_CONTEXT, TYPE,
                        ACTION_ARG, SWIPE_POSITION, MULTI_ROW_OPT, ACTION_ID, DEF_NODATA,
                        IN_PROC_INTRUPT, ESTIMATED_TIME, ACTION_GROUP, DISPLAY_OPT,
                        DISPLAY_MODE, SHOW_CONFIRM, REC_SPECIFIC
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, 
                        %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s,
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, 
                        %s, %s
                    )
                """
                values = (
                    obj_name, line_no, image, description, str(service_code),
                    interactive, rights_char, title, form_no, service_handler,
                    placement, action_type, tran_type, chg_date, chg_term,
                    chg_user, is_confirmation_req, sep_duty_opt, re_auth_opt,
                    show_in_panel, page_context, type_, action_arg, swipe_position,
                    multi_row_opt, action_id, def_nodata, in_proc_intrupt,
                    estimated_time, action_group, display_opt, display_mode,
                    show_confirm, rec_specific
                )
                logger.log(f"\n--- Class Obj_Actions ---\n")
                logger.log(f"insert_query values :: {values}")
                deployment_log(f"OBJ_ACTIONS table insert query for Other database ::: {insert_query}")
                deployment_log(f"OBJ_ACTIONS table insert query values for Other database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in OBJ_ACTIONS table for Other database.")
            cursor.close()

    def process_data(self, conn, sql_models_data, schema_name, con_type, obj_name):
        logger.log(f"Start of Obj_Actions Class")
        deployment_log(f"\n--------------------------------- Start of Obj_Actions Class -------------------------------------\n")

        # --------------------------------

        cursor = conn.cursor()
        deployment_log(f"OBJ_ACTIONS table select query ::: SELECT COUNT(*) FROM obj_actions WHERE OBJ_NAME = '{obj_name}'")
        cursor.execute(f"""SELECT COUNT(*) FROM obj_actions WHERE OBJ_NAME = '{obj_name}'""")

        count_obj_actions = cursor.fetchone()[0]
        logger.log(f"Count obj_actions {count_obj_actions}")
        deployment_log(f"OBJ_ACTIONS table select query result :::  {count_obj_actions}")
        cursor.close()
        if count_obj_actions > 0:
            cursor = conn.cursor()
            delete_query = f"DELETE FROM obj_actions WHERE OBJ_NAME = '{obj_name}'"
            logger.log(f"Class Obj_Actions delete_query ::: {delete_query}")
            deployment_log(f"OBJ_ACTIONS table delete query :::  {delete_query}")
            cursor.execute(delete_query)
            cursor.close()
            logger.log("Data deleted from obj_actions") 
            deployment_log("Data deleted from OBJ_ACTIONS") 

        # --------------------------------

        self.sql_models = sql_models_data
        for sql_model in self.sql_models:
            if "sql_model" in sql_model and "action" in sql_model['sql_model']:
                for actions in sql_model['sql_model']['action']:
                    if actions:
                        if ':' in actions['actual_func']:
                            logger.log(f"Actions: {actions['actual_func'].split(':')[1]}")
                            pattern = r"\w+\(['\"](.*?)['\"],\s*['\"](.*?)['\"]\)"
                            matches = re.findall(pattern, actions['actual_func'].split(':')[1])

                            sql_function_name = matches[0][0]
                            sql_desc = matches[0][1]
                            logger.log(f"Inside sql_function_name: {sql_function_name}")
                            logger.log(f"Inside sql_desc: {sql_desc}")
                            deployment_log(f"OBJ_ACTIONS sql_function_name ::: {sql_function_name}")
                            deployment_log(f"OBJ_ACTIONS sql_desc ::: {sql_desc}")
                            
                            actions["function_name"] = sql_function_name
                            actions["function_desc"] = sql_desc

                            cursor = conn.cursor()
                            if con_type == 'Postgress':
                                sql_function_name = sql_function_name.lower()
                                schema_name = schema_name.lower()
                            else:
                                sql_function_name = sql_function_name.upper()
                                schema_name = schema_name.upper()
                            if con_type == 'Oracle':
                                queryy = f"""
                                    SELECT ARGUMENT_NAME FROM ALL_ARGUMENTS 
                                    WHERE OBJECT_NAME = '{sql_function_name}'
                                    AND OWNER = '{schema_name}'
                                    AND PACKAGE_NAME IS NULL  
                                    ORDER BY POSITION
                                """
                                logger.log(f"\n--- Class Obj_Actions ---\n")
                                logger.log(f"{queryy}")
                                deployment_log(f"ALL_ARGUMENTS table select query for Oracle database ::: {queryy}")
                                cursor.execute(queryy)
                                result = cursor.fetchall()
                                result = result if result != [] else None
                                deployment_log(f"ALL_ARGUMENTS table select query result for Oracle database ::: {result}")
                                logger.log(f"\n result value:::\t{result}")
                                cursor.close()

                                if result != None:
                                    arg_list = []
                                    for i in result:             
                                        first_non_empty = i[0]                        
                                        logger.log(f"\n first_non_empty value:::\t{first_non_empty}") 
                                        if first_non_empty is not None:
                                            if first_non_empty.startswith("p_") or first_non_empty.startswith("P_"):
                                                arg_list.append(first_non_empty[2:].upper())
                                            else:
                                                arg_list.append(first_non_empty.upper())
                                    logger.log(f"\n Obj_Actions sql_input:::\t{arg_list}")
                                    deployment_log(f"OBJ_ACTIONS sql_input ::: {arg_list}")

                                    actions["arg_list"] = arg_list
                                else:
                                    deployment_log(f"Function {sql_function_name} definition is not found, so please execute the function and then upload the model json.")
                                    raise Exception(f"Function {sql_function_name} definition is not found, so please execute the function and then upload the model json.")
                            else:
                                queryy = f"""
                                    SELECT pg_get_function_arguments(p.oid) AS parameters
                                    FROM pg_proc p
                                    JOIN pg_namespace n ON p.pronamespace = n.oid
                                    WHERE p.proname = '{sql_function_name}'  
                                    AND n.nspname = '{schema_name}'
                                """
                                logger.log(f"\n--- Class Obj_Actions ---\n")
                                logger.log(f"{queryy}")
                                deployment_log(f"PG_PROC table select query for Other database ::: {queryy}")
                                cursor.execute(queryy)
                                result = cursor.fetchone()
                                result = result[0] if result is not None else None
                                logger.log(f"\n result value:::\t{result}")
                                deployment_log(f"PG_PROC table select query result for Other database ::: {result}")
                                cursor.close()

                                if result != None:
                                    arglst = result.split(',')
                                    arg_list = []
                                    for i in arglst:             
                                        split_res = i.split(' ')  
                                        first_non_empty = next((item for item in split_res if item), None)                                
                                        logger.log(f"\n first_non_empty value:::\t{first_non_empty}")
                                        if first_non_empty.startswith("p_") or first_non_empty.startswith("P_"):
                                            arg_list.append(first_non_empty[2:].upper())
                                        else:
                                            arg_list.append(first_non_empty.upper())
                                    logger.log(f"\n Obj_Actions sql_input:::\t{arg_list}")
                                    deployment_log(f"OBJ_ACTIONS sql_input ::: {arg_list}")

                                    actions["arg_list"] = arg_list
                                else:
                                    deployment_log(f"Function {sql_function_name} definition is not found, so please execute the function and then upload the model json.")
                                    raise Exception(f"Function {sql_function_name} definition is not found, so please execute the function and then upload the model json.")
                        
                        logger.log(f"actions ::: {actions}")
                        self.insert_or_update_actions(actions, conn, con_type)
        logger.log(f"End of Obj_Actions Class")
        deployment_log(f"End of ITM2MENU Class")
