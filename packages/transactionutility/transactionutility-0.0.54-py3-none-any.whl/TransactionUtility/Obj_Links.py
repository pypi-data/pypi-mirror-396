import cx_Oracle
import loggerutility as logger
from loggerutility import deployment_log

class Obj_Links:
    
    sql_models = []

    def check_or_update_obj_links(self, links, connection, con_type):
        
        required_keys = [
            'obj_name', 'form_no', 'field_name', 'link_form_name', 'link_arg', 'rights_char',
            'line_no'
        ]
        missing_keys = [key for key in required_keys if key not in links]

        if missing_keys:
            deployment_log(f"Missing required keys for OBJ_LINKS table: {', '.join(missing_keys)}")
            raise KeyError(f"Missing required keys for obj_links table: {', '.join(missing_keys)}")
        else:
            obj_name = links.get('obj_name', '') or None
            form_no = links.get('form_no', '') or None
            field_name = links.get('field_name', '') or None
            target_obj_name = links.get('target_object', '') or None
            link_form_name = links.get('link_form_name', '') or None
            link_title = links.get('link_title', '') or None
            link_uri = links.get('link_uri', '') or None
            link_type = links.get('link_type', '') or None
            link_arg = links.get('link_arg', '') or None
            update_flag = links.get('update_flag', '') or None
            link_name = links.get('link_name', '') or None
            rights_char = links.get('rights_char', '') or None
            image = links.get('image', '') or None
            show_in_panel = links.get('show_in_panel', '') or None
            shortcut_char = links.get('shortcut_char', '') or None
            auto_invoke = links.get('auto_invoke', '') or None
            swipe_position = links.get('swipe_position', '') or None
            title = links.get('title', '') or None
            descr = links.get('descr', '') or None
            show_confirm = links.get('show_confirm', '') or None
            display_mode = links.get('display_mode', '') or None
            line_no = links.get('line_no', '') or None
            link_id = links.get('link_id', '') or None
            rec_specific = links.get('record_specific', '') or None

            cursor = connection.cursor()
            deployment_log(f"OBJ_LINKS table select query ::: SELECT COUNT(*) FROM obj_links WHERE OBJ_NAME = '{obj_name}' AND FORM_NO = {form_no} AND FIELD_NAME = '{field_name}' AND LINE_NO = {line_no}")
            cursor.execute(f"""
                SELECT COUNT(*) FROM obj_links 
                WHERE OBJ_NAME = '{obj_name}' 
                AND FORM_NO = {form_no} 
                AND FIELD_NAME = '{field_name}' 
                AND LINE_NO = {line_no}
            """)
            count = cursor.fetchone()[0]
            deployment_log(f"OBJ_LINKS table select query result :::  {count}")
            cursor.close()

            if count > 0:                
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    update_query = """
                        UPDATE obj_links SET
                        TARGET_OBJ_NAME = :target_obj_name, LINK_FORM_NAME = :link_form_name,
                        LINK_TITLE = :link_title, LINK_URI = :link_uri, LINK_TYPE = :link_type,
                        LINK_ARG = :link_arg, UPDATE_FLAG = :update_flag, LINK_NAME = :link_name,
                        RIGHTS_CHAR = :rights_char, IMAGE = :image, SHOW_IN_PANEL = :show_in_panel,
                        SHORTCUT_CHAR = :shortcut_char, AUTO_INVOKE = :auto_invoke,
                        SWIPE_POSITION = :swipe_position, TITLE = :title, DESCR = :descr,
                        SHOW_CONFIRM = :show_confirm, DISPLAY_MODE = :display_mode,
                        LINK_ID = :link_id, REC_SPECIFIC = :rec_specific
                        WHERE OBJ_NAME = :obj_name 
                        AND FORM_NO = :form_no 
                        AND FIELD_NAME = :field_name 
                        AND LINE_NO = :line_no
                    """
                    values = {
                        'obj_name': obj_name,
                        'form_no': form_no,
                        'field_name': field_name,
                        'target_obj_name': target_obj_name,
                        'link_form_name': link_form_name,
                        'link_title': link_title,
                        'link_uri': link_uri,
                        'link_type': link_type,
                        'link_arg': link_arg,
                        'update_flag': update_flag,
                        'link_name': link_name,
                        'rights_char': rights_char,
                        'image': image,
                        'show_in_panel': show_in_panel,
                        'shortcut_char': shortcut_char,
                        'auto_invoke': auto_invoke,
                        'swipe_position': swipe_position,
                        'title': title,
                        'descr': descr,
                        'show_confirm': show_confirm,
                        'display_mode': display_mode,
                        'line_no': line_no,
                        'link_id': link_id,
                        'rec_specific': rec_specific
                    }
                    logger.log(f"\n--- Class Obj_Links ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"OBJ_LINKS table update query for Oracle database ::: {update_query}")
                    deployment_log(f"OBJ_LINKS table update query values for Oracle database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in OBJ_LINKS table for Oracle database.")
                else:
                    update_query = """
                        UPDATE obj_links SET
                            TARGET_OBJ_NAME = %s, LINK_FORM_NAME = %s,
                            LINK_TITLE = %s, LINK_URI = %s, LINK_TYPE = %s,
                            LINK_ARG = %s, UPDATE_FLAG = %s, LINK_NAME = %s,
                            RIGHTS_CHAR = %s, IMAGE = %s, SHOW_IN_PANEL = %s,
                            SHORTCUT_CHAR = %s, AUTO_INVOKE = %s,
                            SWIPE_POSITION = %s, TITLE = %s, DESCR = %s,
                            SHOW_CONFIRM = %s, DISPLAY_MODE = %s,
                            LINK_ID = %s, REC_SPECIFIC = %s
                        WHERE OBJ_NAME = %s 
                        AND FORM_NO = %s 
                        AND FIELD_NAME = %s 
                        AND LINE_NO = %s
                    """
                    values = (
                        target_obj_name, link_form_name, link_title, link_uri, link_type,
                        link_arg, update_flag, link_name, rights_char, image, show_in_panel,
                        shortcut_char, auto_invoke, swipe_position, title, descr,
                        show_confirm, display_mode, link_id, rec_specific,
                        obj_name, form_no, field_name, line_no
                    )
                    logger.log(f"\n--- Class Obj_Links ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"OBJ_LINKS table update query for Other database ::: {update_query}")
                    deployment_log(f"OBJ_LINKS table update query values for Other database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in OBJ_LINKS table for Other database.")
                cursor.close()
            else:
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    insert_query = """
                        INSERT INTO obj_links (
                        OBJ_NAME, FORM_NO, FIELD_NAME, TARGET_OBJ_NAME, LINK_FORM_NAME,
                        LINK_TITLE, LINK_URI, LINK_TYPE, LINK_ARG, UPDATE_FLAG, LINK_NAME,
                        RIGHTS_CHAR, IMAGE, SHOW_IN_PANEL, SHORTCUT_CHAR, AUTO_INVOKE,
                        SWIPE_POSITION, TITLE, DESCR, SHOW_CONFIRM, DISPLAY_MODE, LINE_NO,
                        LINK_ID, REC_SPECIFIC
                        ) VALUES (
                        :obj_name, :form_no, :field_name, :target_obj_name, :link_form_name,
                        :link_title, :link_uri, :link_type, :link_arg, :update_flag, :link_name,
                        :rights_char, :image, :show_in_panel, :shortcut_char, :auto_invoke,
                        :swipe_position, :title, :descr, :show_confirm, :display_mode, :line_no,
                        :link_id, :rec_specific
                    )
                    """
                    values = {
                        'obj_name': obj_name,
                        'form_no': form_no,
                        'field_name': field_name,
                        'target_obj_name': target_obj_name,
                        'link_form_name': link_form_name,
                        'link_title': link_title,
                        'link_uri': link_uri,
                        'link_type': link_type,
                        'link_arg': link_arg,
                        'update_flag': update_flag,
                        'link_name': link_name,
                        'rights_char': rights_char,
                        'image': image,
                        'show_in_panel': show_in_panel,
                        'shortcut_char': shortcut_char,
                        'auto_invoke': auto_invoke,
                        'swipe_position': swipe_position,
                        'title': title,
                        'descr': descr,
                        'show_confirm': show_confirm,
                        'display_mode': display_mode,
                        'line_no': line_no,
                        'link_id': link_id,
                        'rec_specific': rec_specific
                    }
                    logger.log(f"\n--- Class Obj_Links ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"OBJ_LINKS table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"OBJ_LINKS table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in OBJ_LINKS table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO obj_links (
                            OBJ_NAME, FORM_NO, FIELD_NAME, TARGET_OBJ_NAME, LINK_FORM_NAME,
                            LINK_TITLE, LINK_URI, LINK_TYPE, LINK_ARG, UPDATE_FLAG, LINK_NAME,
                            RIGHTS_CHAR, IMAGE, SHOW_IN_PANEL, SHORTCUT_CHAR, AUTO_INVOKE,
                            SWIPE_POSITION, TITLE, DESCR, SHOW_CONFIRM, DISPLAY_MODE, LINE_NO,
                            LINK_ID, REC_SPECIFIC
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s
                        )
                    """
                    values = (
                        obj_name, form_no, field_name, target_obj_name, link_form_name,
                        link_title, link_uri, link_type, link_arg, update_flag, link_name,
                        rights_char, image, show_in_panel, shortcut_char, auto_invoke,
                        swipe_position, title, descr, show_confirm, display_mode, line_no,
                        link_id, rec_specific
                    )
                    logger.log(f"\n--- Class Obj_Links ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"OBJ_LINKS table insert query for Other database ::: {insert_query}")
                    deployment_log(f"OBJ_LINKS table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in OBJ_LINKS table for Other database.")
                cursor.close()

    def process_data(self, conn, sql_models_data, db_vendore):
        logger.log(f"Start of Obj_Links Class")
        deployment_log(f"\n--------------------------------- Start of Genmst Class -------------------------------------\n")
        self.sql_models = sql_models_data
        for sql_model in self.sql_models:
            if "sql_model" in sql_model and "links" in sql_model['sql_model']:
                for links in sql_model['sql_model']['links']:
                    self.check_or_update_obj_links(links, conn, db_vendore)
        logger.log(f"End of Obj_Links Class")
        deployment_log(f"End of Genmst Class")

