from datastar import *
import time

# Create a project and a macro
project = Project.create(
    "Example project for work_with_tasks", "Created by tasks example script"
)
macro = project.add_macro("Tasks Demo Macro")

# Prepare connections used by tasks
csv_connection = connections.DelimitedConnection(
    path="/My Files/Datastar/Customers.csv"
)
sandbox = project.get_sandbox()

# Add an Import task (CSV to sandbox)
import_task = macro.add_import_task(
    name="import_customers",
    source_connection=csv_connection,
    destination_connection=sandbox,
    destination_table="customers_demo",
)

# Add a Run SQL task (operate on sandbox table)
sql_task = macro.add_run_sql_task(
    name="clean_cities",
    query="delete from customers_demo where city = 'london'",
    connection=sandbox,
)

# TODO: Export task not working in backend

# Add an Export task (sandbox table to a file)
# export_task = macro.add_export_task(
#    name="export_customers",
#    source_connection=sandbox,
#    source_table="customers_demo",
#    file_name="customers_out.csv",
# )

# List and fetch tasks
task_names = macro.get_tasks()
print("Tasks configured:", task_names)
assert "import_customers" in task_names
assert macro.get_task("clean_cities") is not None

# Update a task then persist changes
sql_task.description = "Remove London rows"
sql_task.name = "cleanup_cities"
sql_task.save()  # save updates existing tasks

# Add/remove dependencies by name (use the Python task since export is disabled)

# Create a task
preconfigured = RunPythonTask(
    macro,
    filename="script.py",
    directory_path="/My Files/Scripts",
)


# Demonstrate add and remove dependencies on a task
# Use a task that isn't already auto-joined (e.g., Start)
preconfigured.add_dependency(Task.START_NAME)
deps = preconfigured.get_dependencies()
assert Task.START_NAME in deps
preconfigured.remove_dependency(Task.START_NAME)

# Start a macro run and wait for completion
print("Waiting 5s before running macro...")
time.sleep(5)
print("Running macro...")
macro.run()
macro.wait_for_done(verbose=True)
print("Macro finished.")

# Cleanup
# Delete the project first to remove task references to the CSV connection,
# then delete the standalone connection to avoid HTTP 409 conflicts.
project.delete()
csv_connection.delete()

print("Done")
