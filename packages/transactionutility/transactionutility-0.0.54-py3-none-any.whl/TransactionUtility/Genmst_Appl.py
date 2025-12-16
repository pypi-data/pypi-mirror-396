import cx_Oracle
import loggerutility as logger

class Genmst_Appl:

    data_to_insert = [
        {'TRAN_ID':'T1','LINE_NO':9,'SCOPE':'z','SCOPE_DATA':'z'},
        {'TRAN_ID':'T2','LINE_NO':99,'SCOPE':'Z','SCOPE_DATA':'Z'}
    ]

    def check_and_update_tran_id(self, tran_data, connection):
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT COUNT(*) FROM genmst_appl 
            WHERE TRAN_ID = '{tran_data['TRAN_ID']}'
        """)
        count = cursor.fetchone()[0]

        if count > 0:
            update_query = f"""
                UPDATE genmst_appl SET
                    LINE_NO = '{tran_data['LINE_NO']}',
                    SCOPE = '{tran_data['SCOPE']}',
                    SCOPE_DATA = '{tran_data['SCOPE_DATA']}'
                WHERE TRAN_ID = '{tran_data['TRAN_ID']}'
            """

            cursor.execute(update_query)
            logger.log(f"Updated: TRAN_ID {tran_data['TRAN_ID']}")
        else:
            insert_query = f"""
                INSERT INTO genmst_appl (
                    TRAN_ID, LINE_NO, SCOPE, SCOPE_DATA
                ) VALUES (
                    '{tran_data['TRAN_ID']}', '{tran_data['LINE_NO']}', '{tran_data['SCOPE']}', '{tran_data['SCOPE_DATA']}'
                )
            """

            cursor.execute(insert_query)
            logger.log(f"Inserted: TRAN_ID {tran_data['TRAN_ID']}")
        cursor.close()

    def process_data(self, conn):
        for data in self.data_to_insert:
            self.check_and_update_tran_id(data, conn)
