from mcp.server.fastmcp import FastMCP
from api_client import APIClient

mcp = FastMCP("event-ticketing")

@mcp.tool()
def get_event_availability(event_id: str, token: str) -> dict:
    """Cek ketersediaan tiket untuk sebuah event.
    Gunakan tool ini sebelum membuat order untuk memastikan stok tersedia.
    Kembalikan daftar kategori tiket beserta sisa kuota dan harga.

    Args:
        event_id (str): UUID dari event yang ingin dicek ketersediaan tiketnya
        token (str): JWT token dari user yang sedang login

    Returns:
        dict: event_id dan daftar kategori tiket beserta sisa kuota dan harga
    """
    client = APIClient(token)
    # panggil method yang sesuai di api_client
    data = client.get_tiket_kategori(event_id)
    
    return {
        "event_id": event_id,
        "kategori": data
    }

@mcp.tool()
def create_order(items: list, token: str) -> dict:
    """Tool untuk membuat order baru.
    PENTING: Gunakan tool ini HANYA setelah user secara eksplisit mengkonfirmasi 
    detail order (kategori tiket, jumlah, dan total harga).
    Sebelum membuat order cek terlebih dulu event yang tersedia.

    Args:
        items (list): items yang akan dikirim untuk membuat order baru
        token (str): JWT token dari user yang sedang login

    Returns:
        dict: detail order yang berhasil dibuat termasuk kode order dan total harga
    """
    
    client = APIClient(token)
    
    data = client.create_order(items)
    
    return {
        "order": data
    }

@mcp.tool()
def check_order_status(order_id: str, token: str) -> dict:
    """Tool untuk mengecek status dari order menggunakan order_id.

    Args:
        order_id (str): UUID dari order yang ingin dicek statusnya
        token (str): JWT token dari user yang sedang login

    Returns:
        dict: detail order beserta status terkini dalam bahasa Indonesia
    """
    
    client = APIClient(token)
    
    data = client.get_order(order_id)
    
    return {
        "order_status": data
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")