import cx_Oracle
from datetime import datetime
import loggerutility as logger
from loggerutility import deployment_log

class Sd_Trans_Design:
    
    sql_models = []

    def check_or_insert_sdTransDesign(self, sql_model, connection, con_type):

        missing_keys = [
            'schema_name'
        ]
        missing_keys = [key for key in missing_keys if key not in sql_model]

        if missing_keys:
            deployment_log(f"Missing required keys for SD_TRANS_DESIGN table: {', '.join(missing_keys)}")
            raise KeyError(f"Missing required keys for sd_trans_design table: {', '.join(missing_keys)}")
        else:
            schema_name = sql_model.get('schema_name', '') or None
            descr = sql_model.get('descr', '') or None
            data_src = sql_model.get('data_src', '').strip() or 'A'
            data_src_ref = sql_model.get('data_src_ref', '') or None
            data_src_driver = sql_model.get('data_src_driver', '') or None
            user_id_own = sql_model.get('user_id__own', '').strip() or ' '
            purpose = sql_model.get('purpose', '') or None
            def_security_opt = sql_model.get('def_security_opt', '') or None
            application = sql_model.get('application', '') or None
            obj_name = sql_model.get('obj_name', '') or None
            add_term = sql_model.get('add_term', '').strip() or ' '
            add_user = sql_model.get('add_user', '').strip() or ' '
            add_date = datetime.strptime(datetime.now().strftime('%Y-%b-%d'), '%Y-%b-%d')
            chg_date = datetime.strptime(datetime.now().strftime('%Y-%b-%d'), '%Y-%b-%d')
            chg_user = sql_model.get('chg_user', '').strip() or 'System'
            chg_term = sql_model.get('chg_term', '').strip() or 'System'
            schema_model = sql_model.get('schema_model', '') or None
            schema_table_list = sql_model.get('schema_table_list', '') or None
            visual_model = sql_model.get('visual_model', '') or None

            cursor = connection.cursor()
            count_query = f"""
                SELECT COUNT(*) 
                FROM sd_trans_design 
                WHERE SCHEMA_NAME = '{schema_name}'
            """
            logger.log(f"Class Sd_Trans_Design count_query::: {count_query}")
            deployment_log(f"SD_TRANS_DESIGN table select query ::: {count_query}")
            cursor.execute(count_query)
            count = cursor.fetchone()[0]
            deployment_log(f"SD_TRANS_DESIGN table select query result ::: {count}")
            cursor.close()
            if count > 0:
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    update_query = """
                        UPDATE sd_trans_design 
                        SET 
                            DESCR = :descr,
                            DATA_SRC = :data_src,
                            DATA_SRC_REF = :data_src_ref,
                            DATA_SRC_DRIVER = :data_src_driver,
                            USER_ID__OWN = :user_id__own,
                            PURPOSE = :purpose,
                            DEF_SECURITY_OPT = :def_security_opt,
                            APPLICATION = :application,
                            OBJ_NAME = :obj_name,
                            CHG_TERM = :chg_term,
                            CHG_USER = :chg_user,
                            CHG_DATE = :chg_date,
                            SCHEMA_MODEL = :schema_model,
                            SCHEMA_TABLE_LIST = :schema_table_list,
                            VISUAL_MODEL = :visual_model
                        WHERE SCHEMA_NAME = :schema_name
                    """
                    values = {
                        "descr": descr,
                        "data_src": data_src,
                        "data_src_ref": data_src_ref,
                        "data_src_driver": data_src_driver,
                        "user_id__own": user_id_own,
                        "purpose": purpose,
                        "def_security_opt": def_security_opt,
                        "application": application,
                        "obj_name": obj_name,
                        "chg_term": chg_term,
                        "chg_user": chg_user,
                        "chg_date": chg_date,
                        "schema_model": schema_model,
                        "schema_table_list": schema_table_list,
                        "visual_model": visual_model,
                        "schema_name": schema_name
                    }
                    logger.log(f"\n--- Class Sd_Trans_Design ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"SD_TRANS_DESIGN table update query for Oracle database ::: {update_query}")
                    deployment_log(f"SD_TRANS_DESIGN table update query values for Oracle database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in SD_TRANS_DESIGN table for Oracle database.")
                else:
                    update_query = """
                        UPDATE sd_trans_design 
                        SET 
                            DESCR = %s,
                            DATA_SRC = %s,
                            DATA_SRC_REF = %s,
                            DATA_SRC_DRIVER = %s,
                            USER_ID__OWN = %s,
                            PURPOSE = %s,
                            DEF_SECURITY_OPT = %s,
                            APPLICATION = %s,
                            OBJ_NAME = %s,
                            CHG_TERM = %s,
                            CHG_USER = %s,
                            CHG_DATE = %s,
                            SCHEMA_MODEL = %s,
                            SCHEMA_TABLE_LIST = %s,
                            VISUAL_MODEL = %s
                        WHERE SCHEMA_NAME = %s
                    """
                    values = (
                        descr, data_src, data_src_ref, data_src_driver, user_id_own, 
                        purpose, def_security_opt, application, obj_name, chg_term, 
                        chg_user, chg_date, schema_model, schema_table_list, 
                        visual_model, schema_name
                    )
                    logger.log(f"\n--- Class Sd_Trans_Design ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"SD_TRANS_DESIGN table update query for Other database ::: {update_query}")
                    deployment_log(f"SD_TRANS_DESIGN table update query values for Other database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in SD_TRANS_DESIGN table for Other database.")
                cursor.close()
                logger.log(f"Updated: SCHEMA_NAME {schema_name}")
            else:
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    insert_query = """
                        INSERT INTO sd_trans_design (
                        SCHEMA_NAME, DESCR, DATA_SRC, DATA_SRC_REF, DATA_SRC_DRIVER,
                        USER_ID__OWN, PURPOSE, DEF_SECURITY_OPT, APPLICATION, OBJ_NAME, 
                        ADD_TERM, ADD_USER, ADD_DATE, CHG_TERM, CHG_USER, CHG_DATE, 
                        SCHEMA_MODEL, SCHEMA_TABLE_LIST, VISUAL_MODEL
                        ) VALUES (
                        :schema_name, :descr, :data_src, :data_src_ref, :data_src_driver,
                        :user_id__own, :purpose, :def_security_opt, :application, :obj_name, 
                        :add_term, :add_user, :add_date, :chg_term, :chg_user, :chg_date, 
                        :schema_model, :schema_table_list, :visual_model
                        )
                    """
                    values = {
                        "schema_name": schema_name,
                        "descr": descr,
                        "data_src": data_src,
                        "data_src_ref": data_src_ref,
                        "data_src_driver": data_src_driver,
                        "user_id__own": user_id_own,
                        "purpose": purpose,
                        "def_security_opt": def_security_opt,
                        "application": application,
                        "obj_name": obj_name,
                        "add_term": add_term,
                        "add_user": add_user,
                        "add_date": add_date,
                        "chg_term": chg_term,
                        "chg_user": chg_user,
                        "chg_date": chg_date,
                        "schema_model": schema_model,
                        "schema_table_list": schema_table_list,
                        "visual_model": visual_model
                    }
                    logger.log(f"\n--- Class Sd_Trans_Design ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SD_TRANS_DESIGN table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"SD_TRANS_DESIGN table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SD_TRANS_DESIGN table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO sd_trans_design (
                            SCHEMA_NAME, DESCR, DATA_SRC, DATA_SRC_REF, DATA_SRC_DRIVER,
                            USER_ID__OWN, PURPOSE, DEF_SECURITY_OPT, APPLICATION, OBJ_NAME, 
                            ADD_TERM, ADD_USER, ADD_DATE, CHG_TERM, CHG_USER, CHG_DATE, 
                            SCHEMA_MODEL, SCHEMA_TABLE_LIST, VISUAL_MODEL
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s
                        )
                    """
                    values = (
                        schema_name, descr, data_src, data_src_ref, data_src_driver, 
                        user_id_own, purpose, def_security_opt, application, obj_name, 
                        add_term, add_user, add_date, chg_term, chg_user, chg_date, 
                        schema_model, schema_table_list, visual_model
                    )
                    logger.log(f"\n--- Class Sd_Trans_Design ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"SD_TRANS_DESIGN table insert query for Other database ::: {insert_query}")
                    deployment_log(f"SD_TRANS_DESIGN table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in SD_TRANS_DESIGN table for Other database.")
                logger.log(f"Inserted: SCHEMA_NAME {schema_name}")
                cursor.close()

    def process_data(self, conn, user_info, sql_models_data, db_vendore):
        logger.log(f"Start of Sd_Trans_Design Class")
        deployment_log(f"\n--------------------------------- Start of Sd_Trans_Design Class -------------------------------------\n")
        self.sql_models = sql_models_data
        self.check_or_insert_sdTransDesign(self.sql_models, conn, db_vendore)
        logger.log(f"End of Sd_Trans_Design Class")
        deployment_log(f"End of Sd_Trans_Design Class")
