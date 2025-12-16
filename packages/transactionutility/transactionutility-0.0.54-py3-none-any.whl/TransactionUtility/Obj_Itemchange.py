import cx_Oracle
import loggerutility as logger
import json
from datetime import datetime
import re
from loggerutility import deployment_log

class Obj_Itemchange:
    
    sql_models = []
        
    def is_valid_json(self, data):
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False

    def check_or_update_obj_itemchange(self, item_change,connection, con_type):

        required_keys = ['obj_name', 'form_no', 'field_name']
        missing_keys = [key for key in required_keys if key not in item_change]

        if missing_keys:
            deployment_log(f"Missing required keys for OBJ_ITEMCHANGE table: {', '.join(missing_keys)}")
            raise KeyError(f"Missing required keys for obj_itemchange table: {', '.join(missing_keys)}")
        else:
            obj_name = item_change.get('obj_name', '') or None
            form_no = item_change.get('form_no', '') or None
            field_name = item_change.get('field_name', '') or None
            mandatory = item_change.get('mandatory_server', '') or None
            exec_at = item_change.get('exec_at', '') or None
            js_arg = item_change.get('js_arg', '') or None
            arg_list = item_change.get('arg_list', [])
            function_name = item_change.get('function_name', '') or None
            function_desc = item_change.get('function_desc', '') or None
        
            cursor = connection.cursor()
            queryy = f"""
                SELECT COUNT(*) FROM obj_itemchange 
                WHERE OBJ_NAME = '{obj_name}'
                AND FORM_NO =  '{form_no}'
                AND FIELD_NAME =  '{field_name.lower()}'
            """
            logger.log(f"\n--- Class Obj_Itemchange ---\n")
            logger.log(f"{queryy}")
            deployment_log(f"OBJ_ITEMCHANGE table select query ::: {queryy}")
            cursor.execute(queryy)
            count = cursor.fetchone()[0]
            deployment_log(f"OBJ_ITEMCHANGE table select query result ::: {count}")
            cursor.close()

            cursor = connection.cursor()
            queryy = f"""
               SELECT MAX(CAST(EVENT_CONTEXT AS NUMERIC)) AS EVENT_CONTEXT
               FROM SYSTEM_EVENTS 
               WHERE OBJ_NAME = '{obj_name}' 
               AND EVENT_CODE = 'post_item_change'
            """
            logger.log(f"\n--- Class Obj_Itemchange ---\n")
            logger.log(f"{queryy}")
            deployment_log(f"SYSTEM_EVENTS table EVENT_CONTEXT select query ::: {queryy}")
            cursor.execute(queryy)
            event_context_val = cursor.fetchone()[0]
            deployment_log(f"SYSTEM_EVENTS table EVENT_CONTEXT select query result ::: {event_context_val}")
            cursor.close()

            event_context = 0
            logger.log(f"event_context_val ::: {event_context_val}")
            deployment_log(f"event_context_val ::: {event_context_val}")
            if event_context_val != None:
                event_context = int(event_context_val) + 1
            else:
                event_context = int(event_context) + 1
            logger.log(f"event_context ::: {event_context}")
            deployment_log(f"event_context ::: {event_context}")

            if count > 0:

                service_code = f'poic_{obj_name}_{field_name}'
                logger.log(f"obj_item_changed obj_name :: {obj_name}")
                logger.log(f"obj_item_changed service_code :: {service_code}")
                deployment_log(f"obj_item_changed obj_name :: {obj_name}")
                deployment_log(f"obj_item_changed service_code :: {service_code}")

                cursor = connection.cursor()
                deployment_log(f"SYSTEM_EVENTS table select query ::: SELECT COUNT(*) FROM SYSTEM_EVENTS WHERE OBJ_NAME = '{obj_name}' AND EVENT_CODE = 'post_item_change' AND FIELD_NAME = '{field_name.lower()}'")
                cursor.execute(f"""
                    SELECT COUNT(*) FROM SYSTEM_EVENTS 
                    WHERE OBJ_NAME = '{obj_name}' 
                    AND EVENT_CODE = 'post_item_change' 
                    AND FIELD_NAME = '{field_name.lower()}'
                """)                
                count_system_events = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_EVENTS {count_system_events}")
                deployment_log(f"SYSTEM_EVENTS table select query result::: {count_system_events}")
                cursor.close()
                if count_system_events > 0:
                    cursor = connection.cursor()
                    delete_query = f"""
                        DELETE FROM SYSTEM_EVENTS 
                        WHERE OBJ_NAME = '{obj_name}' 
                        AND EVENT_CODE = 'post_item_change' 
                        AND FIELD_NAME = '{field_name.lower()}'
                    """
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"{delete_query}")
                    deployment_log(f"SYSTEM_EVENTS table delete query :::  {delete_query}")
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
                        'event_code': 'post_item_change',
                        'event_context': event_context,
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
                        'field_name': field_name.lower()
                    }
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
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
                            TO_DATE( %s, 'DD-MM-YYYY'), %s, %s, %s, %s, %s, %s, %s
                        )
                    """
                    values = (
                        obj_name,
                        'post_item_change',
                        event_context,
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
                        field_name.lower()
                    )
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_EVENTS table insert query for Other database ::: {insert_query}")
                    deployment_log(f"SYSTEM_EVENTS table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_EVENTS table for Other database.")
                cursor.close()
                logger.log("Data inserted from SYSTEM_EVENTS") 

                # -------------------------------------------------------------------------------------

                cursor = connection.cursor()
                select_query = f"SELECT COUNT(*) FROM SYSTEM_EVENT_SERVICES WHERE SERVICE_CODE = '{service_code}'"
                deployment_log(f"SYSTEM_EVENT_SERVICES table select query ::: {select_query}")
                cursor.execute(select_query)
                
                count_system_services = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_EVENT_SERVICES {count_system_services}")
                deployment_log(f"SYSTEM_EVENT_SERVICES table select query result ::: {count_system_services}")
                cursor.close()
                if count_system_services > 0:
                    cursor = connection.cursor()
                    delete_query = f"DELETE FROM SYSTEM_EVENT_SERVICES WHERE SERVICE_CODE = '{service_code}'"
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"{delete_query}")
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
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
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
                        service_code, function_desc, function_name, None, ' ', 
                        None, None, None, None,  
                        datetime.now().strftime('%d-%m-%Y'), 'System', 'System',  
                        None, None, None
                    )
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_EVENT_SERVICES table insert query for Other database ::: {insert_query}")
                    deployment_log(f"SYSTEM_EVENT_SERVICES table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_EVENT_SERVICES table for Other database.")
                cursor.close()
                logger.log("Data inserted from SYSTEM_EVENT_SERVICES") 

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
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"{delete_query}")
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
                    line_no = str(index+3)

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
                            'line_no': line_no,
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
                            service_code, line_no, args.lower(), "I", None,  
                            "S", None, 
                            datetime.now().strftime('%d-%m-%Y'), "System", "System", None  
                        )
                        logger.log(f"\n--- Class Obj_Itemchange ---\n")
                        logger.log(f"insert_query values :: {values}")
                        deployment_log(f"SYSTEM_SERVICE_ARGS table insert query for Other database ::: {insert_query}")
                        deployment_log(f"SYSTEM_SERVICE_ARGS table insert query values for Other database ::: {values}")
                        cursor.execute(insert_query, values)
                        logger.log(f"Successfully inserted row.")
                        deployment_log(f"Data inserted successfully in SYSTEM_SERVICE_ARGS table for Other database.")  
                    cursor.close()
                    logger.log("Data inserted from SYSTEM_SERVICE_ARGS") 

                # -------------------------------------------------------------------------------------
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    update_query = """
                        UPDATE obj_itemchange SET
                        MANDATORY = :mandatory,
                        EXEC_AT = :exec_at,
                        JS_ARG = :js_arg
                        WHERE OBJ_NAME = :obj_name 
                        AND FORM_NO = :form_no
                        AND FIELD_NAME = :field_name
                    """
                    values = {
                        'obj_name': obj_name,
                        'form_no': form_no,
                        'field_name': field_name.lower(),
                        'mandatory': mandatory,
                        'exec_at': exec_at,
                        'js_arg': js_arg
                    }
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"OBJ_ITEMCHANGE table update query for Oracle database ::: {update_query}")
                    deployment_log(f"OBJ_ITEMCHANGE table update query values for Oracle database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in OBJ_ITEMCHANGE table for Oracle database.")
                else:
                    update_query = """
                        UPDATE obj_itemchange 
                        SET 
                            MANDATORY = %s,
                            EXEC_AT = %s,
                            JS_ARG = %s
                        WHERE 
                            OBJ_NAME = %s 
                            AND FORM_NO = %s
                            AND FIELD_NAME = %s
                    """
                    values = (
                        mandatory, exec_at, js_arg, 
                        obj_name, form_no, field_name.lower()
                    )
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"OBJ_ITEMCHANGE table update query for Other database ::: {update_query}")
                    deployment_log(f"OBJ_ITEMCHANGE table update query values for Other database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in OBJ_ITEMCHANGE table for Other database.")
                cursor.close()
            else:

                service_code = f'poic_{obj_name}_{field_name}'
                logger.log(f"obj_item_changed obj_name :: {obj_name}")
                logger.log(f"obj_item_changed service_code :: {service_code}")
                deployment_log(f"obj_item_changed obj_name :: {obj_name}")
                deployment_log(f"obj_item_changed service_code :: {service_code}")

                cursor = connection.cursor()
                deployment_log(f"SYSTEM_EVENTS table select query ::: SELECT COUNT(*) FROM SYSTEM_EVENTS WHERE OBJ_NAME = '{obj_name}' AND EVENT_CODE = 'post_item_change' AND FIELD_NAME = '{field_name.lower()}'")
                cursor.execute(f"""
                    SELECT COUNT(*) FROM SYSTEM_EVENTS 
                    WHERE OBJ_NAME = '{obj_name}' 
                    AND EVENT_CODE = 'post_item_change' 
                    AND FIELD_NAME = '{field_name.lower()}'
                """)                
                count_system_events = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_EVENTS {count_system_events}")
                deployment_log(f"SYSTEM_EVENTS table select query result :::  {count_system_events}")
                cursor.close()
                if count_system_events > 0:
                    cursor = connection.cursor()
                    delete_query = f"""
                        DELETE FROM SYSTEM_EVENTS 
                        WHERE OBJ_NAME = '{obj_name}' 
                        AND EVENT_CODE = 'post_item_change' 
                        AND FIELD_NAME = '{field_name.lower()}'
                    """
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"{delete_query}")
                    deployment_log(f"SYSTEM_EVENTS table delete query :::  {delete_query}")
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
                        'event_code': 'post_item_change',
                        'event_context': event_context,
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
                        'field_name': field_name.lower()
                    }
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
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
                            TO_DATE( %s, 'DD-MM-YYYY'), %s, %s, %s, %s, %s, %s, %s
                        )
                    """
                    values = (
                        obj_name,
                        'post_item_change',
                        event_context,
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
                        field_name.lower()
                    )
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_EVENTS table insert query for Other database ::: {insert_query}")
                    deployment_log(f"SYSTEM_EVENTS table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_EVENTS table for Other database.")
                cursor.close()
                logger.log("Data inserted from SYSTEM_EVENTS") 

                # -------------------------------------------------------------------------------------

                cursor = connection.cursor()
                select_query = f"SELECT COUNT(*) FROM SYSTEM_EVENT_SERVICES WHERE SERVICE_CODE = '{service_code}'"
                deployment_log(f"SYSTEM_EVENT_SERVICES table select query ::: {select_query}")
                cursor.execute(select_query)
                
                count_system_services = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_EVENT_SERVICES {count_system_services}")
                deployment_log(f"SYSTEM_EVENT_SERVICES table select query result :::  {count_system_services}")
                cursor.close()
                if count_system_services > 0:
                    cursor = connection.cursor()
                    delete_query = f"DELETE FROM SYSTEM_EVENT_SERVICES WHERE SERVICE_CODE = '{service_code}'"
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"{delete_query}")
                    deployment_log(f"SYSTEM_EVENT_SERVICES table delete query :::  {delete_query}")
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
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
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
                        service_code, function_desc, function_name, None, ' ', 
                        None, None, None, None,  
                        datetime.now().strftime('%d-%m-%Y'), 'System', 'System',  
                        None, None, None
                    )
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SYSTEM_EVENT_SERVICES table insert query for Other database ::: {insert_query}")
                    deployment_log(f"SYSTEM_EVENT_SERVICES table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_EVENT_SERVICES table for Other database.")
                cursor.close()
                logger.log("Data inserted from SYSTEM_EVENT_SERVICES") 

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
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"{delete_query}")
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
                    line_no = str(index+3)

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
                            'line_no': line_no,
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
                            service_code, line_no, args.lower(), "I", None,  
                            "S", None, 
                            datetime.now().strftime('%d-%m-%Y'), "System", "System", None  
                        )
                        logger.log(f"\n--- Class Obj_Itemchange ---\n")
                        logger.log(f"insert_query values :: {values}")
                        deployment_log(f"SYSTEM_SERVICE_ARGS table insert query for Other database ::: {insert_query}")
                        deployment_log(f"SYSTEM_SERVICE_ARGS table insert query values for Other database ::: {values}")
                        cursor.execute(insert_query, values)
                        logger.log(f"Successfully inserted row.")
                        deployment_log(f"Data inserted successfully in SYSTEM_SERVICE_ARGS table for Other database.")  
                    cursor.close()
                    logger.log("Data inserted from SYSTEM_SERVICE_ARGS") 

                # -------------------------------------------------------------------------------------
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    insert_query = """
                                INSERT INTO obj_itemchange (
                                OBJ_NAME, FORM_NO, FIELD_NAME, MANDATORY, EXEC_AT, JS_ARG
                                ) VALUES (:obj_name, :form_no, :field_name, :mandatory, :exec_at, :js_arg)
                            """
                    values = {
                        'obj_name': obj_name,
                        'form_no': form_no,
                        'field_name': field_name.lower(),
                        'mandatory': mandatory,
                        'exec_at': exec_at,
                        'js_arg': js_arg
                    }
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"OBJ_ITEMCHANGE table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"OBJ_ITEMCHANGE table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in OBJ_ITEMCHANGE table for Oracle database.")  
                else:
                    insert_query = """
                        INSERT INTO obj_itemchange (
                            OBJ_NAME, FORM_NO, FIELD_NAME, MANDATORY, EXEC_AT, JS_ARG
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    values = (
                        obj_name, form_no, field_name.lower(),
                        mandatory, exec_at, js_arg
                    )
                    logger.log(f"\n--- Class Obj_Itemchange ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"OBJ_ITEMCHANGE table insert query for Other database ::: {insert_query}")
                    deployment_log(f"OBJ_ITEMCHANGE table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in OBJ_ITEMCHANGE table for Other database.")  
                cursor.close()
                logger.log("Data inserted from obj_itemchange") 

    def process_data(self, conn, sql_models_data, object_name, schema_name, con_type):
        logger.log(f"Start of Obj_Itemchange Class")
        deployment_log(f"\n--------------------------------- Start of Obj_Itemchange Class -------------------------------------\n")
        self.sql_models = sql_models_data
        for sql_model in self.sql_models:
            if "sql_model" in sql_model and "columns" in sql_model['sql_model']:
                for column in sql_model['sql_model']['columns']:
                    if "column" in column and "item_change" in column['column']:
                        item_change = column['column']['item_change']
                        logger.log(f"Value of item_change :: {item_change}")
                        deployment_log(f"OBJ_ITEMCHANGE value of item_change :: {item_change}")
                        # if self.is_valid_json(item_change):
                        if str(item_change).startswith("business_logic"):
                            sql_function_name = item_change.split("'")[1]
                            sql_desc = item_change.split("'")[3]
                            fld_name = column['column']['db_name']
                            form_no = sql_model['sql_model']['form_no']
                            logger.log(f"Inside sql_function_name: {sql_function_name}")
                            logger.log(f"Inside sql_desc: {sql_desc}")
                            logger.log(f"Inside fld_name: {fld_name}")

                            deployment_log(f"OBJ_ITEMCHANGE value of sql_function_name :: {sql_function_name}")
                            deployment_log(f"OBJ_ITEMCHANGE value of sql_desc :: {sql_desc}")
                            deployment_log(f"OBJ_ITEMCHANGE value of fld_name :: {fld_name}")

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
                                logger.log(f"\n--- Class Obj_Itemchange ---\n")
                                logger.log(f"{queryy}")
                                deployment_log(f"OBJ_ITEMCHANGE table get arguments select query for Oracle database ::: {queryy}")
                                cursor.execute(queryy)
                                result = cursor.fetchall()
                                result = result if result != [] else None
                                logger.log(f"\n result value:::\t{result}")
                                deployment_log(f"OBJ_ITEMCHANGE table get arguments select query for Oracle database result :::  {result}")
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
                                    logger.log(f"\n obj_itemchange sql_input:::\t{arg_list}")
                                    deployment_log(f"OBJ_ITEMCHANGE table sql_input :::  {arg_list}")

                                    item_change_json = {
                                        'obj_name': object_name,
                                        'form_no': form_no,
                                        'field_name': fld_name,
                                        'arg_list': arg_list,
                                        'function_name': sql_function_name,
                                        'function_desc': sql_desc
                                    }
                                    self.check_or_update_obj_itemchange(item_change_json, conn, con_type)
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
                                logger.log(f"\n--- Class Obj_Itemchange ---\n")
                                logger.log(f"{queryy}")
                                deployment_log(f"OBJ_ITEMCHANGE table get arguments select query for Other database ::: {queryy}")
                                cursor.execute(queryy)
                                result = cursor.fetchone()
                                result = result[0] if result is not None else None
                                logger.log(f"\n result value:::\t{result}")
                                deployment_log(f"OBJ_ITEMCHANGE table get arguments select query for Other database result :::  {result}")
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
                                    logger.log(f"\n obj_itemchange sql_input:::\t{arg_list}")
                                    deployment_log(f"OBJ_ITEMCHANGE table sql_input :::  {arg_list}")

                                    item_change_json = {
                                        'obj_name': object_name,
                                        'form_no': form_no,
                                        'field_name': fld_name,
                                        'arg_list': arg_list,
                                        'function_name': sql_function_name,
                                        'function_desc': sql_desc
                                    }
                                    self.check_or_update_obj_itemchange(item_change_json, conn, con_type)
                                else:
                                    deployment_log(f"Function {sql_function_name} definition is not found, so please execute the function and then upload the model json.")
                                    raise Exception(f"Function {sql_function_name} definition is not found, so please execute the function and then upload the model json.")
        logger.log(f"End of Obj_Itemchange Class")
        deployment_log(f"End of Obj_Itemchange Class")