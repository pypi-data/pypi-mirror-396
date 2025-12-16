# ORM-DATABASE-postgres

## write example postgres


```python
from orm_database_postgres import PostgreSQL
import asyncio
from pydantic import BaseModel

class users(BaseModel):
    users_rt: str
    password_rt : str
    email: str


postgres = PostgreSQL(host="127.0.0.1",user="postgres",database="wallet",password="12341234")



async def main():
    data = {"users_rt":"test1","password_rt":"1234","email":"test1@mail.com"}
    data1 = [{"users_rt":"test1","password_rt":"1234","email":"test1@mail.com"},
            {"users_rt":"test2","password_rt":"1234","email":"test2@mail.com"},
            {"users_rt":"test3","password_rt":"1234","email":"test3@mail.com"}]
    await postgres.start()
    #await postgres.teble_create_BaseModel("users",users)
    #await postgres.insert("users",data1)
    result = await  postgres.select("users",["users_rt","email"])
    print(result)
    #await postgres.delete("users",{"users_rt":"test2"})
    #await postgres.update("users",{"users_rt":"test1"},{"users_rt":"test2"})

```
