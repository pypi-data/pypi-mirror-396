import cx_Oracle
from datetime import datetime
import loggerutility as logger
from loggerutility import deployment_log

class Pophelp:
    
    sql_models = []

    def check_or_update_pophelp(self, lookup, connection, con_type):

        required_keys = [
            'field_name', 'mod_name'
        ]

        missing_keys = [key for key in required_keys if key not in lookup]

        if missing_keys:
            deployment_log(f"Missing required keys for POPHELP table: {', '.join(missing_keys)}")
            raise KeyError(f"Missing required keys for pophelp table: {', '.join(missing_keys)}")
        else:
            field_name = lookup.get('field_name', '') or None
            mod_name = lookup.get('mod_name', '').upper() or None
            sql_str = lookup.get('sql_str', '') or None
            dw_object = lookup.get('dw_object', '') or None
            msg_title = lookup.get('msg_title', '') or None
            width = lookup.get('width', '') or 0
            height = lookup.get('height', '') or 0
            chg_date = datetime.now().strftime('%d-%m-%y')
            chg_user = lookup.get('chg_user', '').strip() or 'System'
            chg_term = lookup.get('chg_term', '').strip() or 'System'
            dist_opt = lookup.get('dist_opt', '') or None
            filter_string = lookup.get('filter_string', '') or None
            sql_input = lookup.get('sql_input', '') or None

            logger.log(f"pophelp sql_str :: {sql_str}")
            default_col = 2
            if sql_str != None:
                select_index = sql_str.upper().find("SELECT ") + len("SELECT ")
                from_index = sql_str.upper().find(" FROM ")
                select_columns_str = sql_str[select_index:from_index].strip().split(',')
                for index, col in enumerate(select_columns_str):
                    col = col.strip().upper()
                    if ' AS ' in col:
                        logger.log(f"In pophelp sql_column name :: {col.split(' AS ')[0].strip()}")
                        if field_name.upper() == col.split(' AS ')[0].strip():
                            default_col = index + 1
                    else:
                        logger.log(f"In pophelp sql_column name :: {col.strip()}")
                        if field_name.upper() == col.strip():
                            default_col = index + 1
            logger.log(f"pophelp field_name :: {field_name}")
            logger.log(f"pophelp default_col :: {default_col}")
            deployment_log(f"POPHELP table field_name ::: {field_name}")
            deployment_log(f"POPHELP table default_col ::: {default_col}")

            pop_align = lookup.get('pop_align', '') or None
            query_mode = lookup.get('query_mode', '') or None
            page_context = lookup.get('page_context', '') or None
            pophelp_cols = lookup.get('pophelp_cols', '') or None
            pophelp_source = lookup.get('pophelp_source', '') or None
            multi_opt = lookup.get('multi_opt', '') or 0
            help_option = lookup.get('help_option', '') or None
            popup_xsl_name = lookup.get('popup_xsl_name', '') or None
            auto_fill_len = lookup.get('auto_fill_len', '') or None
            thumb_obj = lookup.get('thumb_obj', '') or None
            thumb_image_col = lookup.get('thumb_image_col', '') or None
            thumb_alt_col = lookup.get('thumb_alt_col', '') or None
            auto_min_length = lookup.get('auto_min_length', '') or None
            obj_name__ds = lookup.get('obj_name__ds', '') or None
            data_model_name = lookup.get('data_model_name', '') or None
            validate_data = lookup.get('validate_data', '') or None
            item_change = lookup.get('item_change', '') or None
            msg_no = lookup.get('msg_no', '') or None
            filter_expr = lookup.get('filter_expr', '') or None
            layout = lookup.get('layout', '') or None

            cursor = connection.cursor()
            deployment_log(f"POPHELP table select query ::: SELECT COUNT(*) FROM pophelp WHERE FIELD_NAME = '{field_name}' AND MOD_NAME = '{mod_name}'")
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM pophelp 
                WHERE FIELD_NAME = '{field_name}' AND MOD_NAME = '{mod_name}'
            """)
            count = cursor.fetchone()[0]
            deployment_log(f"POPHELP table select query result ::: {count}")
            cursor.close()

            if count > 0:
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    update_query = """
                        UPDATE pophelp SET
                        SQL_STR = :sql_str, DW_OBJECT = :dw_object, 
                        MSG_TITLE = :msg_title, WIDTH = :width, HEIGHT = :height, 
                        CHG_DATE = TO_DATE(:chg_date, 'DD-MM-YYYY'), CHG_USER = :chg_user, 
                        CHG_TERM = :chg_term, DIST_OPT = :dist_opt, FILTER_STRING = :filter_string, 
                        SQL_INPUT = :sql_input, DEFAULT_COL = :default_col, POP_ALIGN = :pop_align, 
                        QUERY_MODE = :query_mode, PAGE_CONTEXT = :page_context, 
                        POPHELP_COLS = :pophelp_cols, POPHELP_SOURCE = :pophelp_source, 
                        MULTI_OPT = :multi_opt, HELP_OPTION = :help_option, 
                        POPUP_XSL_NAME = :popup_xsl_name, AUTO_FILL_LEN = :auto_fill_len, 
                        THUMB_OBJ = :thumb_obj, THUMB_IMAGE_COL = :thumb_image_col, 
                        THUMB_ALT_COL = :thumb_alt_col, AUTO_MIN_LENGTH = :auto_min_length, 
                        OBJ_NAME__DS = :obj_name__ds, DATA_MODEL_NAME = :data_model_name, 
                        VALIDATE_DATA = :validate_data, ITEM_CHANGE = :item_change, 
                        MSG_NO = :msg_no, FILTER_EXPR = :filter_expr, LAYOUT = :layout
                        WHERE FIELD_NAME = :field_name AND MOD_NAME = :mod_name
                    """
                    values = {
                        'field_name': field_name, 'mod_name': mod_name, 'sql_str': sql_str, 'dw_object': dw_object, 'msg_title': msg_title, 'width': width, 'height': height,
                        'chg_date': chg_date, 'chg_user': chg_user, 'chg_term': chg_term, 'dist_opt': dist_opt, 'filter_string': filter_string, 'sql_input': sql_input,
                        'default_col': default_col, 'pop_align': pop_align, 'query_mode': query_mode, 'page_context': page_context, 'pophelp_cols': pophelp_cols, 
                        'pophelp_source': pophelp_source, 'multi_opt': multi_opt, 'help_option': help_option, 'popup_xsl_name': popup_xsl_name, 'auto_fill_len': auto_fill_len,
                        'thumb_obj': thumb_obj, 'thumb_image_col': thumb_image_col, 'thumb_alt_col': thumb_alt_col, 'auto_min_length': auto_min_length,
                        'obj_name__ds': obj_name__ds, 'data_model_name': data_model_name, 'validate_data': validate_data, 'item_change': item_change, 'msg_no': msg_no, 
                        'filter_expr': filter_expr, 'layout': layout
                    }
                    logger.log(f"\n--- Class Pophelp ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"POPHELP table update query for Oracle database ::: {update_query}")
                    deployment_log(f"POPHELP table update query values for Oracle database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in POPHELP table for Oracle database.")
                else:
                    update_query = """
                        UPDATE pophelp SET
                            SQL_STR = %s, DW_OBJECT = %s, 
                            MSG_TITLE = %s, WIDTH = %s, HEIGHT = %s, 
                            CHG_DATE = TO_DATE(%s, 'DD-MM-YYYY'), CHG_USER = %s, 
                            CHG_TERM = %s, DIST_OPT = %s, FILTER_STRING = %s, 
                            SQL_INPUT = %s, DEFAULT_COL = %s, POP_ALIGN = %s, 
                            QUERY_MODE = %s, PAGE_CONTEXT = %s, 
                            POPHELP_COLS = %s, POPHELP_SOURCE = %s, 
                            MULTI_OPT = %s, HELP_OPTION = %s, 
                            POPUP_XSL_NAME = %s, AUTO_FILL_LEN = %s, 
                            THUMB_OBJ = %s, THUMB_IMAGE_COL = %s, 
                            THUMB_ALT_COL = %s, AUTO_MIN_LENGTH = %s, 
                            OBJ_NAME__DS = %s, DATA_MODEL_NAME = %s, 
                            VALIDATE_DATA = %s, ITEM_CHANGE = %s, 
                            MSG_NO = %s, FILTER_EXPR = %s, LAYOUT = %s
                        WHERE FIELD_NAME = %s AND MOD_NAME = %s
                    """
                    values = (
                        sql_str, dw_object, msg_title, width, height, 
                        chg_date, chg_user, chg_term, dist_opt, filter_string, sql_input, 
                        default_col, pop_align, query_mode, page_context, pophelp_cols, 
                        pophelp_source, multi_opt, help_option, popup_xsl_name, auto_fill_len, 
                        thumb_obj, thumb_image_col, thumb_alt_col, auto_min_length, 
                        obj_name__ds, data_model_name, validate_data, item_change, msg_no, 
                        filter_expr, layout, field_name, mod_name
                    )
                    logger.log(f"\n--- Class Pophelp ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"POPHELP table update query for Other database ::: {update_query}")
                    deployment_log(f"POPHELP table update query values for Other database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in POPHELP table for Other database.")
                cursor.close()
                logger.log(f"Updated: FIELD_NAME={field_name} and MOD_NAME={mod_name}")
            else:
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    insert_query = """
                        INSERT INTO pophelp (
                            FIELD_NAME, MOD_NAME, SQL_STR, DW_OBJECT, MSG_TITLE, WIDTH, HEIGHT, 
                            CHG_DATE, CHG_USER, CHG_TERM, DIST_OPT, FILTER_STRING, SQL_INPUT, 
                            DEFAULT_COL, POP_ALIGN, QUERY_MODE, PAGE_CONTEXT, POPHELP_COLS, 
                            POPHELP_SOURCE, MULTI_OPT, HELP_OPTION, POPUP_XSL_NAME, AUTO_FILL_LEN, 
                            THUMB_OBJ, THUMB_IMAGE_COL, THUMB_ALT_COL, AUTO_MIN_LENGTH, 
                            OBJ_NAME__DS, DATA_MODEL_NAME, VALIDATE_DATA, ITEM_CHANGE, MSG_NO, 
                            FILTER_EXPR, LAYOUT
                        ) 
                        VALUES (
                            :field_name, :mod_name, :sql_str, :dw_object, :msg_title, :width, :height, 
                            TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :dist_opt, :filter_string, :sql_input, 
                            :default_col, :pop_align, :query_mode, :page_context, :pophelp_cols, 
                            :pophelp_source, :multi_opt, :help_option, :popup_xsl_name, :auto_fill_len, 
                            :thumb_obj, :thumb_image_col, :thumb_alt_col, :auto_min_length, 
                            :obj_name__ds, :data_model_name, :validate_data, :item_change, :msg_no, 
                            :filter_expr, :layout
                        )
                    """
                    values = {
                        'field_name': field_name, 'mod_name': mod_name, 'sql_str': sql_str, 'dw_object': dw_object, 'msg_title': msg_title, 'width': width, 'height': height,
                        'chg_date': chg_date, 'chg_user': chg_user, 'chg_term': chg_term, 'dist_opt': dist_opt, 'filter_string': filter_string, 'sql_input': sql_input,
                        'default_col': default_col, 'pop_align': pop_align, 'query_mode': query_mode, 'page_context': page_context, 'pophelp_cols': pophelp_cols, 
                        'pophelp_source': pophelp_source, 'multi_opt': multi_opt, 'help_option': help_option, 'popup_xsl_name': popup_xsl_name, 'auto_fill_len': auto_fill_len,
                        'thumb_obj': thumb_obj, 'thumb_image_col': thumb_image_col, 'thumb_alt_col': thumb_alt_col, 'auto_min_length': auto_min_length,
                        'obj_name__ds': obj_name__ds, 'data_model_name': data_model_name, 'validate_data': validate_data, 'item_change': item_change, 'msg_no': msg_no, 
                        'filter_expr': filter_expr, 'layout': layout
                    }
                    logger.log(f"\n--- Class Pophelp ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"POPHELP table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"POPHELP table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in POPHELP table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO pophelp (
                            FIELD_NAME, MOD_NAME, SQL_STR, DW_OBJECT, MSG_TITLE, WIDTH, HEIGHT, 
                            CHG_DATE, CHG_USER, CHG_TERM, DIST_OPT, FILTER_STRING, SQL_INPUT, 
                            DEFAULT_COL, POP_ALIGN, QUERY_MODE, PAGE_CONTEXT, POPHELP_COLS, 
                            POPHELP_SOURCE, MULTI_OPT, HELP_OPTION, POPUP_XSL_NAME, AUTO_FILL_LEN, 
                            THUMB_OBJ, THUMB_IMAGE_COL, THUMB_ALT_COL, AUTO_MIN_LENGTH, 
                            OBJ_NAME__DS, DATA_MODEL_NAME, VALIDATE_DATA, ITEM_CHANGE, MSG_NO, 
                            FILTER_EXPR, LAYOUT
                        ) 
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, 
                            TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, 
                            %s, %s
                        )
                    """
                    values = (
                        field_name, mod_name, sql_str, dw_object, msg_title, width, height, 
                        chg_date, chg_user, chg_term, dist_opt, filter_string, sql_input, 
                        default_col, pop_align, query_mode, page_context, pophelp_cols, 
                        pophelp_source, multi_opt, help_option, popup_xsl_name, auto_fill_len, 
                        thumb_obj, thumb_image_col, thumb_alt_col, auto_min_length, 
                        obj_name__ds, data_model_name, validate_data, item_change, msg_no, 
                        filter_expr, layout
                    )
                    logger.log(f"\n--- Class Pophelp ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"POPHELP table insert query for Other database ::: {insert_query}")
                    deployment_log(f"POPHELP table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in POPHELP table for Other database.")
                cursor.close()
                logger.log(f"Inserted: FIELD_NAME={field_name} and MOD_NAME={mod_name}")

    def process_data(self, conn, sql_models_data, db_vendore):
        logger.log(f"Start of Pophelp Class")
        deployment_log(f"\n--------------------------------- Start of Pophelp Class -------------------------------------\n")
        self.sql_models = sql_models_data
        for sql_model in self.sql_models:
            if "sql_model" in sql_model and "columns" in sql_model['sql_model']:
                for column in sql_model['sql_model']['columns']:
                    lookup = column['column']['lookup']
                    if lookup:
                        self.check_or_update_pophelp(lookup, conn, db_vendore)
        logger.log(f"End of Pophelp Class")
        deployment_log(f"End of Pophelp Class")


