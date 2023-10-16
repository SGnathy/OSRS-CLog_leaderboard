import os
import requests
import concurrent.futures

# Get the directory of the currently executing script
script_directory = os.path.dirname(os.path.abspath(__file__))

print(script_directory)

# Define a function to make the API request
def fetch_data(url):
    response = requests.get(url)
    return response.json()

# Initialize an empty array for logging clogger data
cloggers = []

# Initialize an empty array for API calls
api_urls = []

# Error output string (Searching a name that doesn't exist etc)
errorString = ""

# Open the text file for reading
file_path = os.path.join(script_directory, "cloggers.txt")
with open(file_path, "r") as file:
    # Read each line from the file
    for line in file:
        # Remove leading and trailing whitespace and append the word to the array
        name = line.strip()
        # Create API_URL's
        api_urls.append(f"https://api.collectionlog.net/collectionlog/user/{name}")

# Create a ThreadPoolExecutor for parallel execution
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit API requests in parallel and store the futures
    futures = [executor.submit(fetch_data, url) for url in api_urls]

# Process the results as they become available
for future in concurrent.futures.as_completed(futures):
    try:
        response_data = future.result()
        if "error" in response_data:
            print("API Error:", response_data["error"])
            errorString += f"{response_data['error']}\n"
        else:
            #Add Account type and Log count to list
            clogger_object = {
                "name": response_data["collectionLog"]["username"],
                "accountType": response_data["collectionLog"]["accountType"],
                "uniqueItems": response_data["collectionLog"]["uniqueItems"],
                "uniqueObtained": response_data["collectionLog"]["uniqueObtained"]
            }
            # Truncate account type to minimise output spilling onto new line, particularly on Discord mobile
            match clogger_object["accountType"]:
                case "IRONMAN":
                    clogger_object["accountType"] = "IRONMAN"
                case "GROUP_IRONMAN":
                    clogger_object["accountType"] = "GIM"
                case "ULTIMATE_IRONMAN":
                    clogger_object["accountType"] = "UIM"
                case _:
                    clogger_object["accountType"] = "NORMAL"
            # Append to list
            cloggers.append(clogger_object)
    except Exception as e:
        print(f"Error for {e}")

# Sort the "cloggers" array of objects by the "uniqueObtained" key in descending order
sorted_data = sorted(cloggers, key=lambda x: x["uniqueObtained"], reverse=True)

# Create counter for 'Ranks'
count = 1
# Create output string
output_string = ""
# Build formatted string, appending each users data by rank
for data in sorted_data:
    individual_string = f"Rank {count} - {data['name']}: {data['uniqueObtained']}/{data['uniqueItems']} ({data['accountType']})\n---\n"
    output_string += individual_string
    count = count + 1

#Attach any errors to the end of the output_string
if errorString:
    output_string += f"\n\n Errors:\n{errorString}"

# print(output_string)

# Save the output string to a text file
file_path = os.path.join(script_directory, "clog_results.txt")
with open(file_path, "w") as file:
    file.write(output_string)
