import cx_Oracle, json, re
from DatabaseConnectionUtility import Oracle 
from DatabaseConnectionUtility import Dremio
from DatabaseConnectionUtility import InMemory 
from DatabaseConnectionUtility import Oracle
from DatabaseConnectionUtility import MySql
from DatabaseConnectionUtility import MSSQLServer 
from DatabaseConnectionUtility import SAPHANA
from DatabaseConnectionUtility import Postgress
from .Genmst_Appl import Genmst_Appl
from .Genmst import Genmst
from .Obj_Actions import Obj_Actions
from .Obj_Forms import Obj_Forms
from .Obj_Itemchange import Obj_Itemchange
from .Obj_Links import Obj_Links
from .Pophelp import Pophelp
from .Transetup import Transetup
from .Sd_Trans_Design import Sd_Trans_Design
from .GenerateEditMetadataXML import GenerateEditMetadataXML
from .GenerateBrowMetadataXML import GenerateBrowMetadataXML
from .Obj_Attach_Config import Obj_Attach_Config
from .Obj_Followup_Act import Obj_Followup_Act
from .Dynamic_Table_Creation import Dynamic_Table_Creation
from .Function_Defination import Function_Defination
import loggerutility as logger
from flask import request
import traceback
import commonutility as common
from datetime import datetime
import psycopg2
import requests
from loggerutility import deployment_log

class Generate_Transcation:

    def get_database_connection(self, dbDetails): 
        try:       
            if dbDetails['DB_VENDORE'] != None:
                klass = globals()[dbDetails['DB_VENDORE']]
                dbObject = klass()
                connection_obj = dbObject.getConnection(dbDetails)
                    
            return connection_obj
        except (cx_Oracle.Error, psycopg2.Error) as error:
            logger.log(f"Error while database connection")
            deployment_log(f"Error while database connection : {error}")
            raise Exception(f"Error while database connection : {error}")

    def commit(self, connection):
        if connection:
            try:
                connection.commit()
                logger.log(f"Transaction committed successfully.")
            except cx_Oracle.Error as error:
                logger.log(f"Error during commit: {error}")
        else:
            logger.log(f"No active connection to commit.")

    def rollback(self, connection):
        if connection:
            try:
                connection.rollback()
                logger.log(f"Transaction rolled back successfully.")
            except cx_Oracle.Error as error:
                logger.log(f"Error during rollback: {error}")
        else:
            logger.log(f"No active connection to rollback.")

    def close_connection(self, connection):
        if connection:
            try:
                connection.close()
                logger.log(f"Transaction close successfully.")
            except cx_Oracle.Error as error:
                logger.log(f"Error during close: {error}")
        else:
            logger.log(f"No active connection to close.")
        
    def is_valid_json(self, data):
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False
        
    def replace_lookup(self, sql_models, obj_name):
        pattern = r"^\w+\((\w+\s*(,\s*\w+\s*)*)?\)$"
        for sql_model in sql_models:
            if "sql_model" in sql_model and "columns" in sql_model['sql_model']:
                for column in sql_model['sql_model']['columns']:
                    sql_str = column['column']['lookup']
                    if str(sql_str).startswith("SELECT ") and not self.is_valid_json(sql_str):
                        logger.log(f"lookup in if::: {sql_str}")
                        ques_mark_list = sql_str.split("'?'")
                        sql_input_list = []
                        for lst in ques_mark_list:
                            space_list = lst.split(' ')
                            if len(space_list) > 1:
                                sql_input_list.append(f":{space_list[-3].lower()}")

                        sql_input = ','.join(sql_input_list)
                        logger.log(f"sql_str 94 ::: {sql_input}")

                        json_to_replace = {
                            "field_name": (column['column']['db_name']).upper(),
                            "mod_name": ("w_"+obj_name).upper(),
                            "sql_str": sql_str,
                            "dw_object": "", 
                            "msg_title": "",
                            "width": "", 
                            "height": "",
                            "dist_opt": "",
                            "filter_string": "",
                            "sql_input": sql_input,
                            "default_col": 1, 
                            "pop_align": "", 
                            "query_mode": "",
                            "page_context": "", 
                            "pophelp_cols": "", 
                            "pophelp_source": "",
                            "multi_opt": 0, 
                            "help_option": 2, 
                            "popup_xsl_name": "",
                            "auto_fill_len": 2, 
                            "thumb_obj": "", 
                            "thumb_image_col": "",
                            "thumb_alt_col": "", 
                            "auto_min_length": 2, 
                            "obj_name__ds": "",
                            "data_model_name": "", 
                            "validate_data": "", 
                            "item_change": "",
                            "msg_no": "", 
                            "filter_expr": "", 
                            "layout": "",
                            "chg_date": datetime.now().strftime('%d-%m-%y'),
                            "chg_user": "System",
                            "chg_term": "System"
                            } 

                        column['column']['lookup'] = json_to_replace

                    elif str(sql_str).startswith("SQL("):
                        logger.log(f"lookup in elif ::: {sql_str}")
                        before_parenthesis, after_parenthesis = sql_str.split('(', 1)
                        after_parenthesis = after_parenthesis[:-1]
                        logger.log(f"After parenthesis: {after_parenthesis.strip()}")

                        ques_mark_list = after_parenthesis.split(";")
                        sql_str = ques_mark_list[0]
                        sql_input = ques_mark_list[1]
                        logger.log(f"sql_str 106 ::: {sql_str}")
                        logger.log(f"sql_input 106 ::: {sql_input}")

                        json_to_replace = {
                            "field_name": (column['column']['db_name']).upper(),
                            "mod_name": ("w_"+obj_name).upper(),
                            "sql_str": sql_str,
                            "dw_object": "", 
                            "msg_title": "",
                            "width": "", 
                            "height": "",
                            "dist_opt": "",
                            "filter_string": "",
                            "sql_input": sql_input,
                            "default_col": 1, 
                            "pop_align": "", 
                            "query_mode": "",
                            "page_context": "", 
                            "pophelp_cols": "", 
                            "pophelp_source": "",
                            "multi_opt": 0, 
                            "help_option": 2, 
                            "popup_xsl_name": "",
                            "auto_fill_len": 2, 
                            "thumb_obj": "", 
                            "thumb_image_col": "",
                            "thumb_alt_col": "", 
                            "auto_min_length": 2, 
                            "obj_name__ds": "",
                            "data_model_name": "", 
                            "validate_data": "", 
                            "item_change": "",
                            "msg_no": "", 
                            "filter_expr": "", 
                            "layout": "",
                            "chg_date": datetime.now().strftime('%d-%m-%y'),
                            "chg_user": "System",
                            "chg_term": "System"
                            } 

                        column['column']['lookup'] = json_to_replace

                    elif re.match(pattern, sql_str):
                        logger.log(f"lookup matches regex pattern ::: {sql_str}")
                        before_parenthesis, after_parenthesis = sql_str.split('(', 1)
                        before_parenthesis = before_parenthesis.strip()
                        after_parenthesis = after_parenthesis[:-1].strip().replace(" ,",",")
                        logger.log(f"Before parenthesis:rejex {before_parenthesis}")
                        logger.log(f"After parenthesis:rejex {after_parenthesis}")

                        sql_str = f"SELECT {after_parenthesis} FROM {before_parenthesis}"
                        sql_input = ""
                        logger.log(f"sql_str rejex ::: {sql_str}")
                        logger.log(f"sql_input rejex ::: {sql_input}")

                        json_to_replace = {
                            "field_name": (column['column']['db_name']).upper(),
                            "mod_name": ("w_"+obj_name).upper(),
                            "sql_str": sql_str,
                            "dw_object": "", 
                            "msg_title": "",
                            "width": "", 
                            "height": "",
                            "dist_opt": "",
                            "filter_string": "",
                            "sql_input": sql_input,
                            "default_col": 1, 
                            "pop_align": "", 
                            "query_mode": "",
                            "page_context": "", 
                            "pophelp_cols": "", 
                            "pophelp_source": "",
                            "multi_opt": 0, 
                            "help_option": 2, 
                            "popup_xsl_name": "",
                            "auto_fill_len": 2, 
                            "thumb_obj": "", 
                            "thumb_image_col": "",
                            "thumb_alt_col": "", 
                            "auto_min_length": 2, 
                            "obj_name__ds": "",
                            "data_model_name": "", 
                            "validate_data": "", 
                            "item_change": "",
                            "msg_no": "", 
                            "filter_expr": "", 
                            "layout": "",
                            "chg_date": datetime.now().strftime('%d-%m-%y'),
                            "chg_user": "System",
                            "chg_term": "System"
                            } 

                        column['column']['lookup'] = json_to_replace
        return sql_models
    
    def replace_validation(self, sql_models, obj_name, connection, schema_name, con_type):
        for sql_model in sql_models:
            if "sql_model" in sql_model and "columns" in sql_model['sql_model']:
                for column in sql_model['sql_model']['columns']:
                    if "column" in column and "validations" in column['column']:
                        validations_data = column['column']['validations']
                        logger.log(f"Inside validations_lst: {validations_data}")
                        val_lst = []
                        if isinstance(validations_data, list):
                            for str_input in validations_data:
                                if str(str_input).startswith("must_exist"):
                                    fld_name = column['column']['db_name']
                                    fetched_word = str_input.split("'")[1]
                                    logger.log(f"Inside must_exist: {fetched_word}")
                                    error_cd = "V"+str(fld_name[:3].upper())+str(obj_name[:3].upper())+str(fetched_word[:3].upper())

                                    msg_str = f"{str(column['column']['descr'])} does't exists"

                                    json_to_replace = {
                                        "fld_name": fld_name.upper(),
                                        "mod_name": ("w_"+obj_name).upper(),
                                        "descr": msg_str, 
                                        "error_cd": error_cd,
                                        "blank_opt": "N", 
                                        "fld_type": "C",
                                        "fld_min": fetched_word, 
                                        "fld_max": "1", 
                                        "val_type": "L",
                                        "val_table": "", 
                                        "sql_input": "", 
                                        "fld_width": column['column']['width'] if column['column']['width'] else 0,
                                        "udf_usage_1": "", 
                                        "udf_usage_2": "", 
                                        "udf_usage_3": "",
                                        "val_stage": "",
                                        "obj_name": "w_"+obj_name,
                                        "form_no": sql_model['sql_model']['form_no'],
                                        "action": "EDIT", 
                                        "user_id": "System",
                                        "udf_str1_descr": "", 
                                        "udf_str2_descr": "", 
                                        "udf_str3_descr": "",
                                        "exec_seq": "",
                                        "chg_date": datetime.now().strftime('%d-%m-%y'),
                                        "chg_user": "System",
                                        "chg_term": "System"
                                    }
                                    val_lst.append(json_to_replace)

                                elif str(str_input).startswith("business_logic"):
                                    sql_function_name = str_input.split("'")[1]
                                    sql_desc = str_input.split("'")[3]
                                    fld_name = column['column']['db_name']
                                    logger.log(f"Inside business_logic: {sql_function_name}")
                                    logger.log(f"Inside business_logic: {sql_desc}")
                                    error_cd = "V"+str(fld_name[:3].upper())+str(obj_name[:3].upper())+str(sql_function_name[:3].upper())

                                    cursor = connection.cursor()
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
                                        cursor.execute(queryy)
                                        result = cursor.fetchall()
                                        result = result if result != [] else None
                                        logger.log(f"\n result value:::\t{result}")
                                        cursor.close()

                                        if result != None:         
                                            new_res_list = []
                                            question_mark_lst = []
                                            sql_input = ''
                                            sql_str = ''
                                            for i in result:             
                                                first_non_empty = i[0]                        
                                                logger.log(f"\n first_non_empty value:::\t{first_non_empty}") 
                                                if first_non_empty is not None:
                                                    if first_non_empty.startswith("p_") or first_non_empty.startswith("P_"):
                                                        new_res_list.append(f":{sql_model['sql_model']['form_no']}.{first_non_empty[2:].lower()}")
                                                        question_mark_lst.append("?")
                                                    else:
                                                        new_res_list.append(f":{sql_model['sql_model']['form_no']}.{first_non_empty[2:].lower()}")
                                                        question_mark_lst.append("?")
                                            if new_res_list:
                                                sql_input = ",".join(new_res_list)
                                                question_mark = ",".join(question_mark_lst)
                                                sql_str = f"SELECT {sql_function_name}({question_mark}) FROM DUAL"

                                            logger.log(f"\n sql_input:::\t{sql_input}")
                                            logger.log(f"\n sql_str:::\t{sql_str}")

                                            json_to_replace = {
                                                "fld_name": fld_name.upper(),
                                                "mod_name": ("w_"+obj_name).upper(),
                                                "descr": sql_desc, 
                                                "error_cd": error_cd,
                                                "blank_opt": "N", 
                                                "fld_type": "C",
                                                "fld_min": sql_str, 
                                                "fld_max": "0", 
                                                "val_type": "Q",
                                                "val_table": "", 
                                                "sql_input": sql_input, 
                                                "fld_width": column['column']['width'] if column['column']['width'] else 0,
                                                "udf_usage_1": "", 
                                                "udf_usage_2": "", 
                                                "udf_usage_3": "",
                                                "val_stage": "",
                                                "obj_name": "w_"+obj_name,
                                                "form_no": sql_model['sql_model']['form_no'],
                                                "action": "EDIT", 
                                                "user_id": "System",
                                                "udf_str1_descr": "", 
                                                "udf_str2_descr": "", 
                                                "udf_str3_descr": "",
                                                "exec_seq": "",
                                                "chg_date": datetime.now().strftime('%d-%m-%y'),
                                                "chg_user": "System",
                                                "chg_term": "System"
                                            }
                                            val_lst.append(json_to_replace)
                                        else:
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
                                        cursor.execute(queryy)
                                        result = cursor.fetchone()
                                        result = result[0] if result is not None else None
                                        logger.log(f"\n result value:::\t{result}")
                                        cursor.close()

                                        if result != None:
                                            arglst = result.split(',')            
                                            new_res_list = []
                                            question_mark_lst = []
                                            sql_input = ''
                                            sql_str = ''
                                            for i in arglst:             
                                                split_res = i.split(' ')  
                                                first_non_empty = next((item for item in split_res if item), None)                                
                                                logger.log(f"\n first_non_empty value:::\t{first_non_empty}")
                                                if first_non_empty.startswith("p_") or first_non_empty.startswith("P_"):
                                                    new_res_list.append(f":{sql_model['sql_model']['form_no']}.{first_non_empty[2:].lower()}")
                                                    question_mark_lst.append("?")
                                                else:
                                                    new_res_list.append(f":{sql_model['sql_model']['form_no']}.{first_non_empty[2:].lower()}")
                                                    question_mark_lst.append("?")
                                            if new_res_list:
                                                sql_input = ",".join(new_res_list)
                                                question_mark = ",".join(question_mark_lst)
                                                sql_str = f"SELECT {sql_function_name}({question_mark}) FROM DUAL"

                                            logger.log(f"\n sql_input:::\t{sql_input}")
                                            logger.log(f"\n sql_str:::\t{sql_str}")

                                            json_to_replace = {
                                                "fld_name": fld_name.upper(),
                                                "mod_name": ("w_"+obj_name).upper(),
                                                "descr": sql_desc, 
                                                "error_cd": error_cd,
                                                "blank_opt": "N", 
                                                "fld_type": "C",
                                                "fld_min": sql_str, 
                                                "fld_max": "0", 
                                                "val_type": "Q",
                                                "val_table": "", 
                                                "sql_input": sql_input, 
                                                "fld_width": column['column']['width'] if column['column']['width'] else 0,
                                                "udf_usage_1": "", 
                                                "udf_usage_2": "", 
                                                "udf_usage_3": "",
                                                "val_stage": "",
                                                "obj_name": "w_"+obj_name,
                                                "form_no": sql_model['sql_model']['form_no'],
                                                "action": "EDIT", 
                                                "user_id": "System",
                                                "udf_str1_descr": "", 
                                                "udf_str2_descr": "", 
                                                "udf_str3_descr": "",
                                                "exec_seq": "",
                                                "chg_date": datetime.now().strftime('%d-%m-%y'),
                                                "chg_user": "System",
                                                "chg_term": "System"
                                            }
                                            val_lst.append(json_to_replace)
                                        else:
                                            raise Exception(f"Function {sql_function_name} definition is not found, so please execute the function and then upload the model json.")

                        else:
                            str_input = validations_data
                            if str(str_input).startswith("must_exist"):
                                fld_name = column['column']['db_name']
                                fetched_word = str_input.split("'")[1]
                                logger.log(f"Inside must_exist: {fetched_word}")
                                error_cd = "V"+str(fld_name[:3].upper())+str(obj_name[:3].upper())+str(fetched_word[:3].upper())

                                msg_str = f"{str(column['column']['descr'])} does't exists"

                                json_to_replace = {
                                    "fld_name": fld_name.upper(),
                                    "mod_name": ("w_"+obj_name).upper(),
                                    "descr": msg_str, 
                                    "error_cd": error_cd,
                                    "blank_opt": "N", 
                                    "fld_type": "C",
                                    "fld_min": fetched_word, 
                                    "fld_max": "1", 
                                    "val_type": "L",
                                    "val_table": "", 
                                    "sql_input": "", 
                                    "fld_width": column['column']['width'] if column['column']['width'] else 0,
                                    "udf_usage_1": "", 
                                    "udf_usage_2": "", 
                                    "udf_usage_3": "",
                                    "val_stage": "",
                                    "obj_name": "w_"+obj_name,
                                    "form_no": sql_model['sql_model']['form_no'],
                                    "action": "EDIT", 
                                    "user_id": "System",
                                    "udf_str1_descr": "", 
                                    "udf_str2_descr": "", 
                                    "udf_str3_descr": "",
                                    "exec_seq": "",
                                    "chg_date": datetime.now().strftime('%d-%m-%y'),
                                    "chg_user": "System",
                                    "chg_term": "System"
                                }
                                val_lst.append(json_to_replace)

                            elif str(str_input).startswith("business_logic"):
                                sql_function_name = str_input.split("'")[1]
                                sql_desc = str_input.split("'")[3]
                                fld_name = column['column']['db_name']
                                logger.log(f"Inside business_logic: {sql_function_name}")
                                logger.log(f"Inside business_logic: {sql_desc}")
                                error_cd = "V"+str(fld_name[:3].upper())+str(obj_name[:3].upper())+str(sql_function_name[:3].upper())

                                cursor = connection.cursor()
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
                                    cursor.execute(queryy)
                                    result = cursor.fetchall()
                                    result = result if result != [] else None
                                    logger.log(f"\n result value:::\t{result}")
                                    cursor.close()

                                    if result != None:
                                        new_res_list = []
                                        question_mark_lst = []
                                        sql_input = ''
                                        sql_str = ''
                                        for i in result:             
                                            first_non_empty = i[0]                        
                                            logger.log(f"\n first_non_empty value:::\t{first_non_empty}") 
                                            if first_non_empty is not None:
                                                if first_non_empty.startswith("p_") or first_non_empty.startswith("P_"):
                                                    new_res_list.append(first_non_empty[2:].upper())
                                                    question_mark_lst.append("?")
                                                else:
                                                    new_res_list.append(first_non_empty.upper())
                                                    question_mark_lst.append("?")
                                        if new_res_list:
                                            sql_input = ",".join(new_res_list)
                                            question_mark = ",".join(question_mark_lst)
                                            sql_str = f"SELECT {sql_function_name}({question_mark}) FROM DUAL"

                                        logger.log(f"\n sql_input:::\t{sql_input}")
                                        logger.log(f"\n sql_str:::\t{sql_str}")

                                        json_to_replace = {
                                            "fld_name": fld_name.upper(),
                                            "mod_name": ("w_"+obj_name).upper(),
                                            "descr": sql_desc, 
                                            "error_cd": error_cd,
                                            "blank_opt": "N", 
                                            "fld_type": "C",
                                            "fld_min": sql_str, 
                                            "fld_max": "0", 
                                            "val_type": "Q",
                                            "val_table": "", 
                                            "sql_input": sql_input, 
                                            "fld_width": column['column']['width'] if column['column']['width'] else 0,
                                            "udf_usage_1": "", 
                                            "udf_usage_2": "", 
                                            "udf_usage_3": "",
                                            "val_stage": "",
                                            "obj_name": "w_"+obj_name,
                                            "form_no": sql_model['sql_model']['form_no'],
                                            "action": "EDIT", 
                                            "user_id": "System",
                                            "udf_str1_descr": "", 
                                            "udf_str2_descr": "", 
                                            "udf_str3_descr": "",
                                            "exec_seq": "",
                                            "chg_date": datetime.now().strftime('%d-%m-%y'),
                                            "chg_user": "System",
                                            "chg_term": "System"
                                        }
                                        val_lst.append(json_to_replace)
                                    else:
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
                                    cursor.execute(queryy)
                                    result = cursor.fetchone()
                                    result = result[0] if result is not None else None
                                    logger.log(f"\n result value:::\t{result}")
                                    cursor.close()

                                    if result != None:
                                        arglst = result.split(',')            
                                        new_res_list = []
                                        question_mark_lst = []
                                        sql_input = ''
                                        sql_str = ''
                                        for i in arglst:             
                                            split_res = i.split(' ')  
                                            first_non_empty = next((item for item in split_res if item), None)                                
                                            logger.log(f"\n first_non_empty value:::\t{first_non_empty}")
                                            if first_non_empty.startswith("p_") or first_non_empty.startswith("P_"):
                                                new_res_list.append(first_non_empty[2:].upper())
                                                question_mark_lst.append("?")
                                            else:
                                                new_res_list.append(first_non_empty.upper())
                                                question_mark_lst.append("?")
                                        if new_res_list:
                                            sql_input = ",".join(new_res_list)
                                            question_mark = ",".join(question_mark_lst)
                                            sql_str = f"SELECT {sql_function_name}({question_mark}) FROM DUAL"

                                        logger.log(f"\n sql_input:::\t{sql_input}")
                                        logger.log(f"\n sql_str:::\t{sql_str}")

                                        json_to_replace = {
                                            "fld_name": fld_name.upper(),
                                            "mod_name": ("w_"+obj_name).upper(),
                                            "descr": sql_desc, 
                                            "error_cd": error_cd,
                                            "blank_opt": "N", 
                                            "fld_type": "C",
                                            "fld_min": sql_str, 
                                            "fld_max": "0", 
                                            "val_type": "Q",
                                            "val_table": "", 
                                            "sql_input": sql_input, 
                                            "fld_width": column['column']['width'] if column['column']['width'] else 0,
                                            "udf_usage_1": "", 
                                            "udf_usage_2": "", 
                                            "udf_usage_3": "",
                                            "val_stage": "",
                                            "obj_name": "w_"+obj_name,
                                            "form_no": sql_model['sql_model']['form_no'],
                                            "action": "EDIT", 
                                            "user_id": "System",
                                            "udf_str1_descr": "", 
                                            "udf_str2_descr": "", 
                                            "udf_str3_descr": "",
                                            "exec_seq": "",
                                            "chg_date": datetime.now().strftime('%d-%m-%y'),
                                            "chg_user": "System",
                                            "chg_term": "System"
                                        }
                                        val_lst.append(json_to_replace)
                                    else:
                                        raise Exception(f"Function {sql_function_name} definition is not found, so please execute the function and then upload the model json.")

                        column['column']['validations'] = val_lst
        return sql_models
    
    def replace_obj_itemchange(self,sql_models, object_name):
        try:
            for sql_model in sql_models:
                form_no = sql_model['sql_model'].get('form_no', '') 

                if "sql_model" in sql_model and "columns" in sql_model['sql_model']:
                    for column in sql_model['sql_model']['columns']:
                        if "column" in column and "item_change" in column['column']:
                            item_change = column['column']['item_change']

                            if self.is_valid_json(item_change):
                                obj_name = object_name  
                                field_name = column['column'].get('db_name', '')
                                mandatory = item_change.get('mandatory_server', '')

                                if mandatory.lower() == "yes":
                                    mandatory = "Y"
                                elif mandatory.lower() == "no":
                                    mandatory = "N"

                                exec_at = item_change.get('itemchange_type', '')
                                if exec_at.lower() == "local":
                                    exec_at = "L"
                                elif exec_at.lower() == "server":
                                    exec_at = "Z"

                                js_arg = item_change.get('local_file_name', '')

                                output_data = {
                                    'obj_name': obj_name,
                                    'form_no': form_no,
                                    'field_name': field_name,
                                    'mandatory': mandatory,
                                    'exec_at': exec_at,
                                    'js_arg': js_arg
                                }
                                column['column']['item_change'] = output_data
            return sql_models

        except Exception as e:
            logger.log(f"Error in replace_obj_itemchange: {str(e)}")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'Exception: {returnErr}', "0")
            return str(returnErr)
        
    def get_model_from_schema_name(self):

        schema_name          = ''
        object_name          = ''
        dbDetails            = ''
        transaction_model    = ''
        connection           = None
        token_id             = ''

        jsondata =  request.get_data('jsonData', None)
        jsondata =  json.loads(jsondata[9:])
        logger.log(f"\nJsondata inside Generate_Transcation class:::\t{jsondata} \t{type(jsondata)}","0")
        
        if "dbDetails" in jsondata and jsondata["dbDetails"] != None:
            dbDetails = jsondata["dbDetails"]
            logger.log(f"\nInside dbDetails value:::\t{dbDetails} \t{type(dbDetails)}","0")
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Missing dbDetails value")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            deployment_log(f"{descr}")
            return str(returnErr)
        
        if "object_name" in jsondata and jsondata["object_name"] != None:
            object_name = jsondata["object_name"].lower()
            logger.log(f"\nInside object_name value:::\t{object_name} \t{type(object_name)}","0")
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Missing object_name value")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            deployment_log(f"{descr}")
            return str(returnErr)

        if "schema_name" in jsondata and jsondata["schema_name"] != None:
            schema_name = jsondata["schema_name"]
            logger.log(f"\nInside schema_name value:::\t{schema_name} \t{type(schema_name)}","0")
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Missing schema_name value")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            deployment_log(f"{descr}")
            return str(returnErr)

        if "token_id" in jsondata and jsondata["token_id"] != None:
            token_id = jsondata["token_id"]
            logger.log(f"\nInside token_id value:::\t{token_id} \t{type(token_id)}","0")

        connection = self.get_database_connection(dbDetails)
        if connection:

            logger.log(f"Inside connection")
            sql = f"SELECT SCHEMA_MODEL FROM sd_trans_design WHERE schema_name='{schema_name}'"
            logger.log(f"Class Generate_Transcation select queryy::: {sql}")
            cursor = connection.cursor()
            cursor.execute(sql)
            result_lst = cursor.fetchall()
            logger.log(f"result_lst :::::249 {result_lst} {type(result_lst)}")

            if result_lst:
                clob_data = result_lst[0][0]  
                if clob_data is not None:
                    transaction_model = json.loads(clob_data.read())
                    logger.log(f"Schema Model Data:\n{transaction_model}")
                else:
                    return f"No CLOB data found for the given schema_name."
            else:
                return f"No results returned from the query."            
            cursor.close()
        
        return dbDetails, object_name, schema_name, transaction_model, token_id

    def enhancement_in_model(self, transaction_model, object_name, connection, schema_name, db_vendore):
        form_one_actions = []
        sql_models = transaction_model["transaction"]["sql_models"]

        sql_models = self.sort_model_columns(sql_models)

        sql_models = self.replace_lookup(sql_models, object_name)
        sql_models = self.replace_validation(sql_models, object_name, connection, schema_name, db_vendore)
        sql_models = self.replace_obj_itemchange(sql_models, object_name)

        if "actions" in transaction_model["transaction"]:
            form_one_actions = transaction_model["transaction"]["actions"]
            logger.log(f"form_one_actions list ::: {form_one_actions}")

        sql_models = self.update_obj_actions(sql_models, object_name, form_one_actions)
        sql_models = self.update_obj_links(sql_models, object_name)

        transaction_model["transaction"]["sql_models"] = sql_models

        if "attach_docs" in transaction_model:
            attach_docs = transaction_model['attach_docs']
            transaction_model['attach_docs'] = self.update_attach_docs(attach_docs, object_name)

        return transaction_model

    def sort_model_columns(self, sql_models):
        for sql_model in sql_models:
            if "sql_model" in sql_model and "columns" in sql_model['sql_model']:
                columns = sql_model['sql_model']['columns']
                sorted_data = sorted(
                    columns,
                    key=lambda x: (
                        0 if x['column']['group_name'].lower() == 'basic' else 
                        2 if x['column']['group_name'].lower() == 'others' else 
                        1,
                        x['column']['group_name']
                    )
                )
                logger.log(f"columns to sorted ::: {sorted_data}")
                sql_model['sql_model']['columns'] = sorted_data
        return sql_models
    
    def update_attach_docs(self, attach_docs, object_name):
        new_attach_docs = []
        for attach_doc in attach_docs:
            json_to_replace = {
                "obj_name": object_name,  
                "doc_type": attach_doc,  
                "file_type": "", 
                "min_attach_req": "",  
                "max_attach_allow": "", 
                "attach_mode": "",
                "remarks": "",  
                "chg_date": datetime.now().strftime('%d-%m-%y'),  
                "chg_user": "System", 
                "chg_term": "System", 
                "no_attachments": "", 
                "no_comments": "", 
                "descr_req": "", 
                "doc_purpose": "",  
                "max_size_mb": "",  
                "max_file_size": "", 
                "track_validity": "",  
                "allow_download": "",  
                "extract_prc": "", 
                "show_del_attach": "",  
                "extract_templ": "", 
                "disply_order": "", 
                "meta_data_def": ""  
            }
            new_attach_docs.append(json_to_replace)

        return new_attach_docs
    
    def update_obj_actions(self, sql_models,object_name, form_one_actions):
        self.line_no = 1
        for sql_model in sql_models:
            actions_details = [] 
            if "sql_model" in sql_model and "actions_links" in sql_model['sql_model']:
                logger.log("Inside actions_links")
                for actions_links_json in sql_model['sql_model']['actions_links']:
                    if actions_links_json['type'].upper() == 'ACTION':
                        actions_links_json['obj_name'] = object_name
                        actions_details.append(actions_links_json)
                logger.log(f"actions_details for action::: {actions_details}")
                sql_model['sql_model']['action'] = {}
                sql_model['sql_model']['action'] = actions_details
            else:
                form_no = sql_model['sql_model']['form_no']

                logger.log("Outside actions_links and else")

                action_json = {}
                action_json_file = 'obj_actions_json_file.json'
                with open(action_json_file, 'r') as json_file:
                    action_json = json.load(json_file)

                if (form_no == '1' or form_no == 1):
                    logger.log("Outside actions_links and inside form no 1")
                    actions_lst = []
                    if "action" in sql_model['sql_model']:
                        actions_lst = sql_model['sql_model'].get('action', [])
                    extracted_actions_of_check_lst = [item.split(':')[0] for item in actions_lst]
                    extracted_actions_of_formone = [item.split(':')[0] for item in form_one_actions]
                    logger.log(f"extracted_actions_of_check_lst ::: {extracted_actions_of_check_lst}")
                    logger.log(f"extracted_actions_of_formone ::: {extracted_actions_of_formone}")
                    if len(extracted_actions_of_formone) > 0:
                        for index, action in enumerate(extracted_actions_of_formone):
                            if action.title() in action_json:
                                logger.log(f"Inside action_json :: {actions_details}")
                                data = action_json[action.title()] 
                                data["obj_name"] = object_name
                                data["line_no"] = self.line_no
                                data["form_no"] = form_no
                                data["chg_date"] = datetime.now().strftime('%d-%m-%y')
                                data["chg_term"] = "System"
                                data["chg_user"] = "System"
                                data["actual_func"] = form_one_actions[index]
                                if action in extracted_actions_of_check_lst:
                                    data["page_context"] = 1
                                actions_details.append(data)
                                self.line_no += 1 
                            else:
                                logger.log(f"Inside action_json :: {actions_details}")
                                data = action_json["Default"] 
                                data_copy = data.copy()
                                data_copy["obj_name"] = object_name
                                data_copy["line_no"] = self.line_no
                                data_copy["form_no"] = form_no
                                data_copy["chg_date"] = datetime.now().strftime('%d-%m-%y')
                                data_copy["chg_term"] = "System"
                                data_copy["chg_user"] = "System"
                                data_copy["actual_func"] = form_one_actions[index]

                                data_copy["title"] = action.title()
                                actions_details.append(data_copy)
                                self.line_no += 1 

                        logger.log(f"Outside action_json :: {actions_details}")
                        sql_model['sql_model']['action'] = actions_details 
                    else:
                        for index, action in enumerate(extracted_actions_of_check_lst):
                            if action.title() in action_json:
                                data = action_json[action.title()] 
                                data["obj_name"] = object_name
                                data["line_no"] = self.line_no
                                data["form_no"] = form_no
                                data["chg_date"] = datetime.now().strftime('%d-%m-%y')
                                data["chg_term"] = "System"
                                data["chg_user"] = "System"
                                data["actual_func"] = actions_lst[index]

                                actions_details.append(data)
                                self.line_no += 1  
                        sql_model['sql_model']['action'] = actions_details
                else:
                    if "action" in sql_model['sql_model']:
                        actions_lst = sql_model['sql_model'].get('action', [])
                        for action in actions_lst:
                            if action.title() in action_json:
                                data = action_json[action.title()] 
                                data["obj_name"] = object_name
                                data["line_no"] = self.line_no
                                data["form_no"] = form_no
                                data["chg_date"] = datetime.now().strftime('%d-%m-%y')
                                data["chg_term"] = "System"
                                data["chg_user"] = "System"
                                data["actual_func"] = action

                                actions_details.append(data)
                                self.line_no += 1  

                    sql_model['sql_model']['action'] = actions_details

        return sql_models 
    
    def update_obj_links(self, sql_models,object_name):
        line_no_link = 1

        for sql_model in sql_models:
            links_details = []
            if "sql_model" in sql_model and "actions_links" in sql_model['sql_model']:
                logger.log("inside if")
                for actions_links_json in sql_model['sql_model']['actions_links']:
                    if actions_links_json['type'].upper() == 'LINK':
                        actions_links_json['obj_name'] = object_name
                        links_details.append(actions_links_json)
                logger.log(f"actions_details for links::: {links_details}")
                sql_model['sql_model']['links'] = {}
                sql_model['sql_model']['links'] = links_details
            else:
                logger.log("action_links not found in sql_models")       
                links = sql_model['sql_model'].get('links', [])
                form_no = sql_model['sql_model'].get('form_no', "")
                
                if links:
                    logger.log(f"links data: {links}")

                if form_no:
                    logger.log(f"Form Number: {form_no}")
                link_json = {}
                link_json_file = 'obj_links_file_json.json'
                with open(link_json_file, 'r') as json_file:
                    link_json = json.load(json_file)

                for link in links:
                    data = link_json[link.title()] 

                    data_copy = data.copy()
                    data_copy["obj_name"] = object_name
                    data_copy["line_no"] = line_no_link
                    data_copy["form_no"] = form_no

                    logger.log(f"Updated data copy: {data_copy}")
                    links_details.append(data_copy)
                    logger.log(f"line_no_link: {line_no_link}")
                    logger.log(f"links_details: {links_details}")
                    line_no_link += 1  
                
                sql_model['sql_model']['links'] = links_details

        return sql_models
        
    def genearate_transaction(self, transaction_model, object_name, connection, schema_name, db_vendore):

        sql_models = transaction_model["transaction"]["sql_models"] 

        genmst = Genmst()
        genmst.process_data(connection, sql_models, db_vendore, ("w_"+object_name).upper())

        obj_actions = Obj_Actions()
        obj_actions.process_data(connection, sql_models, schema_name, db_vendore, object_name)

        obj_forms = Obj_Forms()
        obj_forms.process_data(connection, sql_models, object_name, db_vendore)

        obj_links = Obj_Links()
        obj_links.process_data(connection, sql_models, db_vendore)

        pophelp = Pophelp()
        pophelp.process_data(connection, sql_models, db_vendore)

        transetup = Transetup()
        transetup.process_data(connection, sql_models, object_name, db_vendore)

        obj_itemchange = Obj_Itemchange()
        obj_itemchange.process_data(connection, sql_models, object_name, schema_name, db_vendore)

        if "attach_docs" in transaction_model:
            attach_docs = transaction_model["attach_docs"]
            
            obj_attach_config = Obj_Attach_Config()
            obj_attach_config.process_data(connection, attach_docs, db_vendore)

        if "follow_up_actions" in transaction_model["transaction"]:
            follow_up_actions = transaction_model["transaction"]["follow_up_actions"]

            obj_followup_act = Obj_Followup_Act()
            obj_followup_act.process_data(connection, follow_up_actions, object_name, db_vendore)

        generatebrowmetadataXML = GenerateBrowMetadataXML()
        generatebrowmetadataXML.jsonData = transaction_model
        result = generatebrowmetadataXML.build_xml_str(object_name)
        logger.log(f"{result}")
        deployment_log(f"{result}")

        generateeditmetadataXML = GenerateEditMetadataXML()
        generateeditmetadataXML.jsonData = transaction_model
        result = generateeditmetadataXML.build_xml_str(object_name)
        logger.log(f"{result}")
        deployment_log(f"{result}")

    def genearate_transaction_with_model(self):

        logger.log(f"\n\n {'-' * 55 }  Object deployment service started {'-' * 55 }  \n\n")
        deployment_log(f"\n\n {'-' * 55 }  Object deployment service started {'-' * 55 }  \n\n")

        schema_name          = ''
        object_name          = ''
        dbDetails            = ''
        transaction_model    = ''
        user_info            = ''
        connection           = None
        token_id             = ''
        function_sql         = ''

        jsondata =  request.get_data('jsonData', None)
        jsondata =  json.loads(jsondata[9:])
        logger.log(f"\nJsondata inside Generate_Transcation class:::\t{jsondata} \t{type(jsondata)}","0")

        if "transaction_model" in jsondata and jsondata["transaction_model"] != None:
            transaction_model = jsondata["transaction_model"]
            logger.log(f"\nInside transaction_model value:::\t{transaction_model} \t{type(transaction_model)}","0")
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Missing transaction_model value")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            deployment_log(f"{descr}")
            return str(returnErr)
        
        if "dbDetails" in jsondata and jsondata["dbDetails"] != None:
            dbDetails = jsondata["dbDetails"]
            logger.log(f"\nInside dbDetails value:::\t{dbDetails} \t{type(dbDetails)}","0")
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Missing dbDetails value")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            deployment_log(f"{descr}")
            return str(returnErr)
        
        logger.log(f'transaction_model_check type:: {type(transaction_model)}')
        transaction_model_check = json.loads(json.dumps(transaction_model))
        if "transaction" in transaction_model_check and "obj_name" in transaction_model_check["transaction"] and transaction_model_check["transaction"]["obj_name"] != None:
            object_name = transaction_model_check["transaction"]["obj_name"].lower()
            logger.log(f"\nInside object_name value:::\t{object_name} \t{type(object_name)}","0")
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Missing object_name value")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            deployment_log(f"{descr}")
            return str(returnErr)

        if "schema_name" in jsondata and jsondata["schema_name"] != None:
            schema_name = jsondata["schema_name"]
            logger.log(f"\nInside schema_name value:::\t{schema_name} \t{type(schema_name)}","0")
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Missing schema_name value")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            deployment_log(f"{descr}")
            return str(returnErr)

        if "user_info" in jsondata and jsondata["user_info"] != None:
            user_info = jsondata["user_info"]
            logger.log(f"\nInside user_info value:::\t{user_info} \t{type(user_info)}","0")

        if "token_id" in jsondata and jsondata["token_id"] != None:
            token_id = jsondata["token_id"]
            logger.log(f"\nInside token_id value:::\t{token_id} \t{type(token_id)}","0")

        if "function_defination" in jsondata and jsondata["function_defination"] != None:
            function_sql = jsondata["function_defination"]
            logger.log(f"\nInside function_sql value:::\t{function_sql} \t{type(function_sql)}","0")

        deployment_log(f"Database details ::: {dbDetails}")
        connection = self.get_database_connection(dbDetails)
        deployment_log(f"Database connection created ::: {connection}")
        logger.log(f"\nInside Owner name:::\t{dbDetails['SCHEMA_NAME']} \t{type(dbDetails['SCHEMA_NAME'])}","0")

        if connection:
            try:
                token_status = common.validate_token(connection, token_id)
                deployment_log(f"Token validation status ::: {token_status}")

                if token_status == "active":

                    deployment_log(f"Object processing start...")
                    dynamic_table_creation = Dynamic_Table_Creation()
                    dynamic_table_creation.create_alter_table(transaction_model, connection, dbDetails['SCHEMA_NAME'], dbDetails['DB_VENDORE'])

                    function_defination = Function_Defination()
                    function_defination.execute_function(function_sql, connection)

                    enhanced_model = self.enhancement_in_model(transaction_model, object_name, connection, dbDetails['SCHEMA_NAME'], dbDetails['DB_VENDORE'])
                    logger.log(f"enhanced_model:: {enhanced_model}")
                    self.genearate_transaction(enhanced_model, object_name, connection, dbDetails['SCHEMA_NAME'], dbDetails['DB_VENDORE'])

                    sd_trans_design = Sd_Trans_Design()
                    sd_trans_design.process_data(connection, user_info, {'schema_name': schema_name,'schema_model': json.dumps(enhanced_model)}, dbDetails['DB_VENDORE'])

                    self.commit(connection)
                    deployment_log(f"Changes commited")

                    trace = traceback.format_exc()
                    descr = str("Transaction Deployed Successfully.")
                    returnErr = common.getErrorXml(descr, trace)
                    logger.log(f'\n Exception ::: {returnErr}', "0")
                    deployment_log(f"{descr}")
                    return str(returnErr)
                
                elif token_status == "inactive":
                    trace = traceback.format_exc()
                    descr = str("Token Id is not Active.")
                    returnErr = common.getErrorXml(descr, trace)
                    logger.log(f'\n Exception ::: {returnErr}', "0")
                    deployment_log(f"{descr}")
                    return str(returnErr)
                else:
                    trace = traceback.format_exc()
                    descr = str("Invalid Token Id.")
                    returnErr = common.getErrorXml(descr, trace)
                    logger.log(f'\n Exception ::: {returnErr}', "0")
                    deployment_log(f"{descr}")
                    return str(returnErr)
        
            except Exception as e:
                logger.log(f"Rollback successfully.")
                self.rollback(connection)
                logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
                trace = traceback.format_exc()
                descr = str(e)
                returnErr = common.getErrorXml(descr, trace)
                logger.log(f'\n Exception ::: {returnErr}', "0")
                deployment_log(f"Exception in Object deployment process ::: {descr}")
                deployment_log(f"Rollback changes")
                return str(returnErr)
            finally:
                logger.log('Closed connection successfully')
                deployment_log("Closed connection successfully.")
                self.close_connection(connection)
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Connection fail")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            deployment_log(f"Exception ::: {descr}")
            return str(returnErr)
        
    def genearate_transaction_with_schema(self): 

        logger.log(f"\n\n {'-' * 55 }  Object deployment service started {'-' * 55 }  \n\n")
        deployment_log(f"\n\n {'-' * 55 }  Object deployment service started {'-' * 55 }  \n\n")

        connection           = None
        try:
            dbDetails, object_name, schema_name, transaction_model, token_id = self.get_model_from_schema_name()
            connection = self.get_database_connection(dbDetails)
        except Exception as e:
            self.rollback(connection)
            trace = traceback.format_exc()
            returnErr = common.getErrorXml(str(e), trace)
            deployment_log(f"{str(e)}")
            return str(returnErr)

        if connection:
            try:
                token_status = common.validate_token(connection, token_id)

                if token_status == "active":

                    enhanced_model = self.enhancement_in_model(transaction_model, object_name, dbDetails['SCHEMA_NAME'])
                    self.genearate_transaction(enhanced_model, object_name, connection, dbDetails['SCHEMA_NAME'])

                    self.commit(connection)
                    deployment_log(f"Changes commited")

                    trace = traceback.format_exc()
                    descr = str("Transaction Deployed Successfully.")
                    returnErr = common.getErrorXml(descr, trace)
                    logger.log(f'\n Exception ::: {returnErr}', "0")
                    deployment_log(f"{descr}")
                    return str(returnErr)
                
                elif token_status == "inactive":
                    trace = traceback.format_exc()
                    descr = str("Token Id is not Active.")
                    returnErr = common.getErrorXml(descr, trace)
                    logger.log(f'\n Exception ::: {returnErr}', "0")
                    deployment_log(f"{descr}")
                    return str(returnErr)
                else:
                    trace = traceback.format_exc()
                    descr = str("Invalid Token Id.")
                    returnErr = common.getErrorXml(descr, trace)
                    logger.log(f'\n Exception ::: {returnErr}', "0")
                    deployment_log(f"{descr}")
                    return str(returnErr)
        
            except Exception as e:
                logger.log(f"Rollback successfully.")
                self.rollback(connection)
                logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
                trace = traceback.format_exc()
                descr = str(e)
                returnErr = common.getErrorXml(descr, trace)
                logger.log(f'\n Exception ::: {returnErr}', "0")
                deployment_log(f"Exception in Object deployment process ::: {descr}")
                deployment_log(f"Rollback changes")
                return str(returnErr)
            finally:
                logger.log('Closed connection successfully')
                deployment_log("Closed connection successfully.")
                self.close_connection(connection)
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Connection fail")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            deployment_log(f"Exception ::: {descr}")
            return str(returnErr)  

    def deploy_transaction_metadata(self):        
        data = request.get_json()

        headers1 = data.get("headers1")
        file_lst = data.get("file_lst")
        filePath = data.get("filePath")
        app_id = data.get("app_id")
        token_id = data.get("token_id")
        url = data.get("url")

        try:
            for fileName in file_lst:

                file = open(filePath + fileName, "r")
                xml_file_content = file.read()
                file.close()

                new_payload = {
                    "FILE_NAME": fileName,
                    "FILE_CONTENT":xml_file_content,
                    "APP_ID": app_id,
                    "TOKEN_ID": token_id
                }
                
                response1 = requests.post(url, headers=headers1, data=new_payload)

                logger.log(f"{response1.text}")

            return "Transaction Metadata Deployed Successfully."
        except Exception as e:
            return e   
   
        
           
   