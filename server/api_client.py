import httpx
import json
import os
import sys
from dotenv import load_dotenv
from utils.status_order import STATUS_MAP

load_dotenv()

class APIClient:
    def __init__(self, token: str):
        self.base_url = os.getenv("API_BASE_URL")
        self.token = token

    def _get_headers(self) -> dict:
        # kembalikan Authorization header di sini
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_tiket_kategori(self, event_id: str) -> list:
        try:
            response = httpx.get(
                f"{self.base_url}/api/events/{event_id}/tiket-kategori",
                headers=self._get_headers()
            )
        except httpx.RequestError as e:
            raise Exception(f"Tidak bisa terhubung ke server: {str(e)}")
        
        # handle error di sini
        if response.status_code != 200:
            raise Exception(response.json()["message"])

        # proses response dan hitung sisa_kuota
        tiket_kategori = response.json()["data"]
        for kategori in tiket_kategori:
            kategori["sisa_kuota"] = kategori["kuota"] - kategori["terjual"]

        # return list kategori
        return tiket_kategori
    
    def create_order(self, items: list) -> dict:
        if isinstance(items, str):
            items = json.loads(items)
        # merubah snake case menjadi camel case
        converted = [
            {
                "tiketKategoriId": item["tiketKategoriId"],
                "jumlah": item["jumlah"]
            }
            for item in items
        ]

        try:
            response = httpx.post(
                f"{self.base_url}/api/orders",
                headers=self._get_headers(),
                json={"items": converted}
            )
        except httpx.RequestError as e:
            raise Exception(f"Tidak bisa terhubung ke server: {str(e)}")
        
        if response.status_code != 201:
            raise Exception(response.json()["message"])
        
        return response.json()["data"]
    
    def get_order(self, order_id: str) -> dict:
        try:
            response = httpx.get(
                f"{self.base_url}/api/orders/{order_id}",
                headers=self._get_headers()
            )
        except httpx.RequestError as e:
            raise Exception(f"Tidak bisa terhubung ke server: {str(e)}")
        
        # handle error di sini
        if response.status_code != 200:
            raise Exception(response.json()["message"])

        order = response.json()["data"]

        converted_status = STATUS_MAP.get(order["status"], order["status"])
        
        order["status"] = converted_status
        
        return order

    def get_event_by_id(self, event_id: str) -> dict:
        try:
            response = httpx.get(
                f"{self.base_url}/api/events/{event_id}",
                headers=self._get_headers()
            )
        except httpx.RequestError as e:
            raise Exception(f"Tidak bisa terhubung ke server: {str(e)}")
        
        # handle error di sini
        if response.status_code != 200:
            raise Exception(response.json()["message"])

        event_detail = response.json()["data"]
        
        return event_detail