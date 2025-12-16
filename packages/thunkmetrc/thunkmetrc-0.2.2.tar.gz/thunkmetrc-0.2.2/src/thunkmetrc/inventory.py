from typing import List, Optional, Any, Dict
from datetime import datetime, timedelta, timezone
from thunkmetrc.wrapper import MetrcWrapper

async def active_packages_inventory_sync(
    wrapper: MetrcWrapper,
    license_number: str,
    last_known_sync: Optional[datetime] = None,
    buffer_minutes: int = 5
) -> List[Dict[str, Any]]:
    """
    Syncs all active packages modified within the time window.
    
    :param wrapper: MetrcWrapper instance
    :param license_number: Facility license number
    :param last_known_sync: Last successful sync time (datetime). If None, defaults to 24h ago.
    :param buffer_minutes: Buffer to subtract from start time (default 5).
    :return: List of active packages
    """
    end_time = datetime.now(timezone.utc)
    
    if last_known_sync:
        start_time = last_known_sync - timedelta(minutes=buffer_minutes)
    else:
        # Default to 24 hours ago if no sync state
        start_time = end_time - timedelta(hours=24)

    # Ensure UTC if naive (assume UTC if naive, or convert)
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)

    # Format as ISO 8601 strings (e.g. 2023-10-26T12:00:00+00:00)
    # isoformat() produces valid ISO 8601
    start_str = start_time.isoformat()
    end_str = end_time.isoformat()

    all_packages: List[Dict[str, Any]] = []
    page = 1
    page_size = 20

    while True:
        # Wrapper method signature (from generator):
        # async def packages_get_active_v2(self, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None, body: Any = None) -> Any:
        
        # Note: Argument order matters if positional, but keyword args are safer.
        # Generated code uses keyword arguments for query params in the wrapper calling client?
        # Actually wrapper generator adds them as keyword args to the signature defaults.
        
        response = await wrapper.packages_get_active_v2(
            last_modified_end=end_str,
            last_modified_start=start_str,
            license_number=license_number,
            page_number=str(page),
            page_size=str(page_size)
        )

        if response:
            # Response should be a dict if parsed from JSON
            # e.g. { "Data": [...], "TotalPages": 1 }
            data = response.get("Data")
            if isinstance(data, list):
                all_packages.extend(data)
            
            total_pages = response.get("TotalPages")
            if isinstance(total_pages, int):
                if page >= total_pages:
                    break
            else:
                # No pagination info or single page?
                break
        else:
            break

        page += 1

    return all_packages
