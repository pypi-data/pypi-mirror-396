import datetime





class QueryBuilder:
    def __init__(self):
        pass


    def query_baseModel_create_table(self,table,class_BaseModel):
        query = f"CREATE TABLE {table} ("
        result=class_BaseModel.model_json_schema()
        list_keys = result['properties']
        list_keys = list(list_keys.keys())
        type=""
        for a in list_keys:
            data = result['properties'][a]
            if len(data.keys()) == 2:
                match data["type"]:
                    case "string":
                        type = "varchar"
                    case "number":
                        type = "float"
                    case "integer":
                        type = "int" 
                    case "boolean":
                        type = "bool"
                query = query + a + " " + type + ","
            else :
                try:
                    type = data["type"] + " " + data["default"]
                    query = query + a + " " + type + "," 
                except:    
                    match data["type"]:
                        case "string":
                            type = f"varchar({data['varchar']})"
                        case "number":
                            type = "float"
                        case "integer":
                            type = "int" 
                        case "boolean":
                            type = "bool"
                    
                    query = query + a + " " + type + "," 
        query = query[:-1]
        query = query + "  )"
        return query


    def query_create_table(self,table:str,field:dict):
        query = f"CREATE TABLE {table} ("
        filed_key = list(field.keys())
        for a in filed_key:
            query = query + a + " " + field[a] + " ,"
        query = query[:-1]
        query = query + " )"
        return query


    def Query_insert_table(self,table:str):
        return f"INSERT INTO {table}"

    
    def Query_key(self,value):
        query = "("
        if isinstance(value,list):
            for value_item in value:
                return self.list_keys_dict_to_str(query=query,value=value_item)

            
        elif isinstance(value,dict):
            return self.list_keys_dict_to_str(query=query,value=value)

   




    def Query_insert_value(self,value):
        query = "VALUES ("
        if isinstance(value,list):
            for value_item in value:
                return self.list_keys_dict_to_str(query=query,value=value_item,key="?")
        elif isinstance(value,dict):
                return self.list_keys_dict_to_str(query=query,value=value,key="?")

        






        

    def Query_feild(self,feild:list=[]):
        if feild == []:
            query = f"SELECT *  "
            return query
        else:
            query = f"SELECT "
            for field_item in feild:
                query = query + field_item + ","
            query = query[:-1]
            return query
    

    def Query_table(self,table:str):
        return f"FROM {table}"
    

    def Query_filter(self,filter:dict,like:bool=None,filter_and:bool=None):
        if filter == {}:
            return " "
        else:
            query = " WHERE "
            for key in filter.keys():
                if like == True:
                    if filter_and == True:
                        query = query + f"{key} LIKE '%{filter[key]}%' AND "
                    elif filter_and == False:
                        query = query + f"{key} LIKE '%{filter[key]}%' OR "
                elif like == False:
                    if filter_and == True:
                        query = query + f'{key}="{filter[key]}" AND '
                    elif filter_and == False:
                        query = query + f'{key}="{filter[key]}" OR '
            query = query[:-4]
            return query


    def Query_order(self,order:dict):
        if order == {}:
            return ""
        else:
            query = "ORDER BY "
            for order_item in order.keys():
                query = query + f"{order_item} {order[order_item]}"
            return query


    def Query_limit(self,limit:int):
        if limit == None:
            return ""
        else:
            return f"LIMIT {limit}"
        

    def Query_delete(self,table:str):
        query = f"DELETE FROM {table} "
        return query


    def Query_table_update(self,table:str):
        query = f"UPDATE {table} SET "
        return query


    def Query_value(self,value:dict):
        query = ""        
        for value_item in value.keys():
            query = query + f"{value_item}='{value[value_item]}',"
        query = query[:-1]
        return query







    def time_stamp_new(self):
        time = int(datetime.datetime.now().timestamp())
        return time
    


    def list_keys_dict_to_str(self,query:str,value,key=None):
  


        for value_key in value.keys():
            if key != None:
                query = query + f"{key},"
            elif key == None:
                query = query + f"{value_key},"
        return query[:-1]+")"
