"""
Dispatcher Notifikasi & Radar Arbitrase Real-Time.
Mengirimkan notifikasi instan untuk unit motor Hot Deal (diskon >= threshold %)
melalui Webhook, Telegram Bot API, dan WhatsApp API Gateway simulasi.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

class AlertDispatcher:
    """
    Dispatcher Notifikasi untuk Komunitas Showroom & Dealer Rekanan.
    """

    def __init__(self):
        self.webhook_url = os.environ.get("ALERT_WEBHOOK_URL", "")
        self.telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    def format_deal_message(self, deal: Dict[str, Any]) -> str:
        """Format pesan teks notifikasi resmi deal arbitrase."""
        return (
            f"[HOT DEAL ARBITRASE TERDETEKSI]\n"
            f"Kendaraan: {deal.get('motor_name', 'Motor')}\n"
            f"Tahun: {deal.get('year', '-')}\n"
            f"Harga Iklan: Rp {deal.get('price', 0):,.0f}\n"
            f"Fair Market Value: Rp {deal.get('fair_market_value', 0):,.0f}\n"
            f"Potensi Cuan (Hemat): Rp {deal.get('saving_amount', 0):,.0f} (-{deal.get('discount_pct', 0):.1f}%)\n"
            f"Lokasi: {deal.get('city', '-')}\n"
            f"Pajak: {deal.get('tax_status', '-')}\n"
            f"Link Listing: {deal.get('url', '-')}\n"
            f"Waktu Deteksi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')}"
        )

    def dispatch_deal(self, deal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mengirim notifikasi deal ke seluruh channel yang terkonfigurasi.
        """
        msg = self.format_deal_message(deal)
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "deal_id": deal.get("listing_id"),
            "discount_pct": deal.get("discount_pct"),
            "channels": {}
        }

        # 1. Webhook Dispatch
        if self.webhook_url:
            try:
                payload = {"event": "HOT_DEAL_ALERT", "deal": deal, "formatted_message": msg}
                res = requests.post(self.webhook_url, json=payload, timeout=4)
                results["channels"]["webhook"] = {"status": "SUCCESS" if res.status_code == 200 else "ERROR", "code": res.status_code}
            except Exception as e:
                results["channels"]["webhook"] = {"status": "FAILED", "error": str(e)}
        else:
            results["channels"]["webhook"] = {"status": "SKIPPED", "note": "Webhook URL tidak dikonfigurasi"}

        # 2. Telegram Bot Dispatch
        if self.telegram_bot_token and self.telegram_chat_id:
            try:
                tg_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                tg_payload = {"chat_id": self.telegram_chat_id, "text": msg}
                res = requests.post(tg_url, json=tg_payload, timeout=4)
                results["channels"]["telegram"] = {"status": "SUCCESS" if res.status_code == 200 else "ERROR"}
            except Exception as e:
                results["channels"]["telegram"] = {"status": "FAILED", "error": str(e)}
        else:
            results["channels"]["telegram"] = {"status": "SKIPPED", "note": "Telegram bot token/chat_id tidak dikonfigurasi"}

        return results

alert_dispatcher = AlertDispatcher()
