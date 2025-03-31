import code
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, Header, Request
from fastapi.responses import RedirectResponse


""" from authx import AuthX, AuthXConfig, TokenPayload """

from queries.orm import AsyncORM
from schemas import UserLoginSсhema

from config import settings
import requests
import webbrowser
import json




router = APIRouter()

""" config_user = AuthXConfig()
config_user.JWT_SECRET_KEY = settings.SECURITY_USER_JWT_secret_key
config_user.JWT_ACCESS_COOKIE_NAME = settings.SECURITY_USER_JWT_ACCESS_COOKIE_NAME
config_user.JWT_TOKEN_LOCATION = settings.SECURITY_USER_JWT_token_location
config_user.JWT_DECODE_AUDIENCE = settings.SECURITY_USER_JWT_decode_audience
config_user.JWT_COOKIE_CSRF_PROTECT = False

config_admin = AuthXConfig()
config_admin.JWT_SECRET_KEY = settings.SECURITY_ADMIN_JWT_secret_key
config_admin.JWT_ACCESS_COOKIE_NAME = settings.SECURITY_ADMIN_JWT_ACCESS_COOKIE_NAME
config_admin.JWT_TOKEN_LOCATION = settings.SECURITY_ADMIN_JWT_token_location
config_admin.JWT_DECODE_AUDIENCE = settings.SECURITY_ADMIN_JWT_decode_audience
config_admin.JWT_COOKIE_CSRF_PROTECT = False # РАЗОБРАТЬСЯ ИСПРАВИТЬ !!!



security_user = AuthX(config=config_user)
security_admin = AuthX(config=config_admin) """



@router.post("/register/yandexID", tags=["Регистрация пользователей"])
async def redirect_yandex():
    webbrowser.open("https://oauth.yandex.ru/authorize?response_type=code&client_id=6005752b79124f0eb0b4d390eb3a07f2")
    
@router.get("/register/yandexID/{code}", tags=["Регистрация пользователей"])
async def register_user(code: str):
    tok = requests.post('https://oauth.yandex.ru/token', data={'grant_type': 'authorization_code', 'code': code, 'client_id':'6005752b79124f0eb0b4d390eb3a07f2', 'client_secret': '06f4984d2dbb4f99a56a5e51a28d4cf1'})
    dat = json.loads(tok.text)
    res = requests.post("https://login.yandex.ru/info", data={'oauth_token': dat['access_token'], 'format': 'json'})
    data = json.loads(res.text)
    existing_user = await AsyncORM.select_users_registration(data['default_email'])
    if existing_user:
        raise HTTPException(status_code=400, detail=f"Пользователь авторизован")
    await AsyncORM.insert_users(data['real_name'], data['default_email']) # добавляем в базу пользователя и хешируем пароль
    return {"msg": "Пользователь успешно зарегистрирован"} 


""" @router.post("/register/users", tags=["Регистрация пользователей"])
async def register_user(creds: Annotated[UserLoginSсhema, Depends()]):
    existing_user = await AsyncORM.select_users_registration(creds.email, creds.password)
    if existing_user:
        raise HTTPException(status_code=400, detail=f"Пользователь уже существует")
    await AsyncORM.insert_users(creds.username, creds.email, creds.password) # добавляем в базу пользователя и хешируем пароль
    return {"msg": "Пользователь успешно зарегистрирован"} """


""" @router.post("/autorization/", tags=["Авторизация"])
async def autorization_user():
    url = "https://oauth.yandex.ru/authorize"
    params = {
   "response_type": "code",
   "client_id": "6005752b79124f0eb0b4d390eb3a07f2",
}
    response = requests.post(url, params=params)
    print(response.url)
    return {"msg": "Пользователь успешно авторизован"} """



""" @router.post("/login", tags=["Авторизация"])
async def login(creds: Annotated[UserAuthSсhema, Depends()], 
                response: Response):
    user = await AsyncORM.select_users_auth(creds.email, creds.password)
    verify = verify_password(creds.password, user[1])
    admin = verify_password(creds.password, get_password_hash(settings.ADMIN_psw))
    if admin:
        token = security_admin.create_access_token(creds.email, audience='Admin')
        response.set_cookie(config_admin.JWT_ACCESS_COOKIE_NAME, token)
        return {"access_token": token}
    elif verify:
        token = security_user.create_access_token(creds.email, audience='User')
        response.set_cookie(config_user.JWT_ACCESS_COOKIE_NAME, token)
        return {"access_token": token}
    else: 
        raise HTTPException(status_code=401, detail="Не верный пароль")
    

@router.put("/protected_user/", tags=["ручка пользователей"],  dependencies=[Depends(security_user.access_token_required)])
async def protected(username: Annotated[
             str,
             Header(),
        ], payload: TokenPayload = Depends(security_user.access_token_required)):
        await AsyncORM.update_user(payload.sub, username)
        return {"Имя изменено на": username} """


""" @router.get("/select_user", tags=["Cписок читателей"])
async def select_users():
    return await AsyncORM.select_users() 


@router.get("/select_user/protected_admin", tags=["Список читателей, для админов, "], dependencies=[Depends(security_admin.access_token_required)])
async def select_users():
    return await AsyncORM.select_users()      




####################CRUD для книг####################
@router.post("/protected_admin/book/", tags=["CRUD для книг"], dependencies=[Depends(security_admin.access_token_required)])
async def create_books(task: Annotated[BooksSсhema, Depends()]):
   await AsyncORM.create_books(task.bookname, task.authors, task.description, task.Genre, task.quantity)
   return {
    'msg': "Книга успешно добавлена",
    'Имя': task.bookname, 
    'Автор':   task.authors, 
    'Описание':   task.description, 
    'Жанр':   task.Genre, 
    'Количество':   task.quantity
   }


@router.get("/protected_admin/book/", tags=["CRUD для книг"], dependencies=[Depends(security_admin.access_token_required)])
async def read_books(books_filter: Annotated[BooksFilterSсhema, Depends()], response: Response):
    res = await AsyncORM.select_books(books_filter)
    response.headers['Access-Control-Allow-Origin'] = '*'
    if res == []:
        return {
    'msg': "Книга не найдена",
    'Имя': books_filter.booknames, 
    'Автор':   books_filter.authors,
    'Жанр':   books_filter.genres, 
   }
    else:
        return res
    


@router.put("/protected_admin/book/", tags=["CRUD для книг"], dependencies=[Depends(security_admin.access_token_required)])
async def update_books(updates: Annotated[BooksUpdateSсhema, Depends()]):
    return await AsyncORM.update_book(updates)


@router.delete("/protected_admin/book/", tags=["CRUD для книг"], dependencies=[Depends(security_admin.access_token_required)])
async def delete_books(delete: Annotated[BooksDeleteSсhema, Depends()]):
    return await AsyncORM.delete_book(delete)


####################CRUD для авторов####################
@router.post("/protected_admin/author/", tags=["CRUD для авторов"], dependencies=[Depends(security_admin.access_token_required)])
async def create_author(task_author: Annotated[AuthorSсhema, Depends()]):
   await AsyncORM.create_authors(task_author.authorname, task_author.biography, task_author.born)
   return {
    'msg': "Автор успешно добавлен",
    'Имя': task_author.authorname, 
    'Биография':   task_author.biography, 
    'Дата рождения':   task_author.born,
   }


@router.get("/protected_admin/author/", tags=["CRUD для авторов"], dependencies=[Depends(security_admin.access_token_required)])
async def read_author(author_filter: Annotated[AuthorFilterSсhema, Depends()]):
    res = await AsyncORM.select_author(author_filter.authorname)
    if res == []:
        return {
    'msg': "Автор не найден",
    'Имя': author_filter.authorname,  
   }
    else:
        return res
    

 
@router.put("/protected_admin/author/", tags=["CRUD для авторов"], dependencies=[Depends(security_admin.access_token_required)])
async def update_author(updates: Annotated[AuthorUpdateSсhema, Depends()]):
    return await AsyncORM.update_author(updates)


@router.delete("/protected_admin/author/", tags=["CRUD для авторов"], dependencies=[Depends(security_admin.access_token_required)])
async def delete_author(delete_data: Annotated[AuthorDeleteSсhema, Depends()]):
    return await AsyncORM.delete_author(delete_data)
 """

    