# Create API instance using environment variables
# You can either provide a old JSON handle or let it create a new one with account ID and refresh token
api = myqapi.create(handle=json.loads(os.getenv("OLD_JSON")))

# Get devices as GarageDoor objects
print("Getting devices as GarageDoor objects:")
doors = api.devices()
for door in doors:
    print(f"  {door}")
    print(f"  Device ID: {door.device_id}")

print("\n" + "="*50 + "\n")

# Get raw device data
print("Getting raw device data:")
raw_devices = api.devices(raw=True)
print(json.dumps(raw_devices, indent=2))

print("\n" + "="*50 + "\n")

# Toggle the garage doors
for door in doors:
    if door.status().get("door_state") == "open":
        print(f"Closing {door.device_id}...")
        print(json.dumps(door.close(), indent=2))
    else:
        print(f"Opening {door.device_id}...")
        print(json.dumps(door.open(), indent=2))
    
    sleep(30)  # Wait for 30 seconds before checking status
    print(json.dumps(door.status(), indent=2))