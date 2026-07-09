from pydantic import BaseModel, Field
from uuid import UUID


# ── Tool Inputs ──────────────────────────────────────────────

class GetEventAvailabilityInput(BaseModel):
    event_id: UUID = Field(..., description="UUID dari event yang ingin dicek ketersediaan tiketnya")


class OrderItemInput(BaseModel):
    tiket_kategori_id: UUID = Field(..., description="UUID dari kategori tiket")
    jumlah: int = Field(..., ge=1, description="Jumlah tiket yang ingin dipesan (minimal 1)")


class CreateOrderInput(BaseModel):
    items: list[OrderItemInput] = Field(..., min_length=1, description="Daftar tiket yang ingin dipesan")


class CheckOrderStatusInput(BaseModel):
    order_id: UUID = Field(..., description="UUID dari order yang ingin dicek statusnya")


# ── Tool Outputs ─────────────────────────────────────────────

class TiketKategoriResult(BaseModel):
    tiket_kategori_id: UUID
    nama: str
    harga: float
    sisa_kuota: int


class EventAvailabilityResult(BaseModel):
    event_id: UUID
    kategori: list[TiketKategoriResult]


class OrderItemResult(BaseModel):
    tiket_kategori_id: UUID
    jumlah: int
    harga_satuan: float


class OrderResult(BaseModel):
    order_id: UUID
    kode_order: str
    total_harga: float
    status: str
    items: list[OrderItemResult]