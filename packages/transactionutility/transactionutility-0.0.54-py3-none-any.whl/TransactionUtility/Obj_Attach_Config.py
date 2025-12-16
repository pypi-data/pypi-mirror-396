import cx_Oracle
import loggerutility as logger
from datetime import datetime
from loggerutility import deployment_log

class Obj_Attach_Config:
    
    attach_docs = []

    def check_or_update_obj_attach_config(self, attach_doc, connection, con_type):
        required_keys = ['obj_name', 'doc_type']
        missing_keys = [key for key in required_keys if key not in attach_doc]
        
        if missing_keys:
            deployment_log(f"Missing required keys for OBJ_ATTACH_CONFIG table: {', '.join(missing_keys)}")
            raise KeyError(f"Missing required keys for obj_attach_config table: {', '.join(missing_keys)}")
        
        obj_name = attach_doc.get('obj_name', '') or None
        doc_type = attach_doc.get('doc_type', '') or None
        file_type = attach_doc.get('file_type', '') or None
        min_attach_req = attach_doc.get('min_attach_req', '') or None
        max_attach_allow = attach_doc.get('max_attach_allow', '') or None
        attach_mode = attach_doc.get('attach_mode', '') or None
        remarks = attach_doc.get('remarks', '') or None
        chg_date = datetime.now().strftime('%d-%m-%y')
        chg_term = attach_doc.get('chg_term', '').strip() or 'System'
        chg_user = attach_doc.get('chg_user', '').strip() or 'System'
        no_attachments = attach_doc.get('no_attachments', '') or None
        no_comments = attach_doc.get('no_comments', '') or None
        descr_req = attach_doc.get('descr_req', '') or None
        doc_purpose = attach_doc.get('doc_purpose', '') or None
        max_size_mb = attach_doc.get('max_size_mb', '') or None
        max_file_size = attach_doc.get('max_file_size', '') or None
        track_validity = attach_doc.get('track_validity', '') or None
        allow_download = attach_doc.get('allow_download', '') or None
        extract_prc = attach_doc.get('extract_prc', '') or None
        show_del_attach = attach_doc.get('show_del_attach', '') or None
        extract_templ = attach_doc.get('extract_templ', '') or None
        disply_order = attach_doc.get('disply_order', '') or None
        meta_data_def = attach_doc.get('meta_data_def', '') or None

        cursor = connection.cursor()
        deployment_log(f"OBJ_ATTACH_CONFIG table select query ::: SELECT COUNT(*) FROM obj_attach_config WHERE OBJ_NAME = '{obj_name}' AND DOC_TYPE = '{doc_type}'")
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM obj_attach_config
            WHERE OBJ_NAME = '{obj_name}' 
            AND DOC_TYPE = '{doc_type}'
        """)        
        count = cursor.fetchone()[0]
        deployment_log(f"OBJ_ATTACH_CONFIG table select query result :::  {count}")
        cursor.close()
        if count > 0:
            cursor = connection.cursor()
            if con_type == 'Oracle':
                update_query = """
                    UPDATE obj_attach_config SET
                    FILE_TYPE = :file_type, MIN_ATTACH_REQ = :min_attach_req,
                    MAX_ATTACH_ALLOW = :max_attach_allow, ATTACH_MODE = :attach_mode,
                    REMARKS = :remarks, CHG_DATE = TO_DATE(:chg_date, 'DD-MM-YYYY'), CHG_USER = :chg_user,
                    CHG_TERM = :chg_term, NO_ATTACHMENTS = :no_attachments,
                    NO_COMMENTS = :no_comments, DESCR_REQ = :descr_req, DOC_PURPOSE = :doc_purpose,
                    MAX_SIZE_MB = :max_size_mb, MAX_FILE_SIZE = :max_file_size,
                    TRACK_VALIDITY = :track_validity, ALLOW_DOWNLOAD = :allow_download,
                    EXTRACT_PRC = :extract_prc, SHOW_DEL_ATTACH = :show_del_attach,
                    EXTRACT_TEMPL = :extract_templ, DISPLY_ORDER = :disply_order,
                    META_DATA_DEF = :meta_data_def
                    WHERE OBJ_NAME = :obj_name AND DOC_TYPE = :doc_type
                """
                values = {
                    'file_type': file_type, 'min_attach_req': min_attach_req,
                    'max_attach_allow': max_attach_allow, 'attach_mode': attach_mode,
                    'remarks': remarks, 'chg_date': chg_date, 'chg_user': chg_user,
                    'chg_term': chg_term, 'no_attachments': no_attachments,
                    'no_comments': no_comments, 'descr_req': descr_req, 'doc_purpose': doc_purpose,
                    'max_size_mb': max_size_mb, 'max_file_size': max_file_size,
                    'track_validity': track_validity, 'allow_download': allow_download,
                    'extract_prc': extract_prc, 'show_del_attach': show_del_attach,
                    'extract_templ': extract_templ, 'disply_order': disply_order,
                    'meta_data_def': meta_data_def, 'obj_name': obj_name, 'doc_type': doc_type
                }
                logger.log(f"\n--- Class Obj_Attach_Config ---\n")
                logger.log(f"update_query values :: {values}")
                deployment_log(f"OBJ_ATTACH_CONFIG table update query for Oracle database ::: {update_query}")
                deployment_log(f"OBJ_ATTACH_CONFIG table update query values for Oracle database ::: {values}")
                cursor.execute(update_query, values)
                logger.log(f"Successfully updated row.")
                deployment_log(f"Data updated successfully in OBJ_ATTACH_CONFIG table for Oracle database.")
            else:
                update_query = """
                    UPDATE obj_attach_config SET
                        FILE_TYPE = %s, MIN_ATTACH_REQ = %s,
                        MAX_ATTACH_ALLOW = %s, ATTACH_MODE = %s,
                        REMARKS = %s, CHG_DATE = TO_DATE(%s, 'DD-MM-YYYY'), CHG_USER = %s,
                        CHG_TERM = %s, NO_ATTACHMENTS = %s,
                        NO_COMMENTS = %s, DESCR_REQ = %s, DOC_PURPOSE = %s,
                        MAX_SIZE_MB = %s, MAX_FILE_SIZE = %s,
                        TRACK_VALIDITY = %s, ALLOW_DOWNLOAD = %s,
                        EXTRACT_PRC = %s, SHOW_DEL_ATTACH = %s,
                        EXTRACT_TEMPL = %s, DISPLY_ORDER = %s,
                        META_DATA_DEF = %s
                    WHERE OBJ_NAME = %s AND DOC_TYPE = %s
                """
                values = (
                    file_type, min_attach_req, max_attach_allow, attach_mode,
                    remarks, chg_date, chg_user, chg_term, no_attachments,
                    no_comments, descr_req, doc_purpose, max_size_mb, max_file_size,
                    track_validity, allow_download, extract_prc, show_del_attach,
                    extract_templ, disply_order, meta_data_def, obj_name, doc_type
                )
                logger.log(f"\n--- Class Obj_Attach_Config ---\n")
                logger.log(f"update_query values :: {values}")
                deployment_log(f"OBJ_ATTACH_CONFIG table update query for Other database ::: {update_query}")
                deployment_log(f"OBJ_ATTACH_CONFIG table update query values for Other database ::: {values}")
                cursor.execute(update_query, values)
                logger.log(f"Successfully updated row.")
                deployment_log(f"Data updated successfully in OBJ_ATTACH_CONFIG table for Other database.")
            cursor.close()
        else:
            cursor = connection.cursor()
            if con_type == 'Oracle':
                insert_query = """
                    INSERT INTO obj_attach_config (
                        OBJ_NAME, DOC_TYPE, FILE_TYPE, MIN_ATTACH_REQ, MAX_ATTACH_ALLOW,
                        ATTACH_MODE, REMARKS, CHG_DATE, CHG_USER, CHG_TERM, NO_ATTACHMENTS,
                        NO_COMMENTS, DESCR_REQ, DOC_PURPOSE, MAX_SIZE_MB, MAX_FILE_SIZE,
                        TRACK_VALIDITY, ALLOW_DOWNLOAD, EXTRACT_PRC, SHOW_DEL_ATTACH,
                        EXTRACT_TEMPL, DISPLY_ORDER, META_DATA_DEF
                    ) VALUES (
                        :obj_name, :doc_type, :file_type, :min_attach_req, :max_attach_allow,
                        :attach_mode, :remarks, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :no_attachments,
                        :no_comments, :descr_req, :doc_purpose, :max_size_mb, :max_file_size,
                        :track_validity, :allow_download, :extract_prc, :show_del_attach,
                        :extract_templ, :disply_order, :meta_data_def
                    )
                """
                values = {
                    'obj_name': obj_name, 'doc_type': doc_type, 'file_type': file_type,
                    'min_attach_req': min_attach_req, 'max_attach_allow': max_attach_allow,
                    'attach_mode': attach_mode, 'remarks': remarks, 'chg_date': chg_date,
                    'chg_user': chg_user, 'chg_term': chg_term, 'no_attachments': no_attachments,
                    'no_comments': no_comments, 'descr_req': descr_req, 'doc_purpose': doc_purpose,
                    'max_size_mb': max_size_mb, 'max_file_size': max_file_size,
                    'track_validity': track_validity, 'allow_download': allow_download,
                    'extract_prc': extract_prc, 'show_del_attach': show_del_attach,
                    'extract_templ': extract_templ, 'disply_order': disply_order,
                    'meta_data_def': meta_data_def
                }
                logger.log(f"\n--- Class Obj_Attach_Config ---\n")
                logger.log(f"insert_query values :: {values}")
                deployment_log(f"OBJ_ATTACH_CONFIG table insert query for Oracle database ::: {insert_query}")
                deployment_log(f"OBJ_ATTACH_CONFIG table insert query values for Oracle database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in OBJ_ATTACH_CONFIG table for Oracle database.")
            else:
                insert_query = """
                    INSERT INTO obj_attach_config (
                        OBJ_NAME, DOC_TYPE, FILE_TYPE, MIN_ATTACH_REQ, MAX_ATTACH_ALLOW,
                        ATTACH_MODE, REMARKS, CHG_DATE, CHG_USER, CHG_TERM, NO_ATTACHMENTS,
                        NO_COMMENTS, DESCR_REQ, DOC_PURPOSE, MAX_SIZE_MB, MAX_FILE_SIZE,
                        TRACK_VALIDITY, ALLOW_DOWNLOAD, EXTRACT_PRC, SHOW_DEL_ATTACH,
                        EXTRACT_TEMPL, DISPLY_ORDER, META_DATA_DEF
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                """
                values = (
                    obj_name, doc_type, file_type, min_attach_req, max_attach_allow,
                    attach_mode, remarks, chg_date, chg_user, chg_term, no_attachments,
                    no_comments, descr_req, doc_purpose, max_size_mb, max_file_size,
                    track_validity, allow_download, extract_prc, show_del_attach,
                    extract_templ, disply_order, meta_data_def
                )
                logger.log(f"\n--- Class Obj_Attach_Config ---\n")
                logger.log(f"insert_query values :: {values}")
                deployment_log(f"OBJ_ATTACH_CONFIG table insert query for Other database ::: {insert_query}")
                deployment_log(f"OBJ_ATTACH_CONFIG table insert query values for Other database ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Successfully inserted row.")
                deployment_log(f"Data inserted successfully in OBJ_ATTACH_CONFIG table for Other database.")
            cursor.close()

    def process_data(self, conn, attach_docs_data, db_vendore):
        logger.log("Start of Obj_Attach_Config Class")
        deployment_log(f"\n--------------------------------- Start of Obj_Attach_Config Class -------------------------------------\n")
        self.attach_docs = attach_docs_data
        for attach_doc in self.attach_docs:
            self.check_or_update_obj_attach_config(attach_doc, conn, db_vendore)
        logger.log("End of Obj_Attach_Config Class")
        deployment_log(f"End of Obj_Attach_Config Class")
