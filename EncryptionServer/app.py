import uvicorn
from methods import *

from fastapi import FastAPI, Response, status, Depends, Query, File, UploadFile
from typing import Optional, List
from starlette.responses import FileResponse

import db_models
from db_connect import engine, SessionLocal
from sqlalchemy.orm import Session
from db_models import Files
from encryptmode import LUCKey
from PrimeNumber import PrimeType as mode

# DB
db_models.Base.metadata.create_all(engine)

keys = LUCKey(256, mode.MillerRabin, 0.9999999)


def get_db():
    with SessionLocal() as db:
        return db


# END DB


app = FastAPI()


@app.get("/filenames/{user_id}", status_code=status.HTTP_200_OK)  # , response_model=List[str]
async def get_file_names(user_id: str, db: Session = Depends(get_db)):
    res = db.query(Files).filter(Files.user_id == user_id).all()
    print(res)
    return res


@app.get("/key_asymmetric/{username}", status_code=status.HTTP_200_OK)
def get_asymmetric_key(
        response: Response,
        username: str,
        db: Session = Depends(get_db)
):
    return keys.get_open_key()


@app.post("/key/{username}", status_code=status.HTTP_200_OK)
async def get_keys(
        response: Response,
        username: str,
        key: Optional[str] = None,
        c_0: Optional[str] = None,
        db: Session = Depends(get_db)
):
    user = get_user_from_db(db, username)
    if user:
        # key_encrypt = ''
        # for ent in key:
        # key_encrypt += chr(LUC.encrypt_num(ord(ent), keys.get_decrypting_exponent(), keys.get_open_key()[1]))
        user_update_keys(db, key=key, user_name=username, c_0=c_0)
    else:
        response.status_code = status.HTTP_404_NOT_FOUND


@app.post("/login/{username}", status_code=status.HTTP_200_OK)
async def login_user(
        response: Response,
        username: str,
        password: Optional[str] = None,
        db: Session = Depends(get_db)):
    user = get_user_from_db(db, username)
    if user:
        if user.password == password:
            response.status_code = status.HTTP_200_OK
            return get_user_id_from_db(db, username)
        else:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {'msg': 'Wrong password'}
    else:
        response.status_code = status.HTTP_201_CREATED
        return add_user_to_db(
            db,
            login=username,
            password=password,
        )


@app.post("/file/upload/{user_id}", status_code=status.HTTP_200_OK)
async def upload_file(
        response: Response,
        user_id: Optional[str] = None,
        cypher_type: Optional[str] = None,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    key = get_key(db, user_id)[0]
    c_0 = get_c_0(db, user_id)[0]
    # Format new filename
    full_name = format_filename(file)

    # Save file
    await save_file_to_uploads(file, full_name, user_id)

    with open(f'{UPLOADED_FILES_PATH}{user_id}/{full_name}', 'rb') as f:
        open_text = f.read()
    print(key)

    enc = get_encoder(cypher_type, key, c_0)
    decoded = enc.decode(open_text)
    os.remove(f'{UPLOADED_FILES_PATH}{user_id}/{full_name}')
    with open(f'{UPLOADED_FILES_PATH}{user_id}/{full_name}', 'wb') as f:
        f.write(decoded)

    # Get file size
    file_size = get_file_size(full_name, user_id)

    # Get info from DB
    file_info_from_db = get_file_from_db(db, full_name, user_id)

    # Add to DB
    if not file_info_from_db:
        response.status_code = status.HTTP_201_CREATED
        return add_file_to_db(
            db,
            full_name=full_name,
            file_size=file_size,
            user_id=user_id,
            # file=file
        )

    # Update in DB
    # if file_info_from_db:
    #     # Delete file from uploads
    #     delete_file_from_uploads(file_info_from_db.name)
    #
    #     response.status_code = status.HTTP_201_CREATED
    #     return update_file_in_db(
    #         db,
    #         file_id=file_id,
    #         full_name=full_name,
    #         tag=tag,
    #         file_size=file_size,
    #         file=file
    #     )


@app.get("/file/download/{user_id}", status_code=status.HTTP_200_OK)
async def download_file(
        response: Response,
        file_name: str,
        user_id: str,
        db: Session = Depends(get_db)
):
    file_info_from_db = get_file_from_db(db, file_name, user_id)

    if file_info_from_db:
        if os.path.exists(f"{UPLOADED_FILES_PATH}{file_info_from_db.user_id}/{file_info_from_db.name}"):
            file_resp = FileResponse(f"{UPLOADED_FILES_PATH}{file_info_from_db.user_id}/{file_info_from_db.name}")
            response.status_code = status.HTTP_200_OK
            return file_resp
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'msg': 'File not found'}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'msg': 'File not found'}


@app.delete("/api/delete", tags=["Delete"])
async def delete_file(
        response: Response,
        file_id: int,
        db: Session = Depends(get_db)
):
    file_info_from_db = get_file_from_db(db, file_id)

    if file_info_from_db:
        # Delete file from DB
        delete_file_from_db(db, file_info_from_db)

        # Delete file from uploads
        delete_file_from_uploads(file_info_from_db.name)

        response.status_code = status.HTTP_200_OK
        return {'msg': f'File {file_info_from_db.name} successfully deleted'}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'msg': f'File does not exist'}


@app.get("/api/get", tags=["Get files"], status_code=status.HTTP_200_OK)
async def root(
        # *,
        response: Response,
        id: Optional[List[int]] = Query(None),
        name: Optional[List[str]] = Query(None),
        tag: Optional[List[str]] = Query(None),
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        db: Session = Depends(get_db)
):
    # All records by default
    query = db.query(db_models.Files).all()
    files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    if id and not name and not tag:
        query = db.query(db_models.Files).filter(db_models.Files.file_id.in_(id)).all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and name and not tag:
        query = db.query(db_models.Files).filter(db_models.Files.file_id.in_(id)) \
            .filter(db_models.Files.name.in_(name)) \
            .all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and name and tag:
        query = db.query(db_models.Files).filter(db_models.Files.file_id.in_(id)) \
            .filter(db_models.Files.name.in_(name)) \
            .filter(db_models.Files.tag.in_(tag)) \
            .all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and not name and tag:
        query = db.query(db_models.Files).filter(db_models.Files.file_id.in_(id)) \
            .filter(db_models.Files.tag.in_(tag)) \
            .all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and name and tag:
        query = db.query(db_models.Files).filter(db_models.Files.name.in_(name)) \
            .filter(db_models.Files.tag.in_(tag)) \
            .all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and not name and tag:
        query = db.query(db_models.Files).filter(db_models.Files.tag.in_(tag)).all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and name and not tag:
        query = db.query(db_models.Files).filter(db_models.Files.name.in_(name)).all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    if len(files_in_db) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': 'No results =('}

    response.status_code = status.HTTP_200_OK
    return files_in_db


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", reload=True)
