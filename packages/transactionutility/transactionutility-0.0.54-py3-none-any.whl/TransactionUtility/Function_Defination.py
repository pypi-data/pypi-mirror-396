import loggerutility as logger
from loggerutility import deployment_log

class Function_Defination:

    def execute_function(self, function_sql, connection):
        logger.log(f"Start of Function_Defination Class")
        deployment_log(f"\n--------------------------------- Start of Function_Defination Class -------------------------------------\n")
        for i, func in enumerate(function_sql, start=1):
            logger.log(f"Function {i}:\n{'-'*80}\n{func}\n{'-'*80}")
            deployment_log(f"Function {i}:\n{'-'*80}\n{func}\n{'-'*80}")

            cursor = connection.cursor()
            cursor.execute(func)
            logger.log(f"Function {i} executed successfully.")
            deployment_log(f"Function {i} executed successfully.")

            cursor.close()
        logger.log(f"End of Function_Defination Class")
        deployment_log(f"End of Function_Defination Class")
            

