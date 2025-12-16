import cx_Oracle
import psycopg2
from collections import defaultdict
import loggerutility as logger
from loggerutility import deployment_log

class Dynamic_Table_Creation:
        
    def check_table_exists(self, table_name, connection, con_type):
        if not connection:
            return False
        cursor = connection.cursor()
        logger.log(f"Connection type ::: {con_type}")
        if con_type == 'Postgress':
            table_name = table_name.lower()
        else:
            table_name = table_name.upper()
        try:
            if con_type == 'Oracle':
                query = f"""
                    SELECT COUNT(*) FROM (
                        SELECT table_name AS name FROM USER_TABLES WHERE table_name = '{table_name}'
                        UNION
                        SELECT synonym_name AS name FROM USER_SYNONYMS WHERE synonym_name = '{table_name}'
                    )
                """
            else:
                query = f"""
                    SELECT COUNT(*) FROM (
                        SELECT table_name AS name FROM information_schema.tables WHERE table_name = '{table_name}'
                        UNION
                        SELECT table_name AS name FROM information_schema.views WHERE table_name = '{table_name}'
                    ) AS combined
                """
            deployment_log(f"Table exist select query ::: {query}")
            cursor.execute(query)
            count = cursor.fetchone()[0]
            cursor.close()
            logger.log(f"Object existence count: {count}")
            deployment_log(f"Table exist select query result ::: {count}")
            return count > 0

        except (cx_Oracle.Error, psycopg2.Error) as error:
            logger.log(f"Error checking existence: {error}")
            deployment_log(f"Table exist select query Error ::: {error}")
            raise Exception(f"{error}")
        
    def check_column_exists(self, table_name, column_name, connection, con_type):
        if not connection:
            return False
        cursor = connection.cursor()
        if con_type == 'Postgress':
            table_name = table_name.lower()
            column_name = column_name.lower()
        else:
            table_name = table_name.upper()
            column_name = column_name.upper()
        try:
            if con_type == 'Oracle':
                deployment_log(f"Column exist in table select query for Oracle database ::: SELECT COUNT(*) as CNT FROM all_tab_columns WHERE table_name = '{table_name}' AND column_name = '{column_name}'")
                cursor.execute(f"""SELECT COUNT(*) as CNT FROM all_tab_columns WHERE table_name = '{table_name}' AND column_name = '{column_name}'""")
            else:
                deployment_log(f"Column exist in table select query for Other database ::: SELECT COUNT(*) as CNT FROM information_schema.columns WHERE table_name = '{table_name}' AND column_name = '{column_name}'")
                cursor.execute(f"""SELECT COUNT(*) as CNT FROM information_schema.columns WHERE table_name = '{table_name}' AND column_name = '{column_name}'""")
            count = cursor.fetchone()[0]
            cursor.close()
            deployment_log(f"Column exist in table select query result ::: {count}")
            return count > 0
        except (cx_Oracle.Error, psycopg2.Error) as error:
            logger.log(f"Error checking if column {column_name} exists in {table_name}: {error}")
            deployment_log(f"Column exist in table select query ::: Error checking if column {column_name} exists in {table_name}: {error}")
            raise Exception(f"{error}")
        
    def drop_constraint(self, table_name, schema_name, connection, con_type):

        cursor = connection.cursor()
        if con_type == 'Postgress':
            table_name = table_name.lower()
            schema_name = schema_name.lower()
        else:
            table_name = table_name.upper()
            schema_name = schema_name.upper()
        try:
            if con_type == 'Oracle':
                query = f"""
                    SELECT ac.constraint_name FROM all_constraints ac
                    WHERE ac.table_name = '{table_name}'
                    AND ac.constraint_type = 'P'
                    AND ac.owner = '{schema_name}'
                """
            else:
                query = f"""
                    SELECT ac.constraint_name FROM information_schema.table_constraints ac
                    WHERE ac.table_name = '{table_name}'
                    AND ac.constraint_type = 'PRIMARY KEY'
                    AND ac.table_schema = '{schema_name}'
                """

            logger.log(f"\n--- Class Dynamic_Table_Creation ---\n")
            logger.log(f"{query}")
            deployment_log(f"Drop constraint select query ::: {query}")
            cursor.execute(query)
            constraint = cursor.fetchone()
            deployment_log(f"Drop constraint select query result::: {constraint}")

            if constraint:
                constraint_name = constraint[0]
                logger.log(f"Found constraint: {constraint_name} on table {table_name}")
                deployment_log(f"Found constraint: {constraint_name} on table {table_name}")
 
                drop_query = f"ALTER TABLE {schema_name}.{table_name} DROP CONSTRAINT {constraint_name}"
                logger.log(f"Class Dynamic_Table_Creation drop_query::: {drop_query}")
                logger.log(f"\n--- Class Dynamic_Table_Creation ---\n")
                deployment_log(f"Drop constraint alter query ::: {drop_query}")
                cursor.execute(drop_query)
                logger.log(f"Constraint {constraint_name} dropped successfully from table {table_name}.")
                deployment_log(f"Constraint {constraint_name} dropped successfully from table {table_name}.")
            
        except (cx_Oracle.Error, psycopg2.Error) as error:
            logger.log(f"Error while dropping constraint from table {table_name}: {error}")
            deployment_log(f"Error while dropping constraint from table {table_name}: {error}")
            raise Exception(f"{error}")

        finally:
            cursor.close()

    def get_primary_key_columns(self, table_name, schema_name, connection, con_type):
        primary_key_columns = []
        if con_type == 'Postgress':
            table_name = table_name.lower()
            schema_name = schema_name.lower()
        else:
            table_name = table_name.upper()
            schema_name = schema_name.upper()
        
        if con_type == 'Oracle':
            query = f"""
                SELECT acc.column_name
                FROM all_cons_columns acc
                JOIN all_constraints ac ON acc.constraint_name = ac.constraint_name
                WHERE ac.table_name = '{table_name}'
                AND ac.constraint_type = 'P'
                AND ac.owner = '{schema_name}'
            """
        else:
            query = f"""
                SELECT kcu.column_name FROM information_schema.key_column_usage kcu
                JOIN information_schema.table_constraints tc 
                ON kcu.constraint_name = tc.constraint_name
                WHERE 
                    tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_name = '{table_name}'
                    AND tc.table_schema = '{schema_name}'
            """
        cursor = connection.cursor()

        try:
            logger.log(f"Class Dynamic_Table_Creation query::: {query}")
            logger.log(f"\n--- Class Dynamic_Table_Creation ---\n")
            logger.log(f"{query}")
            deployment_log(f"Get primary key columns select query ::: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
            deployment_log(f"Get primary key columns select query result::: {rows}")
            for row in rows:
                primary_key_columns.append(row[0])
            logger.log(f"Primary key columns for table {table_name}: {primary_key_columns}")
            deployment_log(f"Primary key columns for table {table_name}: {primary_key_columns}")
            
        except (cx_Oracle.Error, psycopg2.Error) as error:
            logger.log(f"Error fetching primary key columns for table {table_name}: {error}")
            deployment_log(f"Error fetching primary key columns for table {table_name}: {error}")
            raise Exception(f"{error}")

        finally:
            cursor.close()
        
        return primary_key_columns
    
    def add_primary_key_constraint(self, table_name, column_name_list, connection):

        pk_constraint = f"{table_name}_pk"
        pk_constraint_list = ",".join(column_name_list)
        query = f"""
            ALTER TABLE {table_name}
            ADD CONSTRAINT {pk_constraint} PRIMARY KEY ({pk_constraint_list})
        """
        logger.log(f"Generated query to add primary key constraint: {query}")
        cursor = connection.cursor()
        try:
            logger.log(f"Class Dynamic_Table_Creation query::: {query}")
            logger.log(f"\n--- Class Dynamic_Table_Creation ---\n")
            deployment_log(f"Add primary key constaint alter query ::: {query}")
            cursor.execute(query)
            logger.log(f"Primary key constraint {pk_constraint} added successfully to table {table_name}.")
            deployment_log(f"Primary key constraint {pk_constraint} added successfully to table {table_name}.")
        except (cx_Oracle.Error, psycopg2.Error) as error:
            logger.log(f"Error adding primary key constraint to table {table_name}: {error}")
            deployment_log(f"Error adding primary key constraint to table {table_name}: {error}")
            raise Exception(f"{error}")
        finally:
            cursor.close()

    def create_new_table(self, table_lst, connection, con_type):
        cursor = connection.cursor()

        for table_name, columns in table_lst.items():
            columns_sql = []
            primary_key_columns = []

            for single_col in columns:
                col_name = single_col['db_name']
                col_type = single_col['col_type'].upper()
                db_size = single_col.get('db_size', None)
                is_key = single_col.get('key', False)
                mandatory = single_col.get('mandatory', 'false')

                if db_size:
                    db_size = db_size.split(",")[0] if "," in db_size else db_size

                if col_type in ['CHAR', 'VARCHAR'] and db_size:
                    if db_size == '0':
                        col_def = f"{col_name} {col_type}(10)"  
                    else:
                        col_def = f"{col_name} {col_type}({db_size})"
                
                elif col_type == 'DECIMAL':
                    if db_size and db_size != '0':
                        col_def = f"{col_name} NUMERIC({db_size}, 2)"  
                    else:
                        col_def = f"{col_name} NUMERIC(5, 2)"
                
                elif col_type == 'DATETIME':
                    col_def = f"{col_name} DATE"
                
                elif col_type == 'NUMBER':  
                    if con_type == 'Oracle':
                        col_def = f"{col_name} NUMBER"
                    else:
                        col_def = f"{col_name} NUMERIC"

                else:
                    col_def = f"{col_name} {col_type}"

                if mandatory == 'true' or mandatory == True:
                    col_def += " NOT NULL"

                if is_key:
                    primary_key_columns.append(col_name)
                
                if col_def:
                    columns_sql.append(col_def)

            columns_sql_str = ", ".join(columns_sql)
            create_table_sql = f"CREATE TABLE {table_name} ({columns_sql_str})"

            logger.log(f"create_table_sql ::: {create_table_sql}")
            deployment_log(f"Create new table query ::: {create_table_sql}")

            try:
                logger.log(f"Class Dynamic_Table_Creation create_table_sql::: {create_table_sql}")
                cursor.execute(create_table_sql)
                logger.log(f"Table {table_name} created successfully.")
                deployment_log(f"Table {table_name} created successfully.")

                if primary_key_columns:
                    pk_constraint = f"{table_name}_pk"
                    pk_constraint_list = ", ".join(primary_key_columns)
                    pk_query = f"ALTER TABLE {table_name} ADD CONSTRAINT {pk_constraint} PRIMARY KEY ({pk_constraint_list})"

                    logger.log(f"pk_query :: {pk_query}")
                    deployment_log(f"Create new table add constraint alter query ::: {pk_query}")
                    cursor.execute(pk_query)

            except (cx_Oracle.Error, psycopg2.Error) as error:
                logger.log(f"Error creating table {table_name}: {error}")
                deployment_log(f"Error creating new table {table_name}: {error}")
                raise Exception(f"{error}")

        cursor.close()

    def alter_table_add_columns(self, table_name, single_col, connection, con_type):
        cursor = connection.cursor()

        col_name = single_col['db_name']
        col_type = single_col['col_type'].upper()
        db_size = single_col.get('db_size', None)

        if db_size:
            db_size = db_size.split(",")[0] if "," in db_size else db_size

        mandatory = single_col.get('mandatory', 'false')

        if col_type in ['CHAR', 'VARCHAR'] and db_size:
            col_def = f"{col_name} {col_type}({db_size})" if db_size != '0' else f"{col_name} {col_type}(10)"

        elif col_type == 'DECIMAL':
            col_def = f"{col_name} NUMERIC({db_size}, 2)" if db_size and db_size != '0' else f"{col_name} NUMERIC(5, 2)"

        elif col_type == 'DATETIME':
            col_def = f"{col_name} DATE"  

        elif col_type == 'NUMBER': 
            col_def = f"{col_name} NUMBER" if con_type == 'Oracle' else f"{col_name} NUMERIC"

        else:
            col_def = f"{col_name} {col_type}"

        if mandatory == 'true' or mandatory == True:
            col_def += " NOT NULL"

        if con_type == 'Oracle':
            alter_table_sql = f"ALTER TABLE {table_name} ADD ({col_def})"  
        else:
            alter_table_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_def}"  

        logger.log(f"Executing SQL: {alter_table_sql}")
        deployment_log(f"Alter existing table query ::: {alter_table_sql}")

        try:
            logger.log(f"Class Dynamic_Table_Creation alter_table_sql::: {alter_table_sql}")
            cursor.execute(alter_table_sql)
            logger.log(f"Column {col_name} added successfully to table {table_name}.")
            deployment_log(f"Column {col_name} added successfully to table {table_name}.")
        except (cx_Oracle.Error, psycopg2.Error) as error:
            logger.log(f"Error adding column {col_name} to table {table_name}: {error}")
            deployment_log(f"Error adding column {col_name} to table {table_name}: {error}")
            raise Exception(f"{error}")
        finally:
            cursor.close()
        
    def get_column_from_main_table(self, columns_lst, main_table, table_name, column_name, main_table_col):
        for column in columns_lst:
            column = column['column']
            logger.log(f"1st condition ::: {column['table_name'].upper()} == {main_table.upper()}")
            logger.log(f"3rd condition ::: {column['db_name'].upper()} == {main_table_col.upper()}")
            if column['table_name'].upper() == main_table.upper() and column['db_name'].upper() == main_table_col.upper():
                column['table_name'] = table_name.upper()
                column['db_name'] = column_name.upper()
                return column

    def create_alter_table(self, data, connection, schema_name, db_vendore):
        logger.log(f"Start of Dynamic_Table_Creation Class")
        deployment_log(f"\n--------------------------------- Start of Dynamic_Table_Creation Class -------------------------------------\n")
        try:
            if "transaction" in data and "sql_models" in data['transaction']:
                for index,sql_models in enumerate(data["transaction"]["sql_models"]):
                    logger.log(f"sql_models index ::: {index}")
                    columns = sql_models["sql_model"]["columns"]
                    table_json = defaultdict(list)
                    for column in columns:
                        column = column['column']
                        table_name = column['table_name']
                        column_name = column['db_name']
                        deployment_log(f"Checking {table_name.upper()} table exist in schema")
                        exists = self.check_table_exists(table_name.upper(), connection, db_vendore)
                        deployment_log(f"Table exist result ::: {exists}")
                        logger.log(f"exists ::: {exists}")
                        if exists:
                            logger.log(f"column_name ::: {column_name}")
                            deployment_log(f"Checking {column_name.upper()} column is exist in {table_name.upper()} table")
                            column_exist = self.check_column_exists(table_name.upper(), column_name.upper(), connection, db_vendore)
                            deployment_log(f"Column exist result ::: {column_exist}")
                            logger.log(f"column_exist ::: {column_exist}")
                            if not column_exist:
                                logger.log(f"Inside column_exist ::: {table_name.upper(), column}")
                                self.alter_table_add_columns(table_name.upper(), column, connection, db_vendore)
                                
                                if column['key'] == True:
                                    check_prmary_key_columns = self.get_primary_key_columns(table_name, schema_name, connection, db_vendore)
                                    logger.log(f"check:: {check_prmary_key_columns}")
                                    self.drop_constraint(table_name, schema_name, connection, db_vendore)
                                    check_prmary_key_columns.append(column_name)
                                    logger.log(f"check_prmary_key_columns ::: {check_prmary_key_columns}")
                                    self.add_primary_key_constraint(table_name,check_prmary_key_columns,connection)
                        else:
                            table_json[table_name.upper()].append(column)
                    logger.log(f"outside forloop ::: {dict(table_json)}")
                    self.create_new_table(dict(table_json), connection, db_vendore)
                    
                    if "joins" in sql_models["sql_model"] and "join_predicates" in sql_models["sql_model"]['joins'] and "joins" in sql_models["sql_model"]['joins']['join_predicates']:
                        join_Data_list = sql_models["sql_model"]['joins']['join_predicates']['joins']
                        for single_join in join_Data_list:
                            if single_join['main_table'] == False:
                                if isinstance(single_join['join_table'], list):
                                    main_table = single_join['join_table'][0].lower() if single_join['join_table'] else ''
                                else:
                                    main_table = single_join['join_table'].lower()
                                if isinstance(single_join['join_column'], list):
                                    main_table_col = single_join['join_column'][0].lower() if single_join['join_column'] else ''
                                else:
                                    main_table_col = single_join['join_column'].lower()
                                if isinstance(single_join['table'], list):
                                    table_name_toadd = single_join['table'][0].lower() if single_join['table'] else ''
                                else:
                                    table_name_toadd = single_join['table'].lower()
                                if isinstance(single_join['column'], list):
                                    column_name_toadd = single_join['column'][0].lower() if single_join['column'] else ''
                                else:
                                    column_name_toadd = single_join['column'].lower()
                                
                                if main_table_col == '':
                                    deployment_log(f"Join column is empty. So update the join column and then upload the model json.")
                                    raise Exception(f"Join column is empty. So update the join column and then upload the model json.")
                                
                                if column_name_toadd == '':
                                    deployment_log(f"Join column is empty. So update the join column and then upload the model json.")
                                    raise Exception(f"Join column is empty. So update the join column and then upload the model json.")
                                
                                deployment_log(f"Checking {table_name_toadd.upper()} table exist in schema")
                                exists = self.check_table_exists(table_name_toadd.upper(), connection, db_vendore)
                                deployment_log(f"Table exist result ::: {exists}")
                                logger.log(f"table_name ::: {table_name_toadd.upper()}")
                                logger.log(f"exists ::: {exists}")
                                if exists:
                                    logger.log(f"column_name ::: {column_name_toadd.upper()}")
                                    deployment_log(f"Checking {column_name_toadd.upper()} column is exist in {table_name_toadd.upper()} table")
                                    column_exist = self.check_column_exists(table_name_toadd.upper(), column_name_toadd.upper(), connection, db_vendore)
                                    deployment_log(f"Column exist result ::: {column_exist}")
                                    logger.log(f"column_exist ::: {column_exist}")
                                    if not column_exist:
                                        column = self.get_column_from_main_table(columns, main_table, table_name_toadd, column_name_toadd, main_table_col)
                                        logger.log(f"Inside column_exist join ::: {column}")
                                        self.alter_table_add_columns(table_name_toadd.upper(), column, connection, db_vendore)
                                        
                                        if column['key'] == True:
                                            check_prmary_key_columns = self.get_primary_key_columns(table_name_toadd, schema_name, connection, db_vendore)
                                            logger.log(f"check:: {check_prmary_key_columns}")
                                            self.drop_constraint(table_name_toadd, schema_name, connection, db_vendore)
                                            check_prmary_key_columns.append(column_name_toadd)
                                            logger.log(f"check_prmary_key_columns ::: {check_prmary_key_columns}")
                                            self.add_primary_key_constraint(table_name_toadd,check_prmary_key_columns,connection)
                                else:
                                    logger.log(f"column_name ::: {column_name_toadd.upper()}")
                                    deployment_log(f"Checking {column_name_toadd.upper()} column is exist in {table_name_toadd.upper()} table")
                                    column_exist = self.check_column_exists(table_name_toadd.upper(), column_name_toadd.upper(), connection, db_vendore)
                                    deployment_log(f"Column exist result ::: {column_exist}")
                                    logger.log(f"column_exist ::: {column_exist}")
                                    if not column_exist:
                                        column = self.get_column_from_main_table(columns, main_table, table_name_toadd, column_name_toadd, main_table_col)
                                        if column != None:
                                            table_json = defaultdict(list)
                                            table_json[table_name_toadd.upper()].append(column)
                                            self.create_new_table(dict(table_json), connection, db_vendore)
                                        else:
                                            deployment_log(f"Error in Json model. {table_name_toadd.upper()} is not exist in Column list.")
                                            raise Exception(f"Error in Json model. {table_name_toadd.upper()} is not exist in Column list.")

                                deployment_log(f"Checking {main_table.upper()} table exist in schema")
                                exists = self.check_table_exists(main_table.upper(), connection, db_vendore)
                                deployment_log(f"Table exist result ::: {exists}")
                                logger.log(f"table_name ::: {main_table.upper()}")
                                logger.log(f"exists ::: {exists}")
                                if exists:
                                    logger.log(f"column_name ::: {column_name_toadd.upper()}")
                                    deployment_log(f"Checking {main_table_col.upper()} column is exist in {main_table.upper()} table")
                                    column_exist = self.check_column_exists(main_table.upper(), main_table_col.upper(), connection, db_vendore)
                                    deployment_log(f"Column exist result ::: {column_exist}")
                                    logger.log(f"column_exist ::: {column_exist}")
                                    if not column_exist:
                                        column = self.get_column_from_main_table(columns, table_name_toadd, main_table, main_table_col, column_name_toadd)
                                        logger.log(f"Inside column_exist join ::: {column}")
                                        self.alter_table_add_columns(main_table.upper(), column, connection, db_vendore)
                                        
                                        if column['key'] == True:
                                            check_prmary_key_columns = self.get_primary_key_columns(main_table, schema_name, connection, db_vendore)
                                            logger.log(f"check:: {check_prmary_key_columns}")
                                            self.drop_constraint(main_table, schema_name, connection, db_vendore)
                                            check_prmary_key_columns.append(main_table_col)
                                            logger.log(f"check_prmary_key_columns ::: {check_prmary_key_columns}")
                                            self.add_primary_key_constraint(main_table,check_prmary_key_columns,connection)
                                else:
                                    logger.log(f"column_name ::: {column_name_toadd.upper()}")
                                    deployment_log(f"Checking {column_name_toadd.upper()} column is exist in {main_table.upper()} table")
                                    column_exist = self.check_column_exists(main_table.upper(), column_name_toadd.upper(), connection, db_vendore)
                                    deployment_log(f"Column exist result ::: {column_exist}")
                                    logger.log(f"column_exist ::: {column_exist}")
                                    if not column_exist:
                                        column = self.get_column_from_main_table(columns, table_name_toadd, main_table, main_table_col, column_name_toadd)
                                        if column != None:
                                            table_json = defaultdict(list)
                                            table_json[main_table.upper()].append(column)
                                            self.create_new_table(dict(table_json), connection, db_vendore)
                                        else:
                                            deployment_log(f"Error in Json model. {main_table.upper()} is not exist in Column list.")
                                            raise Exception(f"Error in Json model. {main_table.upper()} is not exist in Column list.")

            logger.log(f"End of Dynamic_Table_Creation Class")
            deployment_log(f"End of Dynamic_Table_Creation Class")
            return f"Success"
        except Exception as e:
            deployment_log(f"Error in dynamic table creation : {e}")
            raise(Exception(f"Error in dynamic table creation : {e}"))

