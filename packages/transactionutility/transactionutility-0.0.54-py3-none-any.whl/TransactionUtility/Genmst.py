import cx_Oracle
from datetime import datetime
import loggerutility as logger
import json
import re
from loggerutility import deployment_log

class Genmst:

    sql_models = []

    def insert_or_update_genmst(self, column, connection, con_type):
        
        required_keys = [
            'fld_name','mod_name','error_cd','blank_opt','fld_type'
        ]
        missing_keys = [key for key in required_keys if key not in column]

        if missing_keys:
            deployment_log(f"Missing required keys for GENMST table: {', '.join(missing_keys)}")
            raise KeyError(f"Missing required keys for genmst table: {', '.join(missing_keys)}")
        else:
            fld_name = column.get('fld_name', '') or None
            mod_name = column.get('mod_name', '').upper() or None
            descr = column.get('descr', '').strip() or None
            error_cd = column.get('error_cd', '').strip() or None
            blank_opt = column.get('blank_opt', '').strip() or None
            fld_type = column.get('fld_type','').strip() or None
            fld_min = column.get('fld_min', '') or None
            fld_max = column.get('fld_max', '') or None
            val_type = column.get('val_type', '') or None
            chg_date = datetime.now().strftime('%d-%m-%y')
            chg_user = column.get('chg_user', '').strip() or 'System'
            chg_term = column.get('chg_term', '').strip() or 'System'
            val_table = column.get('val_table', '') or None
            sql_input = column.get('sql_input', '') or None
            fld_width = column.get('fld_width', '') or 0
            udf_usage_1 = column.get('udf_usage_1', '') or None
            udf_usage_2 = column.get('udf_usage_2', '') or None
            udf_usage_3 = column.get('udf_usage_3', '') or None
            val_stage = column.get('val_stage', '') or None
            obj_name = column.get('obj_name', '')[2:] or None
            form_no = column.get('form_no', '') or None
            action = column.get('action', '') or None
            user_id = column.get('user_id', '') or None
            tran_id = column.get('tran_id', '').strip() or None
            udf_str1_descr = column.get('udf_str1_descr', '') or None
            udf_str2_descr = column.get('udf_str2_descr', '') or None
            udf_str3_descr = column.get('udf_str3_descr', '') or None
            exec_seq = column.get('exec_seq', '') or 0

            # cursor = connection.cursor()
            # queryy = "SELECT COUNT(*) FROM genmst WHERE FLD_NAME = :fld_name and MOD_NAME = :mod_name"
            # cursor.execute(queryy,{'fld_name': fld_name,'mod_name': mod_name})
            # count = cursor.fetchone()[0]
            # logger.log(f"Inside count {count}")
            # cursor.close()
            # if count > 0:
            #     logger.log(f"Inside update :: {fld_name}")
            #     logger.log(f"Inside update :: {action}")
            #     cursor = connection.cursor()
            #     update_query = """
            #         UPDATE genmst SET
            #         FLD_NAME = :FLD_NAME, MOD_NAME = :MOD_NAME, DESCR = :DESCR, ERROR_CD = :ERROR_CD,
            #         BLANK_OPT = :BLANK_OPT, FLD_TYPE = :FLD_TYPE, FLD_MIN = :FLD_MIN, FLD_MAX = :FLD_MAX,
            #         VAL_TYPE = :VAL_TYPE, CHG_DATE = TO_DATE(:CHG_DATE, 'DD-MM-YYYY'), CHG_USER = :CHG_USER,
            #         CHG_TERM = :CHG_TERM, VAL_TABLE = :VAL_TABLE, SQL_INPUT = :SQL_INPUT, FLD_WIDTH = :FLD_WIDTH,
            #         UDF_USAGE_1 = :UDF_USAGE_1, UDF_USAGE_2 = :UDF_USAGE_2, UDF_USAGE_3 = :UDF_USAGE_3,
            #         VAL_STAGE = :VAL_STAGE, OBJ_NAME = :OBJ_NAME, FORM_NO = :FORM_NO, ACTION = :ACTION,
            #         USER_ID = :USER_ID, UDF_STR1_DESCR = :UDF_STR1_DESCR, UDF_STR2_DESCR = :UDF_STR2_DESCR,
            #         UDF_STR3_DESCR = :UDF_STR3_DESCR, EXEC_SEQ = :EXEC_SEQ
            #         WHERE FLD_NAME = :fld_name and MOD_NAME = :mod_name
            #     """
            #     cursor.execute(update_query, {
            #         'fld_name': fld_name,
            #         'mod_name': mod_name,
            #         'descr': descr[:40],
            #         'error_cd': error_cd,
            #         'blank_opt': blank_opt,
            #         'fld_type': fld_type,
            #         'fld_min': fld_min,
            #         'fld_max': fld_max,
            #         'val_type': val_type,
            #         'chg_date': chg_date,
            #         'chg_user': chg_user,
            #         'chg_term': chg_term,
            #         'val_table': val_table,
            #         'sql_input': sql_input,
            #         'fld_width': fld_width,
            #         'udf_usage_1': udf_usage_1,
            #         'udf_usage_2': udf_usage_2,
            #         'udf_usage_3': udf_usage_3,
            #         'val_stage': val_stage,
            #         'obj_name': obj_name,
            #         'form_no': form_no,
            #         'action': action ,
            #         'user_id': user_id ,
            #         'udf_str1_descr': udf_str1_descr,
            #         'udf_str2_descr': udf_str2_descr,
            #         'udf_str3_descr': udf_str3_descr,
            #         'exec_seq': exec_seq
            #     })
            #     cursor.close()
            #     logger.log(f"Updated: MOD_NAME = {mod_name}")
            # else:

            logger.log(f"Inside insert")
            cursor = connection.cursor()
            max_queryy = "SELECT MAX(tran_id) FROM genmst"
            deployment_log(f"GENMST table select query ::: {max_queryy}")
            cursor.execute(max_queryy)
            max_val = cursor.fetchone()[0]
            logger.log(f"max_val ::: {max_val}")
            deployment_log(f"GENMST table select query result ::: {max_val}")
            tran_id = self.add_one_to_numeric_part(max_val)
            deployment_log(f"GENMST table tran_id value ::: {tran_id}")
            cursor.close()

            cursor = connection.cursor()
            deployment_log(f"MESSAGES table select query ::: SELECT COUNT(*) FROM messages WHERE MSG_NO = '{error_cd}'")
            cursor.execute(f"""
                SELECT COUNT(*) FROM messages 
                WHERE MSG_NO = '{error_cd}'
            """)

            count_messages = cursor.fetchone()[0]
            logger.log(f"Count MESSAGES {count_messages}")
            deployment_log(f"MESSAGES table select query result :::  {count_messages}")
            cursor.close()
            if count_messages > 0:
                cursor = connection.cursor()
                delete_query = f"""
                    DELETE FROM messages 
                    WHERE MSG_NO = '{error_cd}'
                """
                logger.log(f"Class Genmst delete_query ::: {delete_query}")
                deployment_log(f"MESSAGES table delete query :::  {delete_query}")
                cursor.execute(delete_query)

                cursor.close()
                logger.log("Data deleted from MESSAGES") 
                deployment_log("Data deleted from MESSAGES") 

            logger.log(f"msg_no Of messages ::: {error_cd}")
            deployment_log(f"msg_no Of MESSAGES ::: {error_cd}")

            cursor = connection.cursor()
            if con_type == 'Oracle':
                insert_query = """
                    INSERT INTO messages (
                        MSG_NO, MSG_STR, MSG_DESCR, MSG_TYPE, MSG_OPT, MSG_TIME, ALARM,
                        ERR_SOURCE, CHG_DATE, CHG_USER, CHG_TERM, OVERRIDE_INPUT, MAIL_OPTION
                    ) VALUES (
                        :msg_no, :msg_str, :msg_descr, :msg_type, :msg_opt, :msg_time, :alarm,
                        :err_source, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term,
                        :override_input, :mail_option
                    )
                """
                values = {
                    'msg_no': error_cd,
                    'msg_str': descr[:60],
                    'msg_descr': descr[:60],
                    'msg_type': 'E', 
                    'msg_opt': 'Y', 
                    'msg_time': '', 
                    'alarm': '',
                    'err_source': '',
                    "chg_date": datetime.now().strftime('%d-%m-%y'),
                    "chg_user": "System", 
                    "chg_term": "System",
                    'override_input': '', 
                    'mail_option': ''
                }
                logger.log(f"\n--- Class Genmst ---\n")
                logger.log(f"insert_query values :: {values}")
                deployment_log(f"MESSAGES table insert query for Oracle database ::: {insert_query}")
                deployment_log(f"MESSAGES table insert query values for Oracle database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in MESSAGES table for Oracle database.")
            else:
                insert_query = """
                    INSERT INTO messages (
                        MSG_NO, MSG_STR, MSG_DESCR, MSG_TYPE, MSG_OPT, MSG_TIME, ALARM,
                        ERR_SOURCE, CHG_DATE, CHG_USER, CHG_TERM, OVERRIDE_INPUT, MAIL_OPTION
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s, %s
                    )
                """
                values = (
                    error_cd,
                    descr[:60],
                    descr[:60],
                    'E',
                    'Y',
                    None, 
                    None,
                    None,
                    datetime.now().strftime('%d-%m-%Y'), 
                    "System",
                    "System",
                    None,
                    None
                )
                logger.log(f"\n--- Class Genmst ---\n")
                logger.log(f"insert_query values :: {values}")
                deployment_log(f"MESSAGES table insert query for Other database ::: {insert_query}")
                deployment_log(f"MESSAGES table insert query values for Other database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in MESSAGES table for Other database.")
            cursor.close()

            # --------------------------------------------------------------------------------

            cursor = connection.cursor()
            deployment_log(f"SYSTEM_EVENTS table select query ::: SELECT COUNT(*) FROM SYSTEM_EVENTS WHERE OBJ_NAME = '{obj_name}' and EVENT_CODE = 'post_validate'")
            cursor.execute(f"""
                SELECT COUNT(*) FROM SYSTEM_EVENTS 
                WHERE OBJ_NAME = '{obj_name}' and EVENT_CODE = 'post_validate'
            """)

            count_system_events = cursor.fetchone()[0]
            logger.log(f"Count SYSTEM_EVENTS {count_system_events}")
            deployment_log(f"SYSTEM_EVENTS table select query result ::: {count_system_events}")
            cursor.close()
            if count_system_events > 0:
                cursor = connection.cursor()
                delete_query = f"""
                    DELETE FROM SYSTEM_EVENTS 
                    WHERE OBJ_NAME = '{obj_name}' and EVENT_CODE = 'post_validate'
                """
                logger.log(f"Class Genmst delete_query ::: {delete_query}")
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
                        :comp_name, :comm_format, :fld_name
                    )
                """
                values = {
                    'obj_name': obj_name,
                    'event_code': 'post_validate',
                    'event_context': '1',
                    'service_code': 'post_gen_val',
                    'method_rule': None,
                    'overwrite_core': '0',
                    'chg_date': datetime.now().strftime('%d-%m-%y'),  
                    'chg_user': 'System',
                    'chg_term': 'System',
                    'result_handle': '2',
                    'comp_type': 'JB',
                    'comp_name': 'ibase.webitm.ejb.sys.GenValidate',
                    'comm_format': None,
                    'fld_name': ''
                }
                logger.log(f"\n--- Class Genmst ---\n")
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
                        TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s, %s, %s, %s, %s
                    )
                """
                values = (
                    obj_name,
                    'post_validate',
                    '1',
                    'post_gen_val',
                    None,  
                    '0',
                    datetime.now().strftime('%d-%m-%Y'),  
                    'System',
                    'System',
                    '2',
                    'JB',
                    'ibase.webitm.ejb.sys.GenValidate',
                    None,  
                    None  
                )
                logger.log(f"\n--- Class Genmst ---\n")
                logger.log(f"insert_query values :: {values}")
                deployment_log(f"SYSTEM_EVENTS table insert query for Other database ::: {insert_query}")
                deployment_log(f"SYSTEM_EVENTS table insert query values for Other database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in SYSTEM_EVENTS table for Other database.")
            cursor.close()
                
            # --------------------------------------------------------------------------------
                
            cursor = connection.cursor()
            deployment_log(f"SYSTEM_EVENT_SERVICES table select query ::: SELECT COUNT(*) FROM SYSTEM_EVENT_SERVICES WHERE service_code = 'post_gen_val'")
            cursor.execute(f"""
                SELECT COUNT(*) FROM SYSTEM_EVENT_SERVICES 
                WHERE service_code = 'post_gen_val'
            """)

            count_system_services = cursor.fetchone()[0]
            logger.log(f"Count SYSTEM_EVENT_SERVICES {count_system_services}")
            deployment_log(f"SYSTEM_EVENT_SERVICES table select query result ::: {count_system_services}")
            cursor.close()
            if count_system_services > 0:
                cursor = connection.cursor()
                delete_query = f"DELETE FROM SYSTEM_EVENT_SERVICES WHERE service_code = 'post_gen_val'"
                logger.log(f"Class Genmst delete_query ::: {delete_query}")
                deployment_log(f"SYSTEM_EVENT_SERVICES table delete query ::: {delete_query}")
                cursor.execute(delete_query)
                cursor.close()
                logger.log("Data deleted from SYSTEM_EVENT_SERVICES") 
                deployment_log("Data deleted from SYSTEM_EVENT_SERVICES") 

            cursor = connection.cursor()
            if con_type == 'Oracle':
                insert_query = """
                    INSERT INTO SYSTEM_EVENT_SERVICES (
                        SERVICE_CODE, SERVICE_DESCR, SERVICE_URI, SERVICE_PROVIDER, METHOD_NAME, RETURN_VALUE, 
                        RETURN_TYPE, RETURN_DESCR, RETURN_XFRM, CHG_DATE, CHG_USER, CHG_TERM, SERVICE_NAMESPACE, 
                        RES_ELEM, SOAP_ACTION
                    ) 
                    VALUES (
                        :service_code, :service_descr, :service_uri, :service_provider, :method_name, :return_value, 
                        :return_type, :return_descr, :return_xfrm, TO_DATE(:chg_date, 'DD-MM-YY'), :chg_user, :chg_term, 
                        :service_namespace, :res_elem, :soap_action
                    )
                """
                values = {
                    'service_code': 'post_gen_val',
                    'service_descr': 'validation',
                    'service_uri': 'http://localhost:9090/axis/services/ValidatorService',
                    'service_provider': 'BASE iformation',
                    'method_name': 'wfValData',
                    'return_value': 'String',
                    'return_type': 'S',
                    'return_descr': None,
                    'return_xfrm': None,
                    'chg_date': datetime.now().strftime('%d-%m-%y'),  
                    'chg_user': 'System',
                    'chg_term': 'System',
                    'service_namespace': None,
                    'res_elem': None,
                    'soap_action': None
                }
                logger.log(f"\n--- Class Genmst ---\n")
                logger.log(f"insert_query values :: {values}")
                deployment_log(f"SYSTEM_EVENT_SERVICES table insert query for Oracle database ::: {insert_query}")
                deployment_log(f"SYSTEM_EVENT_SERVICES table insert query values for Oracle database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in SYSTEM_EVENT_SERVICES table for Oracle database.")
            else:
                insert_query = """
                    INSERT INTO SYSTEM_EVENT_SERVICES (
                        SERVICE_CODE, SERVICE_DESCR, SERVICE_URI, SERVICE_PROVIDER, METHOD_NAME, RETURN_VALUE, 
                        RETURN_TYPE, RETURN_DESCR, RETURN_XFRM, CHG_DATE, CHG_USER, CHG_TERM, SERVICE_NAMESPACE, 
                        RES_ELEM, SOAP_ACTION
                    ) 
                    VALUES (
                        %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, 
                        %s, %s, %s
                    )
                """
                values = (
                    'post_gen_val',
                    'validation',
                    'http://localhost:9090/axis/services/ValidatorService',
                    'BASE iformation',
                    'wfValData',
                    'String',
                    'S',
                    None,                      
                    None,                      
                    datetime.now().strftime('%d-%m-%y'),  
                    'System',
                    'System',
                    None,                      
                    None,                     
                    None                      
                )
                logger.log(f"\n--- Class Genmst ---\n")
                logger.log(f"insert_query values :: {values}") 
                deployment_log(f"SYSTEM_EVENT_SERVICES table insert query for Other database ::: {insert_query}")
                deployment_log(f"SYSTEM_EVENT_SERVICES table insert query values for Other database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in SYSTEM_EVENT_SERVICES table for Other database.")
            cursor.close()                   

            # --------------------------------------------------------------------------------

            cursor = connection.cursor()
            deployment_log(f"SYSTEM_SERVICE_ARGS table select query ::: SELECT COUNT(*) FROM SYSTEM_SERVICE_ARGS WHERE service_code = 'post_gen_val'")
            cursor.execute(f"""
                SELECT COUNT(*) FROM SYSTEM_SERVICE_ARGS 
                WHERE service_code = 'post_gen_val'
            """)

            count_system_services_args = cursor.fetchone()[0]
            logger.log(f"Count SYSTEM_SERVICE_ARGS {count_system_services_args}")
            deployment_log(f"SYSTEM_SERVICE_ARGS table select query result ::: {count_system_services_args}")
            cursor.close()
            if count_system_services_args > 0:
                cursor = connection.cursor()
                delete_query = f"DELETE FROM SYSTEM_SERVICE_ARGS WHERE service_code = 'post_gen_val'"
                logger.log(f"Class Genmst delete_query ::: {delete_query}")
                deployment_log(f"SYSTEM_SERVICE_ARGS table delete query ::: {delete_query}")
                cursor.execute(delete_query)
                cursor.close()
                logger.log("Data deleted from SYSTEM_SERVICE_ARGS") 
                deployment_log("Data deleted from SYSTEM_SERVICE_ARGS") 

            cursor = connection.cursor()
            if con_type == 'Oracle':
                insert_query = """
                    INSERT INTO SYSTEM_SERVICE_ARGS (
                        SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, ARG_XFRM, 
                        CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
                    ) 
                    VALUES (
                        :service_code, :line_no, :arg_name, :arg_mode, :descr, :arg_type, :arg_xfrm, 
                        TO_DATE(:chg_date, 'DD-MM-YY'), :chg_user, :chg_term, :arg_value
                    )
                """
                values = [
                    {
                        'service_code': 'post_gen_val', 'line_no': 1, 'arg_name': 'COMPONENT_TYPE', 'arg_mode': 'I', 'descr': None,
                        'arg_type': 'C.String', 'arg_xfrm': None, 'chg_date': datetime.now().strftime('%d-%m-%y'), 'chg_user': 'System', 'chg_term': 'System', 'arg_value': 'JB'
                    },
                    {
                        'service_code': 'post_gen_val', 'line_no': 2, 'arg_name': 'COMPONENT_NAME', 'arg_mode': 'I', 'descr': None,
                        'arg_type': 'C.String', 'arg_xfrm': None, 'chg_date': datetime.now().strftime('%d-%m-%y'), 'chg_user': 'System', 'chg_term': 'System', 'arg_value': 'ibase.webitm.ejb.sys.GenValidate'
                    },
                    {
                        'service_code': 'post_gen_val', 'line_no': 3, 'arg_name': 'XML_DATA', 'arg_mode': 'I', 'descr': None,
                        'arg_type': 'S', 'arg_xfrm': None, 'chg_date': datetime.now().strftime('%d-%m-%y'), 'chg_user': 'System', 'chg_term': 'System', 'arg_value': None
                    },
                    {
                        'service_code': 'post_gen_val', 'line_no': 4, 'arg_name': 'XML_DATA_ALL', 'arg_mode': 'I', 'descr': None,
                        'arg_type': 'S', 'arg_xfrm': None, 'chg_date': datetime.now().strftime('%d-%m-%y'), 'chg_user': 'System', 'chg_term': 'System', 'arg_value': None
                    },
                    {
                        'service_code': 'post_gen_val', 'line_no': 5, 'arg_name': 'XML_DATA_ALL', 'arg_mode': 'I', 'descr': None,
                        'arg_type': 'S', 'arg_xfrm': None, 'chg_date': datetime.now().strftime('%d-%m-%y'), 'chg_user': 'System', 'chg_term': 'System', 'arg_value': None
                    },
                    {
                        'service_code': 'post_gen_val', 'line_no': 6, 'arg_name': 'OBJ_CONTEXT', 'arg_mode': 'I', 'descr': None,
                        'arg_type': 'S', 'arg_xfrm': None, 'chg_date': datetime.now().strftime('%d-%m-%y'), 'chg_user': 'System', 'chg_term': 'System', 'arg_value': None
                    },
                    {
                        'service_code': 'post_gen_val', 'line_no': 7, 'arg_name': 'WIN_NAME', 'arg_mode': 'I', 'descr': None,
                        'arg_type': 'S', 'arg_xfrm': None, 'chg_date': datetime.now().strftime('%d-%m-%y'), 'chg_user': 'System', 'chg_term': 'System', 'arg_value': None
                    },
                    {
                        'service_code': 'post_gen_val', 'line_no': 8, 'arg_name': 'XTRA_PARAMS', 'arg_mode': 'I', 'descr': None,
                        'arg_type': 'S', 'arg_xfrm': None, 'chg_date': datetime.now().strftime('%d-%m-%y'), 'chg_user': 'System', 'chg_term': 'System', 'arg_value': None
                    },
                    {
                        'service_code': 'post_gen_val', 'line_no': 9, 'arg_name': 'ACTION', 'arg_mode': 'I', 'descr': None,
                        'arg_type': 'S', 'arg_xfrm': None, 'chg_date': datetime.now().strftime('%d-%m-%y'), 'chg_user': 'System', 'chg_term': 'System', 'arg_value': None
                    }
                ]
                logger.log(f"\n--- Class Genmst ---\n")
                for row in values:
                    logger.log(f"insert_query values :: {row}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query values for Oracle database ::: {row}")
                    cursor.execute(insert_query, row)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_SERVICE_ARGS table for Oracle database.")
            else:
                insert_query = """
                    INSERT INTO SYSTEM_SERVICE_ARGS (
                        SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, ARG_XFRM, 
                        CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
                    ) 
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, 
                        TO_DATE(%s, 'DD-MM-YY'), %s, %s, %s
                    )
                """
                values = [
                    ('post_gen_val', 1, 'COMPONENT_TYPE', 'I', None, 'C.String', None, datetime.now().strftime('%d-%m-%y'), 'System', 'System', 'JB'),
                    ('post_gen_val', 2, 'COMPONENT_NAME', 'I', None, 'C.String', None, datetime.now().strftime('%d-%m-%y'), 'System', 'System', 'ibase.webitm.ejb.sys.GenValidate'),
                    ('post_gen_val', 3, 'XML_DATA', 'I', None, 'S', None, datetime.now().strftime('%d-%m-%y'), 'System', 'System', None),
                    ('post_gen_val', 4, 'XML_DATA_ALL', 'I', None, 'S', None, datetime.now().strftime('%d-%m-%y'), 'System', 'System', None),
                    ('post_gen_val', 5, 'XML_DATA_ALL', 'I', None, 'S', None, datetime.now().strftime('%d-%m-%y'), 'System', 'System', None),
                    ('post_gen_val', 6, 'OBJ_CONTEXT', 'I', None, 'S', None, datetime.now().strftime('%d-%m-%y'), 'System', 'System', None),
                    ('post_gen_val', 7, 'WIN_NAME', 'I', None, 'S', None, datetime.now().strftime('%d-%m-%y'), 'System', 'System', None),
                    ('post_gen_val', 8, 'XTRA_PARAMS', 'I', None, 'S', None, datetime.now().strftime('%d-%m-%y'), 'System', 'System', None),
                    ('post_gen_val', 9, 'ACTION', 'I', None, 'S', None, datetime.now().strftime('%d-%m-%y'), 'System', 'System', None)
                ]
                logger.log(f"\n--- Class Genmst ---\n")
                for row in values:
                    logger.log(f"insert_query values :: {row}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query for Other database ::: {insert_query}")
                    deployment_log(f"SYSTEM_SERVICE_ARGS table insert query values for Other database ::: {row}")
                    cursor.execute(insert_query, row)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SYSTEM_SERVICE_ARGS table for Other database.")
            cursor.close() 

            # --------------------------------------------------------------------------------

            cursor = connection.cursor()
            if con_type == 'Oracle':
                insert_query = """
                    INSERT INTO genmst (
                    FLD_NAME, MOD_NAME, DESCR, ERROR_CD, BLANK_OPT, FLD_TYPE, FLD_MIN, FLD_MAX, VAL_TYPE,
                    CHG_DATE, CHG_USER, CHG_TERM, VAL_TABLE, SQL_INPUT, FLD_WIDTH, UDF_USAGE_1, UDF_USAGE_2,
                    UDF_USAGE_3, VAL_STAGE, OBJ_NAME, FORM_NO, ACTION, USER_ID, TRAN_ID, UDF_STR1_DESCR,
                    UDF_STR2_DESCR, UDF_STR3_DESCR, EXEC_SEQ
                    ) VALUES (
                    :fld_name, :mod_name, :descr, :error_cd, :blank_opt, :fld_type, :fld_min, :fld_max, :val_type,
                    TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :val_table, :sql_input, :fld_width,
                    :udf_usage_1, :udf_usage_2, :udf_usage_3, :val_stage, :obj_name, :form_no, :action, :user_id,
                    :tran_id, :udf_str1_descr, :udf_str2_descr, :udf_str3_descr, :exec_seq
                    )
                """
                values = {
                    'fld_name': fld_name,
                    'mod_name': mod_name,
                    'descr': descr[:40],
                    'error_cd': error_cd,
                    'blank_opt': blank_opt,
                    'fld_type': fld_type,
                    'fld_min': fld_min,
                    'fld_max': fld_max,
                    'val_type': val_type,
                    'chg_date': chg_date,
                    'chg_user': chg_user,
                    'chg_term': chg_term,
                    'val_table': val_table,
                    'sql_input': sql_input,
                    'fld_width': fld_width,
                    'udf_usage_1': udf_usage_1,
                    'udf_usage_2': udf_usage_2,
                    'udf_usage_3': udf_usage_3,
                    'val_stage': val_stage,
                    'obj_name': obj_name,
                    'form_no': form_no,
                    'action': action ,
                    'user_id': user_id ,
                    'tran_id': tran_id ,
                    'udf_str1_descr': udf_str1_descr,
                    'udf_str2_descr': udf_str2_descr,
                    'udf_str3_descr': udf_str3_descr,
                    'exec_seq': exec_seq
                }
                logger.log(f"\n--- Class Genmst ---\n")
                logger.log(f"insert_query values :: {values}")
                deployment_log(f"GENMST table insert query for Oracle database ::: {insert_query}")
                deployment_log(f"GENMST table insert query values for Oracle database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in GENMST table for Oracle database.")
            else:
                insert_query = """
                    INSERT INTO genmst (
                        FLD_NAME, MOD_NAME, DESCR, ERROR_CD, BLANK_OPT, FLD_TYPE, FLD_MIN, FLD_MAX, VAL_TYPE,
                        CHG_DATE, CHG_USER, CHG_TERM, VAL_TABLE, SQL_INPUT, FLD_WIDTH, UDF_USAGE_1, UDF_USAGE_2,
                        UDF_USAGE_3, VAL_STAGE, OBJ_NAME, FORM_NO, ACTION, USER_ID, TRAN_ID, UDF_STR1_DESCR,
                        UDF_STR2_DESCR, UDF_STR3_DESCR, EXEC_SEQ
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s
                    )
                """
                values = (
                    fld_name,
                    mod_name,
                    descr[:40],  
                    error_cd,
                    blank_opt,
                    fld_type,
                    fld_min,
                    fld_max,
                    val_type,
                    chg_date,
                    chg_user,
                    chg_term,
                    val_table,
                    sql_input,
                    fld_width,
                    udf_usage_1,
                    udf_usage_2,
                    udf_usage_3,
                    val_stage,
                    obj_name,
                    form_no,
                    action,
                    user_id,
                    tran_id,
                    udf_str1_descr,
                    udf_str2_descr,
                    udf_str3_descr,
                    exec_seq
                )
                logger.log(f"\n--- Class Genmst ---\n")
                logger.log(f"insert_query values :: {values}")
                deployment_log(f"GENMST table insert query for Other database ::: {insert_query}")
                deployment_log(f"GENMST table insert query values for Other database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in GENMST table for Other database.")
            cursor.close()

    def is_valid_json(self, data):
        if isinstance(data, dict):
            return True
        try:
            json.loads(data)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
        
    def add_one_to_numeric_part(self, value):
        logger.log(f"value ::: {value}")
        if value != None:
            numeric_part = re.findall(r'\d+', value)
            if numeric_part:
                num = int(numeric_part[0]) + 1
                num_str = str(num).zfill(len(numeric_part[0]))
                return re.sub(r'\d+', num_str, value, 1)
            else:
                return value
        else:
            return '00000000000000000001'
        
    def process_data(self, conn, sql_models_data, db_vendore, mod_name):
        logger.log(f"Start of Genmst Class")
        deployment_log(f"\n--------------------------------- Start of Genmst Class -------------------------------------\n")

        # --------------------------------

        cursor = conn.cursor()
        deployment_log(f"GENMST table select query ::: SELECT COUNT(*) FROM genmst WHERE MOD_NAME = '{mod_name}'")
        cursor.execute(f"""
            SELECT COUNT(*) FROM genmst 
            WHERE MOD_NAME = '{mod_name}'
        """)

        count_genmst = cursor.fetchone()[0]
        logger.log(f"Count genmst {count_genmst}")
        deployment_log(f"GENMST table select query result ::: {count_genmst}")
        cursor.close()
        if count_genmst > 0:
            cursor = conn.cursor()
            delete_query = f"DELETE FROM genmst WHERE MOD_NAME = '{mod_name}'"
            logger.log(f"Class Genmst delete_query ::: {delete_query}")
            deployment_log(f"GENMST table delete query ::: {delete_query}")
            cursor.execute(delete_query)
            cursor.close()
            logger.log("Data deleted from genmst") 
            deployment_log("Data deleted from GENMST") 

        # --------------------------------

        self.sql_models = sql_models_data
        for sql_model in self.sql_models:
            if "sql_model" in sql_model and "columns" in sql_model['sql_model']:
                for columns in sql_model['sql_model']['columns']:
                    if "column" in columns and "validations" in columns['column']:
                        validations = columns['column']['validations']
                        for column in validations:
                            if self.is_valid_json(column):
                                self.insert_or_update_genmst(column, conn, db_vendore)
        logger.log(f"End of Genmst Class")
        deployment_log(f"End of Genmst Class")

