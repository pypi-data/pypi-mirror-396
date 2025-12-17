from datastar import *
import pandas as pd

TEST_PROJECT_NAME = "Example project for work_with_sandbox"
df = pd.DataFrame({"id": [1, 2], "city": ["london", "paris"]})

project = Project.create(TEST_PROJECT_NAME, "Created by sandbox example script")

# Get a sandbox connection
sandbox = project.get_sandbox()

# Ensure the target table exists via a minimal SQL task
macro = project.add_macro()
macro.add_run_sql_task(
    query="CREATE TABLE IF NOT EXISTS example_table (id INT, city TEXT);",
    connection=sandbox,
)
macro.run()
macro.wait_for_done()

# Write to a sandbox table
sandbox.write_table(df, "example_table")

# Read from a sandbox table
data = sandbox.read_table("example_table")
print(data)

project.delete()

print("Done")
