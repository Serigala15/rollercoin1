#!/usr/bin/env python3
"""
panel1.py
Panel terminal sederhana untuk membaca config.json dan menjalankan
pengaturan lokal. Tidak melakukan login, mengirim token, atau
mengotomatisasi permainan/website.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"

SENSITIVE_KEYS = {
    "access_token",
    "refresh_token",
    "csrf_token",
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"File {CONFIG_FILE.name} tidak ditemukan. "
            "Letakkan config.json di folder yang sama dengan panel1.py."
        )

    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Format config.json harus berupa object JSON.")

    return data


def save_config(config: dict) -> None:
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def masked(value) -> str:
    if value is None:
        return "-"
    text = str(value)
    if len(text) <= 6:
        return "***"
    return text[:3] + "*" * (len(text) - 6) + text[-3:]


def show_config(config: dict) -> None:
    print("\n=== CONFIG ===")
    for key, value in config.items():
        if key in SENSITIVE_KEYS:
            print(f"{key}: {masked(value)}")
        else:
            print(f"{key}: {value}")


def choose_games(config: dict) -> None:
    current = config.get("selected_games", [])

    print("\nGame yang tersedia: 1-15")
    print("Saat ini:", current)
    raw = input("Masukkan nomor game (contoh: 1,2,3) atau A untuk semua: ").strip()

    if raw.lower() == "a":
        config["selected_games"] = list(range(1, 16))
    else:
        try:
            games = []
            for item in raw.split(","):
                n = int(item.strip())
                if not 1 <= n <= 15:
                    raise ValueError
                if n not in games:
                    games.append(n)

            if not games:
                raise ValueError

            config["selected_games"] = games
        except ValueError:
            print("Input tidak valid. Gunakan nomor 1-15, dipisahkan koma.")
            return

    save_config(config)
    print("Pilihan game disimpan.")


def toggle_game(config: dict) -> None:
    config["game"] = not bool(config.get("game", False))
    save_config(config)
    print("game =", config["game"])


def set_run_mode(config: dict) -> None:
    print("\n1. continuous")
    print("2. once")
    choice = input("Pilih mode: ").strip()

    if choice == "1":
        config["run_mode"] = "continuous"
    elif choice == "2":
        config["run_mode"] = "once"
    else:
        print("Pilihan tidak valid.")
        return

    save_config(config)
    print("run_mode =", config["run_mode"])


def local_loop(config: dict) -> None:
    """
    Loop lokal untuk memeriksa konfigurasi.
    Bagian interaksi dengan layanan eksternal sengaja tidak dilakukan.
    """
    delay = max(1, int(config.get("delay_loop", 30)))
    selected = config.get("selected_games", [])

    print("\n=== LOCAL RUN ===")
    print("Mode :", config.get("run_mode", "once"))
    print("Game :", selected)
    print("Delay:", delay, "detik")
    print("\nPanel berjalan dalam mode lokal.")
    print("Tidak ada login, request ke server, atau aksi otomatis pada website.")

    if config.get("run_mode") == "continuous":
        try:
            while True:
                print(
                    f"[LOCAL] konfigurasi aktif | "
                    f"games={selected} | delay={delay}s"
                )
                time.sleep(delay)
        except KeyboardInterrupt:
            print("\nDihentikan.")
    else:
        print("[LOCAL] satu kali pemeriksaan selesai.")


def menu(config: dict) -> None:
    while True:
        print("\n" + "=" * 44)
        print("          ROLLER PANEL - LOCAL")
        print("=" * 44)
        print("[1] Tampilkan config")
        print("[2] Pilih game")
        print("[3] ON/OFF game")
        print("[4] Ubah run mode")
        print("[5] Jalankan pemeriksaan lokal")
        print("[0] Keluar")

        choice = input("\nPilih fitur: ").strip()

        if choice == "1":
            show_config(config)
        elif choice == "2":
            choose_games(config)
        elif choice == "3":
            toggle_game(config)
        elif choice == "4":
            set_run_mode(config)
        elif choice == "5":
            local_loop(config)
        elif choice == "0":
            print("Keluar.")
            break
        else:
            print("Pilihan tidak tersedia.")


def main() -> None:
    try:
        config = load_config()
    except Exception as exc:
        print("Gagal membaca config.json:")
        print(exc)
        return

    menu(config)


if __name__ == "__main__":
    main()
