from datastar import *

TEST_PROJECT_NAME = "Example project for work_with_projects"
TEST_MACRO_NAME = "My new macro"


# Create a project (description is optional)
project = Project.create(TEST_PROJECT_NAME, "This is a test")

# List your existing projects
project_list = Project.get_projects()
print(project_list)
assert len(project_list) > 0

# Connect to an existing project
project_ref = Project.connect_to(TEST_PROJECT_NAME)

# Get a connection to the project sandbox
sandbox = project.get_sandbox()

# Alter the project details
project.name = "A new name"
project.description = "A new description"

# Persist project detail changes to db when ready (Note: will overwrite if out of sync with db)
project.save()

# Get a list of macros in the project
macro_list = project.get_macros()
assert len(macro_list) == 0

# Add a new macro to a project (name and description are optional)
project.add_macro(TEST_MACRO_NAME, "Macro description")

macro_list = project.get_macros()
print(macro_list)
assert len(macro_list) == 1

# Get a macro by name
macro = project.get_macro(TEST_MACRO_NAME)

# Remove a macro by name
project.delete_macro(TEST_MACRO_NAME)

macro_list = project.get_macros()
assert len(macro_list) == 0

# Delete a project
project.delete()

print("Done")
