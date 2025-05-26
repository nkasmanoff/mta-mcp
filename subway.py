"""
This is a simple MCP server that provides information about the next train arrival at a given station and direction.


- Next steps:
- Integrate location?
- More testing with different lines and spelling issues
"""

from typing import Any

# import httpx # This import is no longer used.
from mcp.server.fastmcp import FastMCP
from nyct_gtfs import NYCTFeed


# Initialize FastMCP server
mcp = FastMCP("mta_subway_tracker")


# Helper function to convert datetime objects to string
def convert_datetime_to_string(datetime_obj: Any) -> str | None:
    if datetime_obj is None:
        return None
    return datetime_obj.strftime("%H:%M:%S")


# Helper function to process train data from NYCTFeed
def get_train_info_list(trains_data: Any) -> list[dict[str, Any]]:
    train_info_list_data = []
    for train in trains_data:
        train_info = {
            "name": str(train),
            "line": train.route_id,
            "direction": train.direction,
            "stop_time_updates": [],
        }
        train_info["stop_time_updates"] = [
            {"stop_name": x.stop_name, "arrival": convert_datetime_to_string(x.arrival)}
            for x in train.stop_time_updates
        ]
        train_info_list_data.append(train_info)
    return train_info_list_data


@mcp.tool()
async def get_next_mta_train(
    target_station: str, target_direction: str, feed_id: str = "1"
) -> str:
    """Get the next train arrival information for a given station and direction.

    Args:
        target_station: The name of the target station (e.g., "Times Sq-42 St", "14 St-Union Sq").
        target_direction: The direction of the train ("N" for Northbound, "S" for Southbound).
        feed_id: The GTFS feed ID for the subway lines (e.g., "1" for 1,2,3,4,5,6,S lines).
                 Common feed IDs:
                 "1": 1, 2, 3, 4, 5, 6, S (42 St Shuttle)
                 "26": A, C, E, H (Rockaway Shuttle), S (Franklin Ave Shuttle)
                 "16": N, Q, R, W
                 "21": B, D, F, M
                 "2": L
                 "11": G
                 "31": J, Z
                 "36": 7
                 "51": Staten Island Railway

    """
    try:
        # It's better to run blocking I/O in a separate thread for async compatibility
        # However, NYCTFeed itself might not be async. If issues arise, this part might need
        # to be wrapped with something like asyncio.to_thread in Python 3.9+
        # For now, assuming it's acceptable for the MCP tool context.
        feed = NYCTFeed(feed_id)
        trains_data = feed.trips
    except Exception as e:
        return f"Failed to load MTA feed data for feed ID {feed_id}: {e}"

    if not trains_data:
        return f"No train data found for feed ID {feed_id}."

    train_info_processed = get_train_info_list(trains_data)
    train_info_string = ""
    for train in train_info_processed:
        for stop in train["stop_time_updates"]:
            if (
                stop["stop_name"] == target_station
                and train["direction"] == target_direction
            ):
                # train_name = train["name"] # Original notebook had this, but it's often complex like "14:50 S 1 to South Ferry"
                train_line = train["line"]
                # train_direction = train["direction"] # Already have target_direction
                train_arrival = stop["arrival"]
                if train_arrival:
                    train_info_string += f"The next {target_direction} bound {train_line} train arriving at {target_station} will arrive at {train_arrival}.\n"
                else:
                    train_info_string += f"The next {target_direction} bound {train_line} train is scheduled at {target_station}, but arrival time is not currently available.\n"
    if train_info_string == "":
        return f"No {target_direction} bound trains found for {target_station} on feed {feed_id} at this time."
    return train_info_string


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
