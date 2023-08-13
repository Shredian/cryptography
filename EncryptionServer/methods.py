import os
from datetime import datetime

import db_models
from settings import *
from encryptmode import ECB, OFB, CBC, CFB, EncryptMode


# Get file info from DB
def get_file_from_db(db, file_name, user_id):
    return db.query(db_models.Files) \
        .filter(db_models.Files.name == file_name
                and db_models.Files.user_id == user_id).first()


def get_user_from_db(db, user_name):
    return db.query(db_models.User).filter(db_models.User.login == user_name).first()


def get_user_id_from_db(db, user_name):
    ans = db.query(db_models.User).filter(db_models.User.login == user_name).one()
    return ans.id


def get_encoder(cypher_type, key, c_0: str = None):

    if cypher_type == 'ECB':
        return ECB(key.encode())
    elif cypher_type == 'RDH':
        return CBC(key.encode(), c_0.encode())
    elif cypher_type == 'RD':
        return CBC(key.encode(), c_0.encode())
    elif cypher_type == 'CBC':
        return CBC(key.encode(), c_0.encode())
    elif cypher_type == 'CTR':
        return CBC(key.encode(), c_0.encode())
    elif cypher_type == 'OFB':
        return OFB(key.encode(), c_0.encode())
    elif cypher_type == 'CFB':
        return CFB(key.encode(), c_0.encode())


def user_update_keys(db, key, c_0, user_name):
    db.query(db_models.User). \
        filter(db_models.User.login == user_name). \
        update({db_models.User.key: key, db_models.User.c_0: c_0})
    db.commit()


def get_key(db, user_id):
    return db.query(db_models.User.key).filter(db_models.User.id == user_id).first()


def get_c_0(db, user_id):
    return db.query(db_models.User.c_0).filter(db_models.User.id == user_id).first()


def add_user_to_db(db, **kwargs):
    new_user = db_models.User(
        login=kwargs['login'],
        password=kwargs['password'],
        key=kwargs['key'],
        c_0=kwargs['c_0']
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return db.query(db_models.User.id).filter(db_models.User.login == kwargs['login']).one().id


# Offset\limit
def get_files_from_db_limit_offset(db, query, limit: int = None, offset: int = None):
    if limit and not offset:
        query = query[:limit]
    elif limit and offset:
        limit += offset
        query = query[offset:limit]
    elif not limit and offset:
        query = query[offset:]
    return query


# Delete file from uploads folder
def delete_file_from_uploads(file_name):
    try:
        os.remove(UPLOADED_FILES_PATH + file_name)
    except Exception as e:
        print(e)


# Save file to uploads folder
async def save_file_to_uploads(file, filename, user_id):
    if not os.path.exists(f'{UPLOADED_FILES_PATH}{user_id}'):
        os.makedirs(f'{UPLOADED_FILES_PATH}{user_id}')
    with open(f'{UPLOADED_FILES_PATH}{user_id}/{filename}', "wb") as uploaded_file:
        file_content = await file.read()
        uploaded_file.write(file_content)
        uploaded_file.close()


# Format filename
def format_filename(file):
    # Split filename and extention
    filename, ext = os.path.splitext(file.filename)

    return filename + ext


# Get file size
def get_file_size(filename, user_id):
    file_path = f'{UPLOADED_FILES_PATH}{user_id}/{filename}'
    return os.path.getsize(file_path)


# Add File to DB
def add_file_to_db(db, **kwargs):
    new_file = db_models.Files(
        name=kwargs['full_name'],
        size=kwargs['file_size'],
        user_id=kwargs['user_id']
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file


# Update File in DB
# def update_file_in_db(db, **kwargs):
#     update_file = db.query(db_models.Files).filter(db_models.Files.file_id == kwargs['file_id']).first()
#     update_file.name = kwargs['full_name']
#     update_file.tag = kwargs['tag']
#     update_file.size = kwargs['file_size']
#     update_file.mime_type = kwargs['file'].content_type
#     update_file.modification_time = datetime.now()
#
#     db.commit()
#     db.refresh(update_file)
#     return update_file


# Delete file from DB
def delete_file_from_db(db, file_info_from_db):
    db.delete(file_info_from_db)
    db.commit()
