# ORM-DATABASE-sqlite

## write example code 


```python
from orm_database_sqlite import Sqlite
import asyncio
from pydantic import BaseModel

class users(BaseModel):
    users_rt: str
    password_rt : str
    email: str


sqlite =  Sqlite("example.db")



async def main():
    data = {"users_rt":"test1","password_rt":"1234","email":"test1@mail.com"}
    data1 = [{"users_rt":"test1","password_rt":"1234","email":"test1@mail.com"},
            {"users_rt":"test2","password_rt":"1234","email":"test2@mail.com"},
            {"users_rt":"test3","password_rt":"1234","email":"test3@mail.com"}]
    await sqlite.start()
    #await sqlite.teble_create_BaseModel("users",users)
    #await sqlite.insert("users",data1)
    #result = await  sqlite.select("users",["users_rt","email"])
    #print(result)
    #await sqlite.delete("users",{"users_rt":"test2"})
    await sqlite.update("users",{"users_rt":"test1"},{"users_rt":"test2"})
asyncio.run(main())

```
