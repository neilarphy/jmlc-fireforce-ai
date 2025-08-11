"""
Rosleshoz (Рослесхоз) scraping service.

Lightweight HTML fetch + regex extraction without external parser deps.
"""
from __future__ import annotations

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

ROSLESHOZ_URL = (
    "https://rosleshoz.gov.ru/activity/forest-security-and-protection/fires/operative-information/"
)

_WS = r"\s+"

# Simple disk cache to survive outages
_CACHE_DIR = Path("cache")
_CACHE_DIR.mkdir(exist_ok=True)
_CACHE_FILE = _CACHE_DIR / "rosleshoz_operative.json"
_CACHE_TTL = timedelta(hours=6)


def _curl_fetch(url: str, headers: Dict[str, str]) -> str | None:
    """Best-effort HTML fetch using local curl binary (if available)."""
    try:
        import subprocess
        cmd = [
            "curl",
            "-L",
            "--compressed",
            "-s",
        ]
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
        cmd.append(url)
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return out.decode("utf-8", errors="ignore")
    except Exception:
        return None


def _clean_number(num_str: str) -> int:
    try:
        return int(re.sub(r"\D", "", num_str))
    except Exception:
        return 0


def fetch_latest_operational_info(timeout_s: int = 10) -> Dict[str, Any]:
    """Fetch and parse key stats from Rosleshoz operative information page.

    Returns a dict with normalized fields suitable for the dashboard.
    """
    try:
        # Common headers for both curl and requests
        common_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
        }

        # 1) Try curl first (more reliable for this host)
        html = _curl_fetch(ROSLESHOZ_URL, headers=common_headers)
        if html and len(html) > 500:
            logger.info("Rosleshoz fetch via curl")
            text = re.sub(r"\s+", " ", html).strip()
        else:
            logger.info("Rosleshoz curl fallback not used (no curl or short body), using requests")
            # 2) Robust session with retries
            session = requests.Session()
            retry = Retry(
                total=3,
                backoff_factor=0.8,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=("GET",),
                raise_on_status=False,
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            resp = session.get(
                ROSLESHOZ_URL,
                timeout=timeout_s,
                headers=common_headers,
            )
            resp.raise_for_status()
            html = resp.text
            # Normalize spaces
            text = re.sub(r"\s+", " ", html).strip()

        # Split page into sections by each bulletin header and pick the most recent date
        sections = []
        for m in re.finditer(r"Оперативная информация[^\\n]*?на\\s+(\\d{2}\\.\\d{2}\\.\\d{4})", text):
            try:
                d = datetime.strptime(m.group(1), "%d.%m.%Y")
            except Exception:
                continue
            sections.append((d, m.start()))
        focus = text
        bulletin_date = None
        if sections:
            sections.sort(key=lambda x: x[0], reverse=True)
            top_date, top_start = sections[0]
            # end at next header or end of text
            next_headers = [pos for (_, pos) in sections[1:]]
            top_end = next_headers[0] if next_headers else len(text)
            # clamp window
            focus = text[top_start:top_end]
            bulletin_date = top_date.strftime("%d.%m.%Y")
        else:
            # fallback to first occurrence
            date_anchor = re.search(r"Оперативная информация[^\\n]*?на\\s+(\\d{2}\\.\\d{2}\\.\\d{4})", text)
            if date_anchor:
                start = max(0, date_anchor.start())
                focus = text[start:start + 6000]
                date_match = re.search(r"на\\s+(\\d{2}\\.\\d{2}\\.\\d{4})", focus)
                bulletin_date = date_match.group(1) if date_match else None

        # Yesterday extinguished: "ликвидировано 47 лесных пожаров на площади 16 864 га"
        extinguished_match = re.search(
            r"ликвидировано\s+(\d+)\s+лесных пожаров\s+на площади\s+([\d\s]+)\s*га",
            focus,
            re.IGNORECASE,
        )
        extinguished_count = int(extinguished_match.group(1)) if extinguished_match else 0
        extinguished_area_ha = _clean_number(extinguished_match.group(2)) if extinguished_match else 0

        # Active now: "проводятся работы по тушению 55 лесных пожаров на площади 13 524 га"
        active_match = re.search(
            r"проводятся работы по тушению\s+(\d+)\s+лесных пожаров\s+на площади\s+([\d\s]+)\s*га",
            focus,
            re.IGNORECASE,
        )
        active_count = int(active_match.group(1)) if active_match else 0
        active_area_ha = _clean_number(active_match.group(2)) if active_match else 0

        # Resources: "задействовано 2 252 человека, 220 единиц техники и 34 воздушных судна"
        res_match = re.search(
            r"задействовано\s+([\d\s]+)\s+человек,\s+([\d\s]+)\s+единиц техники\s+и\s+([\d\s]+)\s+воздуш",
            focus,
            re.IGNORECASE,
        )
        people = _clean_number(res_match.group(1)) if res_match else 0
        vehicles = _clean_number(res_match.group(2)) if res_match else 0
        aircraft = _clean_number(res_match.group(3)) if res_match else 0

        em_match = re.search(r"Режим\s+ЧС\s+введен.*?в\s+(\d+)\s+субъектах", focus, re.IGNORECASE)
        em_regions = int(em_match.group(1)) if em_match else 0

        special_match = re.search(
            r"Особый\s+противопожарный\s+режим\s+установлен\s+в\s+(\d+)\s+субъектах",
            focus,
            re.IGNORECASE,
        )
        special_regions = int(special_match.group(1)) if special_match else 0

        # Extract region names list (very rough)
        regions_list: list[str] = []
        # Regions where fires were extinguished (used for indicative points)
        reg_match = re.search(r"Лесные пожары ликвидированы в\s+(.+?)\.", focus)
        if reg_match:
            blob = reg_match.group(1)
            # split by commas and ' и ' and semicolons (site sometimes uses lists)
            parts = re.split(r",| и |;", blob)
            cleaned = []
            for p in parts:
                name = p.strip()
                # normalize endings like 'краях', 'областях' -> singular
                name = re.sub(r"\s+краях$", " край", name)
                name = re.sub(r"\s+крае$", " край", name)
                name = re.sub(r"\s+областях$", " область", name)
                name = re.sub(r"\s+области$", " область", name)
                name = re.sub(r"\bв\s+республике\b", " Республика", name, flags=re.IGNORECASE)
                name = re.sub(r"\bв\s+республиках\b", " Республика", name, flags=re.IGNORECASE)
                name = re.sub(r"\bреспублик[ае]\b", " Республика", name, flags=re.IGNORECASE)
                # fix broken merges seen in curl outputs like 'Запs':[...])РА)
                name = re.sub(r"[^а-яА-Я\s\-()]+", "", name)
                if name:
                    cleaned.append(name)
            regions_list = [n for n in (c.strip() for c in cleaned) if n]

        summary = (
            f"По данным Рослесхоза на {bulletin_date or ''}: ликвидировано {extinguished_count} пожаров, "
            f"активно {active_count} (≈{active_area_ha} га); задействованы {people} чел., {vehicles} техн., {aircraft} ВС."
        ).strip()

        result = {
            "source": "rosleshoz",
            "source_url": ROSLESHOZ_URL,
            "fetched_at": datetime.utcnow().isoformat(),
            "bulletin_date": bulletin_date,
            "extinguished_count": extinguished_count,
            "extinguished_area_ha": extinguished_area_ha,
            "active_count": active_count,
            "active_area_ha": active_area_ha,
            "staff_count": people,
            "equipment_count": vehicles,
            "aircraft_count": aircraft,
            "emergency_regions": em_regions,
            "special_regime_regions": special_regions,
            "summary": summary,
            "regions": regions_list,
        }
        # Save cache
        try:
            _CACHE_FILE.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        return result
    except Exception as e:
        logger.error(f"Rosleshoz fetch failed: {e}")
        # Try curl fallback once
        try:
            html = _curl_fetch(ROSLESHOZ_URL, headers=common_headers)  # type: ignore[name-defined]
            if html:
                text = re.sub(r"\s+", " ", html).strip()
                focus = text
                date_anchor = re.search(r"Оперативная информация[^\n]*?на\s+(\d{2}\.\d{2}\.\d{4})", text)
                if date_anchor:
                    start = max(0, date_anchor.start())
                    focus = text[start:start + 6000]
                date_match = re.search(r"на\s+(\d{2}\.\d{2}\.\d{4})", focus)
                bulletin_date = date_match.group(1) if date_match else None
                extinguished_match = re.search(
                    r"ликвидировано\s+(\d+)\s+лесных пожаров\s+на площади\s+([\d\s]+)\s*га",
                    focus,
                    re.IGNORECASE,
                )
                extinguished_count = int(extinguished_match.group(1)) if extinguished_match else 0
                extinguished_area_ha = _clean_number(extinguished_match.group(2)) if extinguished_match else 0
                active_match = re.search(
                    r"проводятся работы по тушению\s+(\d+)\s+лесных пожаров\s+на площади\s+([\d\s]+)\s*га",
                    focus,
                    re.IGNORECASE,
                )
                active_count = int(active_match.group(1)) if active_match else 0
                active_area_ha = _clean_number(active_match.group(2)) if active_match else 0
                res_match = re.search(
                    r"задействовано\s+([\d\s]+)\s+человек,\s+([\d\s]+)\s+единиц техники\s+и\s+([\d\s]+)\s+воздуш",
                    focus,
                    re.IGNORECASE,
                )
                people = _clean_number(res_match.group(1)) if res_match else 0
                vehicles = _clean_number(res_match.group(2)) if res_match else 0
                aircraft = _clean_number(res_match.group(3)) if res_match else 0
                em_match = re.search(r"Режим\s+ЧС\s+введен.*?в\s+(\d+)\s+субъектах", focus, re.IGNORECASE)
                em_regions = int(em_match.group(1)) if em_match else 0
                special_match = re.search(
                    r"Особый\s+противопожарный\s+режим\s+установлен\s+в\s+(\d+)\s+субъектах",
                    focus,
                    re.IGNORECASE,
                )
                special_regions = int(special_match.group(1)) if special_match else 0
                regions_list: list[str] = []
                reg_match = re.search(r"Лесные пожары ликвидированы в\s+(.+?)\.", focus)
                if reg_match:
                    blob = reg_match.group(1)
                    parts = re.split(r",| и ", blob)
                    regions_list = [p.strip() for p in parts if p.strip()]
                summary = (
                    f"По данным Рослесхоза на {bulletin_date or ''}: ликвидировано {extinguished_count} пожаров, "
                    f"активно {active_count} (≈{active_area_ha} га); задействованы {people} чел., {vehicles} техн., {aircraft} ВС."
                ).strip()
                result = {
                    "source": "rosleshoz",
                    "source_url": ROSLESHOZ_URL,
                    "fetched_at": datetime.utcnow().isoformat(),
                    "bulletin_date": bulletin_date,
                    "extinguished_count": extinguished_count,
                    "extinguished_area_ha": extinguished_area_ha,
                    "active_count": active_count,
                    "active_area_ha": active_area_ha,
                    "staff_count": people,
                    "equipment_count": vehicles,
                    "aircraft_count": aircraft,
                    "emergency_regions": em_regions,
                    "special_regime_regions": special_regions,
                    "summary": summary,
                    "regions": regions_list,
                }
                try:
                    _CACHE_FILE.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass
                return result
        except Exception:
            pass
        # Try cache first
        try:
            if _CACHE_FILE.exists():
                stat = _CACHE_FILE.stat()
                age_ok = datetime.utcnow() - datetime.utcfromtimestamp(stat.st_mtime) <= _CACHE_TTL
                cached = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
                if age_ok:
                    cached["stale"] = False
                else:
                    cached["stale"] = True
                cached["error"] = str(e)
                return cached
        except Exception:
            pass

        # Return safe fallback
        return {
            "source": "rosleshoz",
            "source_url": ROSLESHOZ_URL,
            "fetched_at": datetime.utcnow().isoformat(),
            "bulletin_date": None,
            "extinguished_count": 0,
            "extinguished_area_ha": 0,
            "active_count": 0,
            "active_area_ha": 0,
            "staff_count": 0,
            "equipment_count": 0,
            "aircraft_count": 0,
            "emergency_regions": 0,
            "special_regime_regions": 0,
            "summary": "Данные Рослесхоза временно недоступны",
            "error": str(e),
        }


