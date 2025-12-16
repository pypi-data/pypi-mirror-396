# for 11.xml

import json
import loggerutility as logger
from collections import defaultdict

class GenerateBrowMetadataXML:

    header = '''<?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE Sybase_eDataWindow>
                <Sybase_eDataWindow>
                    <Release>9</Release>
                    <BaseDefinition>
                        <units>1</units>
                        <timer_interval>0</timer_interval>
                        <color>79741120</color>
                        <processing>0</processing>
                        <HTMLDW>no</HTMLDW>
                        <print>
                            <documentname></documentname>
                            <printername></printername>
                            <orientation>0</orientation>
                            <margin>
                                <left>24</left>
                                <right>24</right>
                                <top>24</top>
                                <bottom>24</bottom>
                            </margin>
                            <paper>
                                <source>0</source>
                                <size>0</size>
                            </paper>
                            <prompt>no</prompt>
                            <canusedefaultprinter>yes</canusedefaultprinter>
                            <buttons>no</buttons>
                            <preview.buttons>no</preview.buttons>
                            <cliptext>no</cliptext>
                            <overrideprintjob>no</overrideprintjob>
                        </print>
                    </BaseDefinition>
                    <Summary>
                        <height>0</height>
                        <color>536870912</color>
                    </Summary>
                    <Footer>
                        <height>0</height>
                        <color>536870912</color>
                    </Footer>
                    <Detail>
                        <height>523</height>
                        <color>536870912</color>
                    </Detail>'''

    footer = '''<HtmlTable>
                    <border>1</border>
                </HtmlTable>
                <HtmlGen>
                    <clientevents>1</clientevents>
                    <clientvalidation>1</clientvalidation>
                    <clientcomputedfields>1</clientcomputedfields>
                    <clientformatting>0</clientformatting>
                    <clientscriptable>0</clientscriptable>
                    <generatejavascript>1</generatejavascript>
                    <encodeselflinkargs>1</encodeselflinkargs>
                    <netscapelayers>0</netscapelayers>
                </HtmlGen>
                <Export.XML>
                    <headgroups>1</headgroups>
                    <includewhitespace>0</includewhitespace>
                    <metadatatype>0</metadatatype>
                    <savemetadata>0</savemetadata>
                </Export.XML>
                <Import.XML>
                </Import.XML>
                <Export.PDF>
                    <method>0</method>
                    <distill.custompostscript>0</distill.custompostscript>
                    <xslfop.print>0</xslfop.print>
                </Export.PDF>
            </Sybase_eDataWindow>
        '''

    jsonData = {}

    def get_Table_Column(self, column_detail ,joins_details):

        main_table = ''
        if "join_predicates" in joins_details and "joins" in joins_details['join_predicates']:
            for join in joins_details['join_predicates']['joins']:
                logger.log(f"join of BROMETA in get_Table_Column ::: {join}")
                if join.get('main_table') == True:
                    main_table = join.get('table').lower()

        initial_tag = f"<initial>{column_detail['default_value']}</initial>" if len(column_detail['default_value']) != 0 else "" 

        update_tags = (
            "<update>yes</update>\n<updatewhereclause>yes</updatewhereclause>\n<key>yes</key>"
            if main_table == column_detail['table_name'].lower() and column_detail['key'] == True
            else (
                "<update>yes</update>\n<updatewhereclause>yes</updatewhereclause>"
                if main_table == column_detail['table_name'].lower() else "<update>no</update>\n<updatewhereclause>no</updatewhereclause>"
            )
        )
        
        dropdown_tags = (
            "<values>\n" +
            "".join(
                f"<item display=\"{item['display']}\" data=\"{item['data']}\" />\n"
                for item in column_detail["edit_mask"].get("values", [])
            ) +
            "</values>"
            if "edit_mask" in column_detail and
            "mask" in column_detail["edit_mask"] and
            (column_detail["edit_mask"].get("mask", "") == "ddlb" or column_detail["edit_mask"].get("mask", "") == "multi_select")
            else ""
        )

        table_column_tag = f'''<table_column>
                            <type{' precision="3"' if column_detail['col_type'].lower() == 'number' else (
                                f' size="{"0" if column_detail["db_size"] == "" else (round(float(column_detail["db_size"].split(",")[0])) if "," in column_detail["db_size"] else round(float(column_detail["db_size"])))}"' 
                                if column_detail['col_type'].lower() != 'date' else ""
                            )}>{"decimal" if column_detail['col_type'].lower() == 'number' else "datetime" if column_detail['col_type'].lower() == 'date' else column_detail['col_type'].lower()}</type>
                            <name>{column_detail['db_name'].lower()}</name>
                            <dbname>{column_detail['table_name'].lower()}.{column_detail['db_name'].lower()}</dbname>
                            {update_tags}
                            {initial_tag}
                            {dropdown_tags}
                        </table_column>'''

        return table_column_tag
    
    def get_Text_Object(self, column_detail, x, y):
        
        # visible_tag = "<visible>1</visible>" if column_detail['HIDDEN'] == "" or column_detail['HIDDEN'] == "true"   else "<visible>0</visible>"
        
        text_object_tag = f'''<TextObject>
                                    <band>Detail</band>
                                    <alignment>1</alignment>
                                    <text>{column_detail['heading']}</text>
                                    <border>0</border>
                                    <color>0</color>
                                    <x>{x}</x>
                                    <y>{y}</y>
                                    <height>15</height>
                                    <width>{column_detail['width'] if column_detail['width'] else '200'}</width>
                                    <html>
                                        <valueishtml>0</valueishtml>
                                    </html>
                                    <name>{column_detail['db_name'].lower()}_t</name>
                                    <visible>{"1" if not column_detail['hidden'] 
                                            else "0" if str(column_detail['hidden']) == "1" 
                                            else "1" if str(column_detail['hidden']) == "0" 
                                            else "0" if (column_detail['hidden'] == True or column_detail['hidden'] == "true") 
                                            else "1" if (column_detail['hidden'] == False or column_detail['hidden'] == "false") 
                                            else "1"}</visible>
                                    <font>
                                        <face>Times New Roman</face>
                                        <height>-10</height>
                                        <weight>400</weight>
                                        <family>1</family>
                                        <pitch>2</pitch>
                                        <charset>0</charset>
                                    </font>
                                    <background>
                                        <mode>2</mode>
                                        <color>79741120</color>
                                    </background>
                            </TextObject>'''
        
        return text_object_tag
        
    def get_Column_Object(self, column_detail, x, y, tabsequence):
        tabsequence_tag = ""
        if 'protect' in column_detail.keys():
            if column_detail['protect'] == "1" or column_detail['protect'] == 1 or column_detail['protect'] == "true" or column_detail['protect'] == True:
                tabsequence_tag = f"<tabsequence>32766</tabsequence>"
            else:
                tabsequence_tag = f"<tabsequence>{tabsequence}</tabsequence>"
                tabsequence += 10

        if 'edit_mask' in column_detail and 'mask' in column_detail['edit_mask']:
            if column_detail['edit_mask']['mask'] == 'ddlb' or column_detail['edit_mask']['mask'] == 'multi_select':
                edit_style = f'''<EditStyle style="ddlb">
                                    <limit>{
                                        "0" if column_detail["db_size"] == "" 
                                        else (round(float(column_detail["db_size"].split(",")[0]))
                                            if "," in column_detail["db_size"] 
                                            else round(float(column_detail["db_size"])))
                                    }</limit>
                                    <allowedit>no</allowedit>
                                    <case>upper</case>
                                    <imemode>0</imemode>
                                    {"<required>yes</required>" if column_detail['mandatory'] == 'true' or column_detail['mandatory'] == True else ""}
                                </EditStyle>'''
            else:
                edit_style = f'''<EditStyle style="edit">
                                    <limit>{
                                        "0" if column_detail["db_size"] == "" 
                                        else (round(float(column_detail["db_size"].split(",")[0]))
                                            if "," in column_detail["db_size"] 
                                            else round(float(column_detail["db_size"])))
                                    }</limit>
                                    <case>upper</case>
                                    <focusrectangle>no</focusrectangle>
                                    <autoselect>yes</autoselect>
                                    <imemode>0</imemode>
                                    {"<required>yes</required>" if column_detail['mandatory'] == 'true' or column_detail['mandatory'] == True else ""}
                                </EditStyle>'''
        elif column_detail['col_type'].lower() == 'number':
            edit_style = f'''<EditStyle style="edit">
                                <limit>{
                                    "0" if column_detail["db_size"] == "" 
                                    else (round(float(column_detail["db_size"].split(",")[0]))
                                        if "," in column_detail["db_size"] 
                                        else round(float(column_detail["db_size"])))
                                }</limit>
                                <case>upper</case>
                                <focusrectangle>no</focusrectangle>
                                <autoselect>yes</autoselect>
                                <imemode>0</imemode>
                                {"<required>yes</required>" if column_detail['mandatory'] == 'true' or column_detail['mandatory'] == True else ""}
                            </EditStyle>'''
        elif column_detail['col_type'].lower() == 'date':
            edit_style = f'''<EditStyle style="editmask">
                                <mask>dd/mm/yy</mask>
                                <focusrectangle>no</focusrectangle>
                                <imemode>0</imemode>
                                {"<required>yes</required>" if column_detail['mandatory'] == 'true' or column_detail['mandatory'] == True else ""}
                            </EditStyle>'''
            
        elif column_detail['col_type'].lower() == 'datetime':
            edit_style = f'''<EditStyle style="editmask">
                                <mask>dd/mm/yy hh:mm:ss</mask>
                                <focusrectangle>no</focusrectangle>
                                <imemode>0</imemode>
                                {"<required>yes</required>" if column_detail['mandatory'] == 'true' or column_detail['mandatory'] == True else ""}
                            </EditStyle>'''
        else:
            edit_style = f'''<EditStyle style="edit">
                                <limit>{
                                    "0" if column_detail["db_size"] == "" 
                                    else (round(float(column_detail["db_size"].split(",")[0]))
                                        if "," in column_detail["db_size"] 
                                        else round(float(column_detail["db_size"])))
                                }</limit>
                                <case>upper</case>
                                <focusrectangle>no</focusrectangle>
                                <autoselect>yes</autoselect>
                                <imemode>0</imemode>
                                {"<required>yes</required>" if column_detail['mandatory'] == 'true' or column_detail['mandatory'] == True else ""}
                            </EditStyle>'''
            
        column_object_tag = f'''<ColumnObject>
                    <band>Detail</band>
                    <id>2</id>
                    <alignment>{'1' if column_detail['col_type'].upper() == 'NUMBER' else '0'}</alignment>
                    {tabsequence_tag}
                    <border>5</border>
                    <color>0</color>
                    <x>{x}</x>
                    <y>{y}</y>
                    <height>15</height>
                    <width>{column_detail['width'] if column_detail['width'] else '200'}</width>
                    <format>{'dd/mm/yy' if column_detail['col_type'].upper() == 'DATE' 
                            else 'dd/mm/yy hh:mm:ss' if column_detail['col_type'].upper() == 'DATETIME' 
                            else column_detail['format'] if column_detail['format'] != '' 
                            else '[Yes/No]' if ("edit_mask" in column_detail and "mask" in column_detail["edit_mask"] and column_detail["edit_mask"].get("mask", "") == "yes_no")
                            else '[general]'}</format>
                    <html>
                        <valueishtml>0</valueishtml>
                    </html>
                    <name>{column_detail['db_name'].lower()}</name>
                    <visible>{"1" if not column_detail['hidden'] 
                        else "0" if str(column_detail['hidden']) == "1" 
                        else "1" if str(column_detail['hidden']) == "0" 
                        else "0" if (column_detail['hidden'] == True or column_detail['hidden'] == "true") 
                        else "1" if (column_detail['hidden'] == False or column_detail['hidden'] == "false") 
                        else "1"}</visible>
                    {edit_style}
                    <font>
                        <face>Times New Roman</face>
                        <height>-10</height>
                        <weight>400</weight>
                        <family>1</family>
                        <pitch>2</pitch>
                        <charset>0</charset>
                    </font>
                    <background>
                        <mode>2</mode>
                        <color>16777215</color>
                    </background>
                </ColumnObject>'''

        return column_object_tag, tabsequence

   
    def retrival_query(self, sqlModel, column_detail_lst, argument_list):
        sql_query = ""
        columns   = []
        base_table = ""
        joins = []

        # for column in column_detail['column']:
        # if column_detail['checked'] == 'true' and not column_detail['default_function']:    # Original
        for column_data in column_detail_lst:
            column_detail = column_data['column']
            # if not column_detail['default_function']:
            alias = column_detail['name']
            col = f"{column_detail['table_name']}.{column_detail['db_name']}"
            columns.append(f"{col} AS {alias}")
            
            # Extract joins that are not on the same table
            joins = []
            # base_table = jsonData['sql_model']['columns'][0]['column'][0]['table_name'] # original
            
            base_table = sqlModel['columns'][0]['column']['table_name']
            
        if "joins" in sqlModel and "join_predicates" in sqlModel['joins'] and "joins" in sqlModel['joins']['join_predicates']:
            for join in sqlModel['joins']['join_predicates']['joins']:
                logger.log(f"join of BROMETA ::: {join}")
                if join['main_table'] == False and 'join_table' in join and join['table'] != join['join_table']:
                    if isinstance(join['join_column'], list):
                        join_col = join['join_column'][0] if join['join_column'] else ''
                    else:
                        join_col = join['join_column']
                    if isinstance(join['column'], list):
                        table_col = join['column'][0] if join['column'] else ''
                    else:
                        table_col = join['column']
                    if join_col == '':
                        raise Exception(f"Join column is empty. So update the join column and then upload the model json.")
                    if table_col == '':
                        raise Exception(f"Join column is empty. So update the join column and then upload the model json.")        
                    joins.append(f" LEFT JOIN {join['table']} ON {join['join_table']}.{join_col} = {join['table']}.{table_col}")

                # if join['main_table'] == 'true' and join['join_table'] and join['table'] != join['join_table']:
                #     joins.append(f"JOIN {join['join_table']} ON {join['table']}.{join['column']} = {join['join_table']}.{join['join_column']}")
            
        # Construct SQL query
        sql_query = f"SELECT {', '.join(columns)}\n FROM {base_table}\n"
        if joins:
            sql_query += ' '.join(joins)
        
        logger.log(f"GenerateBrowMetadataXML argument_list ::: {argument_list}")
        for argument_detail in argument_list:
            tableName = argument_detail[argument_detail.find("<table_name>") + 12 : argument_detail.find("</table_name>")]
            columnName = argument_detail[argument_detail.find("<name>") + 6 : argument_detail.find("</name>")]
            if "WHERE" in sql_query :
                sql_query += f" AND {tableName.upper()}.{columnName.upper()} = ? "
            else:
                sql_query += f" WHERE {tableName.upper()}.{columnName.upper()} = ? "

        logger.log(f"GenerateBrowMetadataXML sql query ::: {sql_query}")
        return sql_query

    def get_argument_list(self, column_detail_lst, joins_details, header_primary_key_lst):

        main_table = ''
        if "join_predicates" in joins_details and "joins" in joins_details['join_predicates']:
            for join in joins_details['join_predicates']['joins']:
                if join.get('main_table') == True:
                    main_table = join.get('table').lower()

        argument_object_list = []
        for column_data in column_detail_lst:
            column_detail = column_data['column']
            logger.log(f"column_detail table_name ::: {column_detail['table_name'].lower()}")
            logger.log(f"main_table ::: {main_table}")
            logger.log(f"header_primary_key_lst ::: {column_detail['db_name'].lower()}")
            logger.log(f"header_primary_key_lst ::: {header_primary_key_lst}")
            logger.log(f"header_primary_key_lst ::: {column_detail['key']}")
            if column_detail['key'] == True and column_detail['table_name'].lower() == main_table and column_detail['db_name'].lower() in header_primary_key_lst:
                logger.log(f"header_primary_key_lst inside")
                tableName           = column_detail['table_name'].lower()
                column_Name         = column_detail['db_name'].lower()
                column_Datatype     = column_detail['col_type'].lower()
                if column_Datatype == "char" or column_Datatype == "varchar2":
                    column_Datatype = "string"
                
                argument_tags       = f'''<argument>
                                            <table_name>{tableName}</table_name>
                                            <name>{column_Name}</name>
                                            <type>{column_Datatype}</type>
                                        </argument>'''
                argument_object_list.append(argument_tags)
        return argument_object_list
    
    def get_header_primary_key_list(self, column_detail_lst, joins_details):

        main_table = ''
        if "join_predicates" in joins_details and "joins" in joins_details['join_predicates']:
            for join in joins_details['join_predicates']['joins']:
                if join.get('main_table') == True:
                    main_table = join.get('table').lower()

        pk_list = []
        for column_data in column_detail_lst:
            column_detail = column_data['column']
            if column_detail['key'] == True and column_detail['table_name'].lower() == main_table:
                column_Name         = column_detail['db_name'].lower()
                pk_list.append(column_Name)
        return pk_list

    def get_join_object(self, sqlModel, column_detail):
        update_tag_list      = []
        update_tag           = ""

        if "joins" in sqlModel and "join_predicates" in sqlModel['joins'] and "joins" in sqlModel['joins']['join_predicates']:
            join_Data_list       = sqlModel['joins']['join_predicates']['joins']
        
            logger.log(f"join_Data_list ::: {join_Data_list}")
            if len(join_Data_list) == 1:
                logger.log(f"Inside")
                join_Data_list = join_Data_list[0]
                if "table" in join_Data_list:
                    logger.log(f"Inside1")
                    update_tag = f'''<updatewhere>0</updatewhere>
                                     <updatekeyinplace>no</updatekeyinplace>
                                     <update>{join_Data_list['table'].lower()}</update>'''
                    update_tag_list.append(update_tag)
                
            else: 
                logger.log(f"Outside")   
                for each_join_detail in join_Data_list :
                    if each_join_detail['main_table'] == True : 
                        logger.log(f"each_join_detail['main_table'] ::: {each_join_detail}")                       
                        if "table" in each_join_detail:
                            logger.log(f"Inside2")
                            update_tag = f'''<updatewhere>0</updatewhere>
                                             <updatekeyinplace>no</updatekeyinplace>
                                             <update>{each_join_detail['table'].lower()}</update>'''
                            
                            update_tag_list.append(update_tag)
        else:
            update_tag = f'''<updatewhere>0</updatewhere>
                             <updatekeyinplace>no</updatekeyinplace>
                             <update>{column_detail['table_name'].lower()}</update>'''
    
            update_tag_list.append(update_tag)
            
        logger.log(f"column_detail in get_join_object in edit::: {update_tag_list}")
        return update_tag_list
            
    def build_xml_str(self, object_name):

        x                     = 10
        y                     = 10
        tabsequence           = 10
        previous_group_name   = ""
        current_group_name    = ""
        final_XML             = ""
        
        header_primary_key_lst    = []
        for sqlmodels_list in self.jsonData["transaction"]["sql_models"]:
            tableColumn_list      = []
            textObject_list       = []
            columnObject_list     = []
            groupObject_list      = []
            retreival_query_list  = []
            argument_list         = []

            data = sqlmodels_list['sql_model']['columns']
            grouped_data = {k: list(v) for k, v in defaultdict(list, {
                item["column"].get("group_name", ""): [] for item in data
            }).items()}
            for item in data:
                grouped_data[item["column"].get("group_name", "")].append(item)
            sorted_data = sum((sorted(group, key=lambda item: int(item["column"]["x"])) for group in grouped_data.values()), [])
            sqlmodels_list['sql_model']['columns'] = sorted_data

            for index, column_detail in enumerate(sqlmodels_list['sql_model']['columns']) :# [0]['column']):
                tableColumn     = self.get_Table_Column(column_detail['column'], sqlmodels_list['sql_model']['joins'] if "joins" in sqlmodels_list['sql_model'] else [])
                tableColumn_list.append(tableColumn)
                if 'x' in column_detail['column'] and column_detail['column']['x'] != '':
                    x = int(column_detail['column']['x'])
                else:
                    x+=10

                if 'y' in column_detail['column'] and column_detail['column']['y'] != '':
                    y = int(column_detail['column']['y'])

                logger.log(f"value of x ::: {x}")
                logger.log(f"value of y ::: {y}")
                
                textObject      = self.get_Text_Object(column_detail['column'], x, y)
                textObject_list.append(textObject)
                x+=10

                columnObject, tabsequence      = self.get_Column_Object(column_detail['column'], x, y, tabsequence)
                columnObject_list.append(columnObject)

                update_tag_list       = self.get_join_object(sqlmodels_list['sql_model'], column_detail['column'])

            logger.log(f"Type of form ::: {type(sqlmodels_list['sql_model']['form_no'])}")
            if (sqlmodels_list['sql_model']['form_no'] == '1' or sqlmodels_list['sql_model']['form_no'] == 1):
                logger.log(f"Inside form no 1")
                header_primary_key_lst = self.get_header_primary_key_list(sqlmodels_list['sql_model']['columns'],sqlmodels_list['sql_model']['joins'] if "joins" in sqlmodels_list['sql_model'] else [])
                logger.log(f"header_primary_key_lst ::: {header_primary_key_lst}")
            else:
                logger.log(f"Inside other than form no 1")
                logger.log(f"header_primary_key_lst ::: {header_primary_key_lst}")
                argument_list = self.get_argument_list(sqlmodels_list['sql_model']['columns'],sqlmodels_list['sql_model']['joins'] if "joins" in sqlmodels_list['sql_model'] else [],header_primary_key_lst)
            retreival_query       = self.retrival_query(sqlmodels_list['sql_model'], sqlmodels_list['sql_model']['columns'], argument_list,) 
            
            final_XML       = ( self.header + "\n" 
                                    + "<TableDefinition>"             + "\n"
                                    + "\n".join(tableColumn_list)     + "\n" 
                                    + "<retrieve>" + retreival_query  + "</retrieve> \n"
                                    + "\n".join(update_tag_list)      
                                    + "\n".join(argument_list)        + "\n"
                                    + "</TableDefinition>"  
                                    + "\n".join(textObject_list)      + "\n" 
                                    + "\n".join(columnObject_list)    + "\n" 
                                    # + "\n".join(groupObject_list)     + "\n" 
                                    + self.footer ) 
            
            fileName     = f"{object_name}1{sqlmodels_list['sql_model']['form_no']}.xml"
            finalMessage = self.create_XML_file(fileName, final_XML)
        return finalMessage 
    
    def create_XML_file(self, fileName, final_XML_str):
        filePath = "/wildfly/server/default/deploy/ibase.ear/metadata/"
        with open(filePath + fileName, "w") as file:
            file.write(final_XML_str)
            return f" New '{fileName}' file written and saved successfully."

