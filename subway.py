from typing import Any

# import httpx # This import is no longer used.
from mcp.server.fastmcp import FastMCP
from nyct_gtfs import NYCTFeed
from datetime import datetime

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
        target_direction: The direction of the train ("N" for Northbound / Uptown, "S" for Southbound / Downtown).
        feed_id: The GTFS feed ID for the subway lines (e.g., "1" for 1,2,3,4,5,6,S lines).
                 Common Feed IDs:
                 "1": 1, 2, 3, 4, 5, 6, 7, S (42 St Shuttle)
                 "A": A, C, E, S (Rockaway Shuttle)
                 "N": N, Q, R, W
                 "B": B, D, F, M, S (Frankin Ave)
                 "L": L
                 "G": G
                 "J": J, Z
                 "7": 7
                 "SIR": Staten Island Railway

    This function returns a string with the next train arrival information for the given station and direction.
    You can use this tool to get the next train arrival information for a given station and direction.
    """
    try:
        feed = NYCTFeed(feed_id)
        trains_data = feed.trips
    except Exception as e:
        return f"Failed to load MTA feed data for feed ID {feed_id}: {e}"

    if not trains_data:
        return f"No train data found for feed ID {feed_id}."

    train_info_processed = get_train_info_list(trains_data)
    current_time = datetime.now().strftime("%H:%M:%S")
    train_info_string = f"Current time: {current_time}\n"
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
