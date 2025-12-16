from orm_database_postgres.orm_query import QueryBuilder
import asyncpg
import sys
import datetime

class PostgreSQL:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.ObjectQueryBuilder = QueryBuilder()
    async def start(self):
        try:
            self.db = await asyncpg.connect(host=self.host, user=self.user, password=self.password, database=self.database)
        except:
            print("Error connecting postgres")
            sys.exit(1)


    async def teble_create_BaseModel(self,table:str , class_BaseModel):
        query = self.ObjectQueryBuilder.query_baseModel_create_table(table,class_BaseModel)
        try:
            await self.db.execute(query)
            return True
        except: 
            return False

    async def teble_create(self, table: str, field: dict):
        query = self.ObjectQueryBuilder.query_create_table(table,field)
        await self.db.execute(query)



    async def insert(self,table:str,value):
        
        query_table = self.ObjectQueryBuilder.Query_insert_table(table)
        query_key = self.ObjectQueryBuilder.Query_key(value)
        query_value = self.ObjectQueryBuilder.Query_insert_value(value)
        query = f"{query_table} {query_key} {query_value}"
        if isinstance(value,dict):
            data = ()

            for value_item in value.items():
                
                data +=  ( value_item[1],)
            await self.db.executemany(query,[data])
        elif isinstance(value,list):
            data_list = []
            for single_value in value:
                data  = ()
                for value_item in single_value.items():
                    data +=  ( value_item[1],)

                data_list.append(data)
            await self.db.executemany(query,data_list)



    async def select(self,table:str,
                     filed:list =[],
                     filter:dict={},
                      order:dict={},
                     limit:int=None,
                     like:bool=False,
                     filter_and:bool=True):


        query_feild = self.ObjectQueryBuilder.Query_feild(filed)
        query_table = self.ObjectQueryBuilder.Query_table(table,filed)
        query_filter = self.ObjectQueryBuilder.Query_filter(filter,like,filter_and)
        query_order = self.ObjectQueryBuilder.Query_order(order)
        query_limit = self.ObjectQueryBuilder.Query_limit(limit)
        
        query = f"{query_feild} {query_table} {query_filter} {query_order} {query_limit}"
        #await self.db.prepare(query)
        result = await  self.db.fetch(query)
        data = []
        data_row = []
        try:
            for a in result:
                for b in a:
                    data.append(b)
                data_row.append(data)
                data = []
        except :
            for a in result[0]:
                data_row.append(a)
        return data_row        
         

    
    async def delete(self,table:str,filter,like:bool=False,filter_and:bool=True):
        query_table = self.ObjectQueryBuilder.Query_delete(table)
        query_filter = self.ObjectQueryBuilder.Query_filter(filter,like=like,filter_and=filter_and)
        query = f"{query_table} {query_filter}"
        await self.db.execute(query)
    

    async def update(self,table:str,filter:dict,value:dict):
        query_table = self.ObjectQueryBuilder.Query_table_update(table)
        query_value = self.ObjectQueryBuilder.Query_value(value)
        query_filter = self.ObjectQueryBuilder.Query_filter(filter,False,False)
        query = f"{query_table} {query_value} {query_filter} "
        await self.db.execute(query)




    
