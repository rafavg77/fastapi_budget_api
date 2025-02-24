from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....crud import crud_usuario
from ....schemas.usuario import Usuario, UsuarioCreate
from ....api import deps

router = APIRouter()

@router.post("/", response_model=Usuario)
def create_usuario(
    *,
    db: Session = Depends(deps.get_db),
    usuario_in: UsuarioCreate,
) -> any:
    usuario = crud_usuario.get_by_cuenta(db, usuario_cuenta=usuario_in.usuario_cuenta)
    if usuario:
        raise HTTPException(
            status_code=400,
            detail="Este usuario ya existe en el sistema.",
        )
    return crud_usuario.create(db=db, obj_in=usuario_in)

@router.get("/", response_model=List[Usuario])
def read_usuarios(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> any:
    usuarios = crud_usuario.get_multi(db, skip=skip, limit=limit)
    return usuarios

@router.get("/{usuario_cuenta}", response_model=Usuario)
def read_usuario(
    *,
    db: Session = Depends(deps.get_db),
    usuario_cuenta: str,
) -> any:
    usuario = crud_usuario.get_by_cuenta(db, usuario_cuenta=usuario_cuenta)
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado",
        )
    return usuario