from .TransDatabaseOracle import TransDatabaseOracle 
from .TransDatabaseDremio import TransDatabaseDremio
from .TransDatabaseInMemory import TransDatabaseInMemory
from .TransDatabaseMySql import TransDatabaseMySql 
from .TransDatabaseMSSQLServer import TransDatabaseMSSQLServer 
from .TransDatabaseSAPHANA import TransDatabaseSAPHANA 
from .TransDatabasePostgress import TransDatabasePostgress
from DatabaseConnectionUtility import Oracle 
from DatabaseConnectionUtility import Dremio
from DatabaseConnectionUtility import InMemory 
from DatabaseConnectionUtility import Oracle
from DatabaseConnectionUtility import MySql
from DatabaseConnectionUtility import MSSQLServer 
from DatabaseConnectionUtility import SAPHANA
from DatabaseConnectionUtility import Postgress
import loggerutility as logger
from flask import Flask, request
import traceback
import json

class TransDatabasecatlog:
    
    tableName=""
    connectObj=None
    def getTransTableDetails(self): 
        try:
            logger.log(f"Inside getTableDetails","0")
            
            jsonData = request.get_data('jsonData', None)
            jsonData = json.loads(jsonData[9:])
            logger.log(f"jsonData: {jsonData}","0")
            
            dbDetails   = jsonData['dbDetails']
            userInfo    = jsonData['userInfo']['UserInfo']
            serviceName = jsonData['serviceName']
            
            if 'tableName' in jsonData.keys():
                if jsonData['tableName'] != None and jsonData['tableName'] != "":
                    self.tableName   = jsonData['tableName']

            dbDetails["NAME"] = dbDetails.pop("DB_USER_NAME")
            dbDetails["KEY"]  = dbDetails.pop("LOGPASSWORD")
            dbDetails["URL"]  = dbDetails.pop("DB_URL")
            
            if dbDetails['DB_VENDORE'] != None:
                klass = globals()[dbDetails['DB_VENDORE']]
                dbObject = klass()
                connectObj = dbObject.getConnection(dbDetails)

            klass = globals()["TransDatabase" + dbDetails["DB_VENDORE"]]
            dbObject = klass()
            
            if serviceName == "tables":
                return json.dumps(dbObject.getTables(connectObj, dbDetails, userInfo, self.tableName))
            
            elif serviceName == "tablesStructure":
                return json.dumps(dbObject.getColumns(connectObj, self.tableName, userInfo, dbDetails))

            elif serviceName == "TableData":
                return str(dbObject.getTableData(connectObj, self.tableName, userInfo, dbDetails))

            else:
                logger.log(f"Invalid serviceName: {serviceName}","0")
                return str(f"Invalid serviceName: {serviceName}")
            
        except NameError as nameError:
            trace = traceback.format_exc()
            descr = str("Undefined Variable: " + str(nameError))
            returnErr = self.getErrorXml(descr, trace)
            logger.log(f'\n Exception returnString inside DB_Catlog : {returnErr}', "0")
            return str(returnErr)
        
        except Exception as e:
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = self.getErrorXml(descr, trace)
            logger.log(f'\n Exception returnString inside DB_Catlog : {returnErr}', "0")
            return str(returnErr)

    
    def getErrorXml(self, descr, trace):
        errorXml = '''<Root>
                            <Header>
                                <editFlag>null</editFlag>
                            </Header>
                            <Errors>
                                <error type="E">
                                    <message><![CDATA['''+descr+''']]></message>
                                    <trace><![CDATA['''+trace+''']]></trace>
                                    <type>E</type>
                                </error>
                            </Errors>
                        </Root>'''
        return errorXml

