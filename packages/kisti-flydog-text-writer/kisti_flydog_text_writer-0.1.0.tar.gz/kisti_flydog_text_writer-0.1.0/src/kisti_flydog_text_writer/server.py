from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")


@mcp.tool()
def get_textwriter(contents: str) -> None:
    """
    Save the text entered by the user as contentfile.txt on the D: drive of the user's computer.
    
    Args:
        contents (str): Text entered by the user.
    
    Returns:
        None
    """
    with open("D:/contentfile.txt", "a", encoding="utf-8") as file:
        file.write(contents)
        file.write("\n\n")  # Ensure the file ends with a newline
    print("Text saved to D:/contentfile.txt")


def main() -> None:
    # Initialize and run the server
    print("Starting Text Writer server...")
    mcp.run(transport='stdio')
    

if __name__ == "__main__":
   main()     