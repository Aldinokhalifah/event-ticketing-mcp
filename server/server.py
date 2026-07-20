from mcp.server.fastmcp import FastMCP
from api_client import APIClient

mcp = FastMCP("event-ticketing-mcp")


@mcp.tool()
def search_event(nama: str, token: str) -> dict:
    """Cari event berdasarkan nama event.
    Gunakan tool ini PERTAMA ketika user menyebut nama event.
    Hasil pencarian berisi event_id yang dibutuhkan tool lain.

    Args:
        nama (str): Nama dari event yang dicari

    Returns:
        dict: detail event
    """

    client = APIClient(token)
    # panggil method yang sesuai di api_client
    data = client.search_events(nama)
    
    return {
        "keyword": nama,
        "detail_event": data
    }

@mcp.tool()
def get_event_availability(event_id: str, token: str) -> dict:
    """Ambil detail informasi sebuah event berdasarkan event_id.
    Gunakan tool ini jika user ingin tahu informasi event seperti nama, 
    lokasi, tanggal, dan status event.

    Args:
        event_id (str): UUID dari event yang ingin dicek ketersediaan tiketnya

    Returns:
        dict: event_id dan detail event
    """
    client = APIClient(token)
    # panggil method yang sesuai di api_client
    data = client.get_event_by_id(event_id)
    
    return {
        "event_id": event_id,
        "detail_event": data
    }

@mcp.tool()
def get_ticket_category_event(event_id: str, token: str) -> dict:
    """Cek katergori tiket apa yang tersedia untuk sebuah event berdasarkan id event.
    Gunakan tool ini jika user ingin melihat kategori tiket dari sebuah event.

    Args:
        event_id (str): UUID dari event yang ingin dicek ketersediaan tiketnya

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
    detail order yang ada di items (kategori tiket id dan jumlah).
    Sebelum membuat order cek terlebih dulu event yang tersedia.

    Args:
        items (list): items yang akan dikirim untuk membuat order baru

    Returns:
        dict: detail order yang berhasil dibuat termasuk kode order dan total harga
    """
    
    client = APIClient(token)
    try:
        data = client.create_order(items)
        return {"order": data}
    except Exception as e:
        raise

@mcp.tool()
def check_order_status(order_id: str, token: str) -> dict:
    """Tool untuk mengecek status dari order menggunakan order_id.

    Args:
        order_id (str): UUID dari order yang ingin dicek statusnya

    Returns:
        dict: detail order beserta status terkini dalam bahasa Indonesia
    """
    
    client = APIClient(token)
    
    data = client.get_order(order_id)
    
    return {
        "order_status": data
    }

@mcp.tool()
def get_my_orders(token: str) -> dict:
    """Ambil semua order milik user yang sedang login.
    Gunakan tool ini ketika user ingin melihat daftar order
    atau ingin mengecek status order tanpa tahu order_id-nya.
    Dari hasil tool ini, ambil id untuk digunakan di check_order_status.

    Returns:
        dict: detail order beserta status terkini dalam bahasa Indonesia
    """

    client = APIClient(token)
    
    data = client.get_my_orders()
    
    return {
        "orders": data
    }

@mcp.tool()
def get_events_list(token: str) -> dict:
    """Mengambil semua event yang tersedia.
    Gunakan tool ini ketika user ingin melihat semua daftar event yang tersedia.
    Gunakan tool ini jika hasil pencarian menggunakan tool search_event tidak ditemukan.

    Returns:
        dict: list events
    """

    client = APIClient(token)
    
    data = client.list_events()
    
    return {
        "list_events": data
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")