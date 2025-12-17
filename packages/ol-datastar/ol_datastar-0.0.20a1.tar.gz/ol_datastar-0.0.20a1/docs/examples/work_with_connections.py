from datastar import *

DESC = "Created by work_with_connections example"


# Minimal delimited (e.g. CSV) connection (required fields only)
csv = DelimitedConnection(path="/My Files/Datastar/Customers.csv")

# Full configuration
csv2 = DelimitedConnection(
    description="Customer flat file",
    path="/My Files/Datastar/Customers.csv",  # path visible to the platform
    delimiter=",",
    encoding="utf-8",
)

# Update basic details via properties, then persist (Delimited)
csv.name = "CSV rename"
csv.description = DESC
csv.delimiter = ";"  # change delimiter
csv.save()


# Cosmic Frog model connection by name
frog_by_name = FrogModelConnection(model_name="Datastar test")

# Update Frog model connection metadata and persist (does not change model binding)
frog_by_name.name = "Frog rename"
frog_by_name.description = DESC
frog_by_name.save()

# Optilogic database connection by name
opti_by_name = OptiConnection(
    storage_name="Datastar test",
    # Can also specify schema here
)

# Update Optilogic DB connection properties and persist
opti_by_name.name = "OL DB rename"
opti_by_name.description = DESC
opti_by_name.schema = "analytics_v2"
opti_by_name.save()

# Sandbox connection (special in-project connection)
# Access the sandbox via a project when needed
project = Project.create(
    "Example project for work_with_connections",
    "Created by datastar connections example script",
)
sandbox = project.get_sandbox()


# List existing connections by name (no filter)
collections = Connection.get_connections()
print(collections)


# List existing connections by name, filtered by type
collections_dsv = Connection.get_connections("dsv")
print(collections_dsv)


# Simple example: fetch an existing connection by name and print it
# Ensure the connection exists first
existing = DelimitedConnection(
    path="/My Files/Datastar/Existing.csv", name="Existing CSV"
)
fetched = Connection.get_connection("Existing CSV")
print(f"Fetched connection name: {fetched.name}")


# Clean up: delete all created connections - uncomment to examine the connections in UI
csv.delete()
csv2.delete()
frog_by_name.delete()
opti_by_name.delete()
existing.delete()

# Delete the example project when finished
project.delete()

print("Done")
