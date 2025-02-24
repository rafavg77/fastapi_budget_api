from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....crud import crud_cuenta
from ....schemas.cuenta import Cuenta, CuentaCreate
from ....api import deps

router = APIRouter()

@router.post("/", response_model=Cuenta)
def create_cuenta(
    *,
    db: Session = Depends(deps.get_db),
    cuenta_in: CuentaCreate,
) -> Any:
    return crud_cuenta.create(db=db, obj_in=cuenta_in)

@router.get("/usuario/{usuario_cuenta}", response_model=List[Cuenta])
def read_cuentas_by_usuario(
    *,
    db: Session = Depends(deps.get_db),
    usuario_cuenta: str,
) -> Any:
    cuentas = crud_cuenta.get_by_usuario(db, usuario_cuenta=usuario_cuenta)
    return cuentas