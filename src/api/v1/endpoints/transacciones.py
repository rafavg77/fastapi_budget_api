from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....crud import crud_transaccion
from ....schemas.transaccion import Transaccion, TransaccionCreate
from ....api import deps

router = APIRouter()

@router.post("/", response_model=Transaccion)
def create_transaccion(
    *,
    db: Session = Depends(deps.get_db),
    transaccion_in: TransaccionCreate,
) -> Any:
    return crud_transaccion.create(db=db, obj_in=transaccion_in)

@router.get("/cuenta/{cuenta_transaccion}", response_model=List[Transaccion])
def read_transacciones_by_cuenta(
    *,
    db: Session = Depends(deps.get_db),
    cuenta_transaccion: str,
) -> Any:
    transacciones = crud_transaccion.get_by_cuenta(db, cuenta_transaccion=cuenta_transaccion)
    return transacciones
