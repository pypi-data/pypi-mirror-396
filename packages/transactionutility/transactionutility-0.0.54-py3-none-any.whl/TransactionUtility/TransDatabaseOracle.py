#    -- WORKING  07-SEPT-2022  --

import loggerutility as logger
import pandas as pd
import traceback

class TransDatabaseOracle:
    
    def getTables(self,connectObj, dbDetails, userInfo, tableName=""):
        logger.log(f"inside oracle getTables","0")
        resultStr = ""
        transDB = ""
        schemaName = ""
        isTableFound = False
        maxCount = "500"
        
        if "transDB" in userInfo.keys():
            if len(userInfo["transDB"]) != 0 : 
               transDB = userInfo["transDB"]
        logger.log(f"transDB: {transDB}","0")

        if "schemaName" in dbDetails.keys():
            if len(userInfo["schemaName"]) != 0 : 
               schemaName = dbDetails["schemaName"]
               logger.log(f"schemaName: {schemaName}","0")
               connectObj.current_schema = schemaName
        try:
            if (len(userInfo) != 0):
                cursor = connectObj.cursor()
                if ("" == tableName):	
                    selectQuery = "SELECT OBJECT_NAME FROM ALL_OBJECTS WHERE (OBJECT_TYPE='TABLE' OR OBJECT_TYPE='SYNONYM') AND  OWNER= '" + transDB +"' AND ROWNUM <= " + maxCount   
                    logger.log(f"selectQuery {selectQuery}","0")
                    cursor.execute(selectQuery)
                    resultStr = cursor.fetchall()
                    
                    tableJson={"Root":{"TABLEDETAILS":[]}}
                    for i in resultStr:
                        isTableFound = True
                        tableJson["Root"]["TABLEDETAILS"].append( { "TABLE_NAME" : i[0] } ) 
                    
                else:
                    logger.log(f"Oracle getTables else","0")
                    tableName = "'%"+tableName+"%'";
                    selectQuery =  "SELECT OBJECT_NAME FROM ALL_OBJECTS WHERE (OBJECT_TYPE='TABLE' OR OBJECT_TYPE='SYNONYM') AND  OWNER= '" +transDB.upper()+ "' AND OBJECT_NAME LIKE " + tableName.upper()  
                    
                    logger.log(f"SelectQuery oracle getTables: {selectQuery}","0")
                    cursor.execute(selectQuery)
                    resultStr = cursor.fetchall()
                    
                    tableJson={"Root":{"TABLEDETAILS":[]}}
                    for i in resultStr:
                        isTableFound = True
                        tableJson["Root"]["TABLEDETAILS"].append( { "TABLE_NAME" : i[0] } ) 
                    # logger.log(f"TableJson :{tableJson}","0")
            
                if(not isTableFound ) : 
                    resultStr = self.getErrorXml("Tables not found in the Oracle Database against the Schema "+transDB+"", "Table not Exist")
                    logger.log(f"error String Oracle getTables: {resultStr}", "0")
            
            resultStr = tableJson
            logger.log(f"resultStr : {resultStr}", "0")
            
        except Exception as e:
            trace = traceback.format_exc()
            descr = str(e)
            logger.log(f"{self.getErrorXml(descr, trace)}","0")
        
        finally:
            if (connectObj != None):
                connectObj.close()
                logger.log(f"Oracle DB connection closed","0")
        return resultStr
                
    def getColumns(self, connectObj, tableNames, userInfo, dbDetails):
        
        logger.log(f"inside Oracle getColumns()", "0")
        if "transDB" in userInfo.keys():
            if len(userInfo["transDB"]) != 0: 
                transDB = userInfo["transDB"]

        if "schemaName" in dbDetails.keys():
            if len(userInfo["schemaName"]) != 0 : 
               schemaName = dbDetails["schemaName"]
               logger.log(f"schemaName: {schemaName}","0")
               connectObj.current_schema = schemaName
                
        resultStr = ""
        tableArray = tableNames.split(",")            
        counter = 0 
        mainDataArray=[]
                        
        try:
            if len(userInfo) != 0 :
                if  (tableNames !=  "") and (tableNames != None):
                     
                    for j in range(len(tableArray)):
                        
                        columnDataArray=[]
                        mainDataJson = {}
                        currentTable= tableArray[j]
                        selectQuery = " SELECT COLUMN_NAME, DATA_LENGTH, DATA_TYPE, NULLABLE FROM ALL_TAB_COLUMNS WHERE TABLE_NAME= '"+ tableArray[j]+"' and OWNER= '" + transDB.upper() + "'"     
                        logger.log(f"selectQuery: {selectQuery}","0")
                        
                        cursor = connectObj.cursor()
                        cursor.execute(selectQuery)
                        resultStr = cursor.fetchall()
                        logger.log(f"resultStr line 107: {resultStr}","0")
                        
                        for i in range(len(resultStr)):
                            counter+=1
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
                                logger.log(f"expression : {expression}","0")
                            
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
                    
                    logger.log(f"mainDataArray Oracle : {mainDataArray}","0")
                    connectObj.close()
                    connectObj = None
            
            resultStr = mainDataArray
            logger.log(f"resultStr: {resultStr}","0")
        except Exception as e:
            trace = traceback.format_exc()
            descr = str(e)
            logger.log(f"{self.getErrorXml(descr, trace)}","0")
        
        finally:
            if connectObj != None:
                connectObj.close()
                logger.log(f"Oracle getColumns Connection closed. ","0" )
        
        return resultStr	
    
    def getTableData(self, connectObj, tableName, userInfo, dbDetails):
        selectQuery = "SELECT * FROM " + tableName + " WHERE ROWNUM <= 50"
        logger.log(f"selectQuery: {selectQuery}","0")
        df = pd.read_sql(selectQuery, connectObj)
        tableDataJson = df.assign( **df.select_dtypes(['datetime']).astype(str).to_dict('list') ).to_json(orient="records")
        logger.log(f"Inside DbOracle gettabledata tableDataJson: {tableDataJson}","0")
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

    
