import httpx


async def lookup_ip_location(ip_address: str) -> str:
    url = f"http://ip-api.com/json/{ip_address}?fields=status,country,city"
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
    except Exception:
        return "Unknown"
    if data.get("status") != "success":
        return "Unknown"
    city = data.get("city") or "Unknown City"
    country = data.get("country") or "Unknown Country"
    return f"{city}, {country}"


# Alias used by services/auth_service.py
ip_to_country = lookup_ip_location
