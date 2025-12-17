from datastar import *
from datastar import Task

TEST_PROJECT_NAME = "Example project for work_with_macros"
TEST_MACRO_NAME = "My new macro"

project = Project.create(TEST_PROJECT_NAME, "Created by datastar macro example script")

# Add a macro to project
macro = project.add_macro(TEST_MACRO_NAME)

# Add a macro (name is automatic)
macro = project.add_macro()
print(macro.name)

# Change macro details
macro.name = "a new name"
macro.description = "a new description"

# Persist macro details to db
macro.save()


# Get list of tasks in a macro
task_list = macro.get_tasks()
assert len(task_list) == 1
assert task_list[0] == Task.START_NAME  # Automatic start task only!

# Use a helper to add a task to a macro (for more on tasks see work_with_tasks.py)
sql_task = macro.add_run_sql_task(
    query=f"delete from some_table where city = 'london'",
    connection=project.get_sandbox(),
)

# Minimal examples: add multiple tasks
t1 = macro.add_run_sql_task(query="select 1", connection=project.get_sandbox())
t2 = macro.add_run_sql_task(query="select 2", connection=project.get_sandbox())
macro.add_tasks([t1, t2])  # chains t1 -> t2

# Make several tasks depend on a single predecessor
fan1 = macro.add_run_sql_task(query="select 3", connection=project.get_sandbox())
fan2 = macro.add_run_sql_task(query="select 4", connection=project.get_sandbox())
macro.add_tasks([fan1, fan2], previous_task=sql_task)

# --- Examples: Copying tasks and macros ---

# 1) Copy a task to the same macro (a new task with "(copy)" suffix)
sql_task_copy_same = macro.add_task(sql_task)

# 2) Copy a task into a new macro in the same project
target_macro = project.add_macro("Copy Target Macro")
sql_task_copy_other = target_macro.add_task(sql_task)

# 3) Clone (copy) the whole macro within the same project
#    This creates a new macro with the same tasks and dependencies
macro_clone_same_project = macro.clone()

# 4) Clone the whole macro into a new project
clone_project = Project.create(
    f"{TEST_PROJECT_NAME} (clone target)", "Project created for macro clone example"
)
macro_clone_new_project = macro.clone(project=clone_project)

task_list = macro.get_tasks()
print("Tasks in macro:", task_list)
assert len(task_list) == 11

# Get an existing task by name
task_ref = macro.get_task(task_list[1])
assert task_ref
print(task_ref.name)

# Delete an existing task by name
macro.delete_task(task_ref.name)

# Delete a macro directly
macro2 = project.add_macro("Temp macro to delete")
macro2.delete()

# Start a macro run
macro.run()

# Wait for the macro run to complete
macro.wait_for_done(verbose=True)

# Clean up
clone_project.delete()
project.delete()

print("Done")
