#    -- WORKING  07-SEPT-2022  --

import traceback
import pandas as pd
import loggerutility as logger

class TransDatabaseSnowFlake:
    
    def getTables(self,connectObj, dbDetails, userInfo, tableName=""):
        logger.log(f"Inside DatabaseSnowFlake getTables()","0")
        resultStr = ""
        isTableFound = False
        schemaName = ""
        maxCount="500"
        dbName = ""
        try:
            if len(userInfo) != 0:
                if dbDetails["DATABASE_SCHEMA"] != None or len(dbDetails["DATABASE_SCHEMA"]) > 0 :
                    dbName = dbDetails["DATABASE_SCHEMA"]
                    logger.log(f"dbName:::{dbName}", "0")
                    
                else:
                    if "transDB" in userInfo.keys():
                        if len(userInfo["transDB"]) != "" : 
                            dbName = userInfo["transDB"]
                
                schemaName =  "'" + dbName + "." + dbName + "'"
                logger.log(f"schemaName:::{schemaName}", "0")  
                
                if ("" == tableName) :	
                    selectQuery = '''select TABLE_NAME from INFORMATION_SCHEMA."TABLES" where table_type='TABLE' and table_schema= ''' + schemaName + " LIMIT " + maxCount
                    logger.log(f"Inside DatabaseSnowFlake getTables selectQuery: {selectQuery}","0")
                    cursor = connectObj.cursor()
                    cursor.execute(selectQuery)
                    resultStr = cursor.fetchall()
                    
                    tableJson={"Root":{"TABLEDETAILS":[]}}
                    for i in resultStr:
                        isTableFound = True
                        tableJson["Root"]["TABLEDETAILS"].append( { "TABLE_NAME" : i[0] }) 
                    logger.log(f"Inside DatabaseSnowFlake tablejson: {tableJson}","0")
                else:
                    tableName = "'%"+tableName+"%'";
                    selectQuery =  '''select TABLE_NAME from INFORMATION_SCHEMA.\"TABLES\" where table_type='TABLE' and table_schema='''+schemaName+" and table_name like "+tableName    
                    
                    logger.log(f"Inside DatabaseSnowFlake selectQuery: {selectQuery}","0")
                    cursor = connectObj.cursor()
                    cursor.execute(selectQuery)
                    resultStr = cursor.fetchall()
                    
                    tableJson={"Root":{"TABLEDETAILS":[]}}
                    for i in resultStr:
                        isTableFound = True
                        tableJson["Root"]["TABLEDETAILS"].append( { "TABLE_NAME" : i[0] } ) 
            
                resultStr = tableJson
                logger.log(f"Inside DatabaseSnowFlake resultStr getTables(): {resultStr}", "0")
                
            else:
                if not isTableFound:
                    resultStr = self.getErrorXml("Tables not found in the InMemory Database against the Schema "+schemaName+"", "Table not Exist")
                    logger.log(f"Inside DatabaseSnowFlake error String: {resultStr}","0")
            
        except Exception as e:
            trace = traceback.format_exc()
            descr = str(e)
            logger.log(f"{self.getErrorXml(descr, trace)}","0")
            
        finally:
            if connectObj != None:
                connectObj.close()
        
        return resultStr    
            
    def getColumns(self, connectObj, tableNames, userInfo, dbDetails):
        logger.log(f"Inside DatabaseSnowFlake getColumns ","0")
        resultStr=""        
        mainDataArray=[]
        dbName = ""

        if dbDetails["DATABASE_SCHEMA"] != None or len(dbDetails["DATABASE_SCHEMA"]) > 0 :
            dbName = dbDetails["DATABASE_SCHEMA"]
            logger.log(f"dbName:::{dbName}", "0")
            
        else:
            if "transDB" in userInfo.keys():
                if len(userInfo["transDB"]) != "" : 
                    dbName = userInfo["transDB"]
        
        schemaName =  "'" + dbName + "." + dbName + "'"
        logger.log(f"schemaName:::{schemaName}", "0")  

        try:
            if len(userInfo) != 0:  
                if  (tableNames !=  "") and (tableNames != None):
                    
                    tableArray = tableNames.split(",")
                    counter = 0 
                    
                    if connectObj != None:
                        logger.log(f" Connected InMemory.","0")

                    for j in range(len(tableArray)):
                        columnDataArray=[]
                        mainDataJson = {}
                        currentTable= tableArray[j]
                        
                        selectQuery = '''select COLUMN_NAME, COLUMN_SIZE, DATA_TYPE, IS_NULLABLE from INFORMATION_SCHEMA."COLUMNS" where table_name='''  + "'" + tableArray[j] + "'" + ''' AND table_schema=''' + schemaName                  
                        logger.log(f"selectQuery: {selectQuery}","0")
                        cursor = connectObj.cursor()
                        cursor.execute(selectQuery)
                        resultStr = cursor.fetchall()
                        
                        for i in range(len(resultStr)):
                            counter   += 1
                            columnData = {}
                            columnName = resultStr[i][0]
                            columnSize = resultStr[i][1] 
                            colType    = resultStr[i][2]
                            isNullable = resultStr[i][3]
                            javaType = ""   
                            defaultFunction = ""
                            expression = ""
                            content = (columnName.replace("_", " ")).title()
                            
                            if("CHAR".lower() == colType.lower()) or ("VARCHAR2".lower()==colType.lower()) or  ("VARCHAR".lower() == colType.lower()):
                                javaType = "java.lang.String"
                            
                            elif ("NUMBER".lower() == colType.lower()):
                                javaType = "java.math.BigDecimal"
                                defaultFunction = "SUM"
                            
                            elif ("DATE".lower() == colType.lower()):
                                javaType = "java.sql.Date"
                            
                            else:
                                javaType = "java.lang.String"
                                colType  = "CHAR"
                            
                            if( not"".lower() == defaultFunction.lower()):
                                expression = defaultFunction + "(" + columnName +")" 
                            
                            else:
                                pass
                            
                            columnData["db_name"]                           = columnName  
                            columnData["name"]                              = content     
                            columnData["db_size"]                           = columnSize  
                            columnData["key"]                               = "false"     
                            columnData["col_id"]                            = str(counter)
                            columnData["col_type"]                          = colType     
                            columnData["default_function"]                  = defaultFunction 
                            columnData["hidden"]                            = ""          
                            columnData["format"]                            = ""          
                            columnData["descr"]                             = content     
                            columnData["expression"]                        = expression  
                            columnData["table_name"]                        = currentTable
                            columnData["table_display_name"]                = currentTable.replace("_", " ").lower()  
                            columnData["group_name"]                        = ""          
                            columnData["heading"]                           = ""          
                            columnData["default_value"]                     = ""          
                            columnData["edit_mask"]                         = {"mask": "", "values":{"data":"", "display":""}}        
                            columnData["protect"]                           = ""          
                            columnData["mandatory"]                         = ""          
                            columnData["validations"]                       = ""          
                            columnData["x"]                                 = ""          
                            columnData["y"]                                 = ""          
                            columnData["tabsequence"]                       = ""
                            columnData["lookup"]                            = ""
                            columnData["item_change"]                       = ""
                            columnDataArray.append(columnData)
                    
                        mainDataJson["TABLE_NAME"]      =   currentTable
                        mainDataJson["COLUMN"]          =   columnDataArray
                        mainDataJson["DISPLAY_NAME"]    =   currentTable.replace("_", " ").lower()
                        mainDataArray.append(mainDataJson)
                        
                    connectObj.close()
                    connectObj = None
            
            resultStr = mainDataArray
            logger.log(f"resultStr getColumns(): {resultStr}","0")
        except Exception as e:
            trace = traceback.format_exc()
            descr = str(e)
            logger.log(f"{self.getErrorXml(descr, trace)}","0")
            
        finally:
            if connectObj != None:
                connectObj.close()
        
        return resultStr

    def getTableData(self, connectObj, tableName, userInfo, dbDetails):
        Database_Schema = ""
        if 'Database_Schema' in dbDetails.keys():
                if dbDetails['Database_Schema'] != None:
                    Database_Schema = dbDetails['Database_Schema']

        selectQuery = '''SELECT * FROM "''' + Database_Schema + '''".''' + tableName + " WHERE ROWNUM <= 50"
        logger.log(f"selectQuery: {selectQuery}","0")
        df = pd.read_sql(selectQuery, connectObj)
        tableDataJson = df.assign( **df.select_dtypes(['datetime']).astype(str).to_dict('list') ).to_json(orient="records")
        logger.log(f"tableDataJson: {tableDataJson}","0")
        return tableDataJson

    def getErrorXml(self, descr, trace):
        errorXml ='''<Root>
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

