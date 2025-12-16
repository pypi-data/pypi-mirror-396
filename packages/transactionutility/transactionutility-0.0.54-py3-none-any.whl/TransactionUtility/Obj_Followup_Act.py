import cx_Oracle
import loggerutility as logger
from datetime import datetime
import re
from loggerutility import deployment_log

class Obj_Followup_Act:

    def check_or_update_followup_act(self, followup_act, connection, con_type):

        required_keys = [
            'obj_name', 'line_no', 'action_id'
        ]
        missing_keys = [key for key in required_keys if key not in followup_act]

        if missing_keys:
            deployment_log(f"Missing required keys for OBJ_FOLLOWUP_ACT table: {', '.join(missing_keys)}")
            raise KeyError(f"Missing required keys for obj_followup_act table: {', '.join(missing_keys)}")
        else:
            obj_name = followup_act.get('obj_name', '') or None
            line_no = followup_act.get('line_no', '') or None
            action_id = followup_act.get('action_id', '') or None
            action_type = followup_act.get('action_type', '') or None
            action_info = followup_act.get('action_info', '') or None
            conditional_expression = followup_act.get('conditional_expression', '') or None
            conditional_input = followup_act.get('conditional_input', '') or None
            chg_date = datetime.now().strftime('%d-%m-%y')
            chg_user = followup_act.get('chg_user', '').strip() or 'System'
            chg_term = followup_act.get('chg_term', '').strip() or 'System'
            max_retry_count = followup_act.get('max_retry_count', '') or None

            cursor = connection.cursor()
            deployment_log(f"OBJ_FOLLOWUP_ACT table select query ::: SELECT COUNT(*) FROM obj_followup_act WHERE OBJ_NAME = '{obj_name}' AND LINE_NO = '{line_no}' AND ACTION_ID = '{action_id}'")
            cursor.execute(f"""
                SELECT COUNT(*) FROM obj_followup_act 
                WHERE OBJ_NAME = '{obj_name}' 
                AND LINE_NO = '{line_no}'
                AND ACTION_ID = '{action_id}'
            """)
            count = cursor.fetchone()[0]
            logger.log(f"Count ::: {count}")
            deployment_log(f"OBJ_FOLLOWUP_ACT table select query result :::  {count}")
            cursor.close()
            if count > 0:
                logger.log(f"Inside update")
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    update_query = """
                        UPDATE obj_followup_act SET
                        ACTION_TYPE = :action_type, ACTION_INFO = :action_info,
                        CONDITIONAL_EXPRESSION = :conditional_expression, CONDITIONAL_INPUT = :conditional_input,
                        CHG_DATE = TO_DATE(:chg_date, 'DD-MM-YY'), CHG_USER = :chg_user, CHG_TERM = :chg_term,
                        MAX_RETRY_COUNT = :max_retry_count
                        WHERE OBJ_NAME = :obj_name 
                        AND LINE_NO = :line_no 
                        AND ACTION_ID = :action_id
                    """
                    values = {
                        'obj_name': obj_name,
                        'line_no': line_no,
                        'action_id': action_id,
                        'action_type': action_type,
                        'action_info': action_info,
                        'conditional_expression': conditional_expression,
                        'conditional_input': conditional_input,
                        'chg_date': chg_date,
                        'chg_user': chg_user,
                        'chg_term': chg_term,
                        'max_retry_count': max_retry_count
                    }
                    logger.log(f"\n--- Class Obj_Followup_Act ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"OBJ_FOLLOWUP_ACT table update query for Oracle database ::: {update_query}")
                    deployment_log(f"OBJ_FOLLOWUP_ACT table update query values for Oracle database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in OBJ_FOLLOWUP_ACT table for Oracle database.")
                else:
                    update_query = """
                        UPDATE obj_followup_act
                        SET 
                            ACTION_TYPE = %s,
                            ACTION_INFO = %s,
                            CONDITIONAL_EXPRESSION = %s,
                            CONDITIONAL_INPUT = %s,
                            CHG_DATE = TO_DATE(%s, 'DD-MM-YY'),
                            CHG_USER = %s,
                            CHG_TERM = %s,
                            MAX_RETRY_COUNT = %s
                        WHERE 
                            OBJ_NAME = %s 
                            AND LINE_NO = %s 
                            AND ACTION_ID = %s
                    """
                    values = (
                        action_type, action_info, conditional_expression, conditional_input,
                        chg_date, chg_user, chg_term, max_retry_count,
                        obj_name, line_no, action_id
                    )
                    logger.log(f"\n--- Class Obj_Followup_Act ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"OBJ_FOLLOWUP_ACT table update query for Other database ::: {update_query}")
                    deployment_log(f"OBJ_FOLLOWUP_ACT table update query values for Other database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in OBJ_FOLLOWUP_ACT table for Other database.")
                cursor.close()
            else:
                logger.log(f"Inside Insert")
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    insert_query = """
                        INSERT INTO obj_followup_act (
                        OBJ_NAME, LINE_NO, ACTION_ID, ACTION_TYPE, ACTION_INFO,
                        CONDITIONAL_EXPRESSION, CONDITIONAL_INPUT, CHG_DATE, CHG_USER,
                        CHG_TERM, MAX_RETRY_COUNT
                        ) VALUES (
                        :obj_name, :line_no, :action_id, :action_type, :action_info,
                        :conditional_expression, :conditional_input, TO_DATE(:chg_date, 'DD-MM-YY'), :chg_user,
                        :chg_term, :max_retry_count
                    )
                    """
                    values = {
                        'obj_name': obj_name,
                        'line_no': line_no,
                        'action_id': action_id,
                        'action_type': action_type,
                        'action_info': action_info,
                        'conditional_expression': conditional_expression,
                        'conditional_input': conditional_input,
                        'chg_date': chg_date,
                        'chg_user': chg_user,
                        'chg_term': chg_term,
                        'max_retry_count': max_retry_count
                    }
                    logger.log(f"\n--- Class Obj_Followup_Act ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"OBJ_FOLLOWUP_ACT table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"OBJ_FOLLOWUP_ACT table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in OBJ_FOLLOWUP_ACT table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO obj_followup_act (
                            OBJ_NAME, LINE_NO, ACTION_ID, ACTION_TYPE, ACTION_INFO,
                            CONDITIONAL_EXPRESSION, CONDITIONAL_INPUT, CHG_DATE, CHG_USER,
                            CHG_TERM, MAX_RETRY_COUNT
                        ) VALUES (
                            %s, %s, %s, %s, %s, 
                            %s, %s, TO_DATE(%s, 'DD-MM-YY'), %s, 
                            %s, %s
                        )
                    """
                    values = (
                        obj_name, line_no, action_id, action_type, action_info,
                        conditional_expression, conditional_input, chg_date, chg_user,
                        chg_term, max_retry_count
                    )
                    logger.log(f"\n--- Class Obj_Followup_Act ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"OBJ_FOLLOWUP_ACT table insert query for Other database ::: {insert_query}")
                    deployment_log(f"OBJ_FOLLOWUP_ACT table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in OBJ_FOLLOWUP_ACT table for Other database.")
                cursor.close()


    def process_data(self, conn, follow_up_actions, obj_name, db_vendore):
        logger.log(f"Start of Obj_Followup_Act Class")
        deployment_log(f"\n--------------------------------- Start of Obj_Followup_Act Class -------------------------------------\n")
        for index, action in enumerate(follow_up_actions):
            parts = action.split(',', 1)

            if ':' in parts[1]:
                new_parts = parts[1].split(':')
                main_text = new_parts[1]
            else:
                main_text = parts[1]

            logger.log(f"Inside follow_up_actions ::: {parts[0]}")
            logger.log(f"Inside follow_up_actions ::: {main_text}")
            deployment_log(f"OBJ_FOLLOWUP_ACT main_text ::: {main_text}")

            action_id = ''
            action_info = ''
            if str(main_text).startswith("business_logic"):
                action_word = parts[0][3:]
                if 'add' == action_word.lower() or 'edit' == action_word.lower():
                    action_id = "save"
                else:
                    action_id = action_word

                pattern = r"business_logic\((.*)\)"
                match = re.search(pattern, main_text)

                if match:
                    logger.log(f'business_logic match for followup_act ::: {match}')
                    inside_parentheses = match.group(1)
                    logger.log(f'business_logic inside_parentheses for followup_act ::: {inside_parentheses}')
                    action_info = inside_parentheses.split(",")[-2].replace("'","")
                logger.log(f"business_logic action_id: {action_id}")
                logger.log(f"business_logic action_info: {action_info}")
                deployment_log(f"OBJ_FOLLOWUP_ACT business_logic action_id: {action_id}")
                deployment_log(f"OBJ_FOLLOWUP_ACT business_logic action_info: {action_info}")

                followup_act = {
                    'obj_name': obj_name,
                    'line_no': str(index+1),
                    'action_id': action_id,
                    'action_type': "D",
                    'action_info': action_info,
                    'conditional_expression': "",
                    'conditional_input': "",
                    'chg_date': datetime.now().strftime('%d-%m-%y'),
                    'chg_user': "System",
                    'chg_term': "System",
                    'max_retry_count': 0
                }
                logger.log(f"followup_act: {followup_act}")

                self.check_or_update_followup_act(followup_act, conn, db_vendore)

            elif str(main_text).startswith("email"):
                action_word = parts[0][3:]
                if 'add' == action_word.lower() or 'edit' == action_word.lower():
                    action_id = "save"
                else:
                    action_id = action_word

                pattern = r"email\((.*)\)"
                match = re.search(pattern, main_text)

                if match:
                    logger.log(f'Inside match for followup_act ::: {match}')
                    inside_parentheses = match.group(1)
                    logger.log(f'Inside inside_parentheses for followup_act ::: {inside_parentheses}')
                    action_info = inside_parentheses.split(",")[-2].replace("'","")
                logger.log(f"email action_id: {action_id}")
                logger.log(f"email action_info: {action_info}")
                deployment_log(f"OBJ_FOLLOWUP_ACT email action_id: {action_id}")
                deployment_log(f"OBJ_FOLLOWUP_ACT email action_info: {action_info}")

                followup_act = {
                    'obj_name': obj_name,
                    'line_no': str(index+1),
                    'action_id': action_id,
                    'action_type': "E",
                    'action_info': action_info,
                    'conditional_expression': "",
                    'conditional_input': "",
                    'chg_date': datetime.now().strftime('%d-%m-%y'),
                    'chg_user': "System",
                    'chg_term': "System",
                    'max_retry_count': 0
                }
                logger.log(f"followup_act: {followup_act}")

                self.check_or_update_followup_act(followup_act, conn, db_vendore)

                # -----------------------------------------------------------------------------

                format_code = ''
                body_mail = ''
                send_to = ''
                if match:
                    logger.log(f'Inside match ::: {match}')
                    inside_parentheses = match.group(1)
                    logger.log(f'Inside inside_parentheses ::: {inside_parentheses}')
                    pattern1 = r"\((.*)\)"
                    match1 = re.search(pattern1, inside_parentheses)
                    if match1:
                        logger.log(f'Inside match1 ::: {match1}')
                        send_to_lst = []
                        for data in match1.group(1).split(","):
                            send_to_lst.append('{(E)ROLE_CODE}')
                        send_to = ",".join(send_to_lst)
                    else:
                        send_to_word = inside_parentheses.split(",")[0].replace("'","")
                        logger.log(f"send_to_word ::: {send_to_word}")
                        if send_to_word == 'CUSTOMER_EMAIL':
                            send_to = "{(C)cust_code}"
                        else:
                            send_to = "{(E)ROLE_CODE}"

                    parts = inside_parentheses.split(",")
                    format_code = parts[-2].replace("'","")
                    body_mail = parts[-1].replace("'","")
                    logger.log(f"send_to ::: {send_to}")
                    logger.log(f"format_code ::: {format_code}")
                    logger.log(f"body_mail ::: {body_mail}")

                deployment_log(f"OBJ_FOLLOWUP_ACT send_to : {send_to}")
                deployment_log(f"OBJ_FOLLOWUP_ACT format_code : {format_code}")
                deployment_log(f"OBJ_FOLLOWUP_ACT body_mail : {body_mail}")

                cursor = conn.cursor()
                deployment_log(f"MAIL_FORMAT table select query ::: SELECT COUNT(*) FROM MAIL_FORMAT WHERE FORMAT_CODE = '{format_code}'")
                cursor.execute(f"""
                    SELECT COUNT(*) FROM MAIL_FORMAT 
                    WHERE FORMAT_CODE = '{format_code}'
                """)

                count_mail_format = cursor.fetchone()[0]
                logger.log(f"Count MAIL_FORMAT {count_mail_format}")
                deployment_log(f"MAIL_FORMAT table select query result :::  {count_mail_format}")
                cursor.close()

                if count_mail_format > 0:
                    cursor = conn.cursor()
                    delete_query = f"""
                        DELETE FROM MAIL_FORMAT 
                        WHERE FORMAT_CODE = '{format_code}'
                    """
                    logger.log(f"\n--- Class Obj_Followup_Act ---\n")
                    logger.log(f"{delete_query}")
                    deployment_log(f"MAIL_FORMAT table delete query :::  {delete_query}")
                    cursor.execute(delete_query)
                    cursor.close()
                    logger.log("Data deleted from MAIL_FORMAT")
                    deployment_log("Data deleted from MAIL_FORMAT") 

                cursor = conn.cursor()
                if db_vendore == 'Oracle':
                    insert_query = """
                        INSERT INTO MAIL_FORMAT (
                            FORMAT_CODE, FORMAT_TYPE, SEND_TO, COPY_TO, BLIND_COPY, SUBJECT, BODY_COMP, PRIORITY,
                            DELIVERY_REPORT, RETURN_RECEIPT, MAIL_APPLICATION, MAIL_SERVER, MAIL_BOX, MAIL_ID, ATTACH_TYPE,
                            ATTACH_TEXT, WINNAME, WIN_NAME, MAIL_GENERATION, MAIL_DESCR, FN_NAME, COND_METHOD,
                            EMAIL_EXPR, ATTACH_OBJECT, TEMPLATE_PURPOSE, STATUS, USER_ID__OWN, BODY_TEXT
                        ) VALUES (
                            :format_code, :format_type, :send_to, :copy_to, :blind_copy, :subject, :body_comp, :priority,
                            :delivery_report, :return_receipt, :mail_application, :mail_server, :mail_box, :mail_id, :attach_type,
                            :attach_text, :winname, :win_name, :mail_generation, :mail_descr, :fn_name, :cond_method,
                            :email_expr, :attach_object, :template_purpose, :status, :user_id__own, :body_text
                        )
                    """
                    values = {
                        'format_code': format_code,
                        'format_type': 'T',
                        'send_to': send_to,
                        'copy_to': '',
                        'blind_copy': '',
                        'subject': body_mail,
                        'body_comp': '',
                        'priority': '',
                        'delivery_report': '',
                        'return_receipt': '',
                        'mail_application': 'M',
                        'mail_server': '',
                        'mail_box': '',
                        'mail_id': '',
                        'attach_type': '',
                        'attach_text': '',
                        'winname': '',
                        'win_name': f'w_{obj_name}',
                        'mail_generation': '',
                        'mail_descr': '',
                        'fn_name': '',
                        'cond_method': '',
                        'email_expr': '',
                        'attach_object': '',
                        'template_purpose': '',
                        'status': '',
                        'user_id__own': '',
                        'body_text': body_mail
                    }
                    logger.log(f"\n--- Class Obj_Followup_Act ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"MAIL_FORMAT table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"MAIL_FORMAT table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in MAIL_FORMAT table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO MAIL_FORMAT (
                            FORMAT_CODE, FORMAT_TYPE, SEND_TO, COPY_TO, BLIND_COPY, SUBJECT, BODY_COMP, PRIORITY,
                            DELIVERY_REPORT, RETURN_RECEIPT, MAIL_APPLICATION, MAIL_SERVER, MAIL_BOX, MAIL_ID, ATTACH_TYPE,
                            ATTACH_TEXT, WINNAME, WIN_NAME, MAIL_GENERATION, MAIL_DESCR, FN_NAME, COND_METHOD,
                            EMAIL_EXPR, ATTACH_OBJECT, TEMPLATE_PURPOSE, STATUS, USER_ID__OWN, BODY_TEXT
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s
                        )
                    """
                    values = (
                        format_code, 'T', send_to, None, None, body_mail, None, None,
                        None, None, 'M', None, None, None, None, None,
                        None, f'w_{obj_name}', None, None, None, None,
                        None, None, None, None, None, body_mail
                    )
                    logger.log(f"\n--- Class Obj_Followup_Act ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"MAIL_FORMAT table insert query for Other database ::: {insert_query}")
                    deployment_log(f"MAIL_FORMAT table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in MAIL_FORMAT table for Other database.")
                cursor.close()

        logger.log(f"End of Obj_Followup_Act Class")
        deployment_log(f"End of Obj_Followup_Act Class")
