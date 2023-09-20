from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, UploadFile, File, Form, Body 
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/posts", tags=['Posts'])

@router.get("/", response_model=List[schemas.Post])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    # Query posts as before
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # Iterate through posts and add image URLs
    for post in posts:
        image_url = f"/images/{post.image_path}"  # Assuming the image path is relative to "upload_images" directory
        post.image_path = image_url

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(
    title: str = Form(...),
    content: str = Form(...),
    published: bool = Form(True),
    latitude: float = Form(...),
    longitude: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    # Handle image file upload and save it to a directory
    image_file = image.file
    image_path = os.path.join("app/upload_images", image.filename)

    with open(image_path, "wb") as f:
        f.write(image_file.read())

    # Create a new post with location data, title, and content
    new_post = models.Post(
        owner_id=current_user.id,
        latitude=latitude,
        longitude=longitude,
        title=title,
        content=content,
        published=published,
        image_path=image_path
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} does not exist!")

    # Create a full image URL based on your server setup
    image_url = f"/images/{post.image_path}"  # This assumes the image path is relative to the "upload_images" directory

    # Add the image URL to the response
    post.image_path = image_url

    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #deleting post
    # cursor.execute("""Delete from posts where id = %s returning * """, (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exists!!")

    if post.owner_id != current_user.id or current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorised to perform requested action!")

    post_query.delete(synchronize_session = False)
    db.commit()

    # We do not return a message!
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Put method requires all the fields to be sent again
# whereas the patch method requires for only the changed ones
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    # cursor.execute("update posts set title = %s, content = %s, published = %s, owner_id = 11 where id = %s returning *",
    # (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exists!!")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorised to perform requested action!")

    post_query.update(updated_post.dict(), synchronize_session = False)
    db.commit()

    return post_query.first()