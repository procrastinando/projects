import streamlit as st
import os
import subprocess
import yaml

# Helper functions to manage directories and files
def get_directories():
    return [d for d in os.listdir() if os.path.isdir(d) and os.path.exists(os.path.join(d, f"{d}_CV.yaml"))]

def delete_directory(directory):
    subprocess.run(["rm", "-rf", directory])

def load_yaml_file(yaml_path):
    with open(yaml_path, 'r') as file:
        return yaml.safe_load(file)

def save_yaml_file(yaml_path, data):
    with open(yaml_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

def create_new_directory(name):
    subprocess.run(["mkdir", name])
    subprocess.run(["rendercv", "new", name])

def render_pdf(directory, yaml_file):
    subprocess.run(["rendercv", "render", os.path.join(directory, yaml_file)])

# Streamlit UI

st.title("RenderCV Manager")

# Section: Create new directory
st.subheader("Create a New CV Directory")
new_name = st.text_input("Enter the directory name")
if st.button("New"):
    if new_name:
        create_new_directory(new_name)
        st.success(f"New directory '{new_name}' created!")
    else:
        st.error("Please enter a name.")
    st.experimental_rerun()

# Divider
st.markdown("---")

# Section: Manage existing directories
directories = get_directories()

if directories:
    st.subheader("Manage CV Directories")

    # Dropdown to select directory
    selected_dir = st.selectbox("Select a CV directory", directories)

    # Delete button
    if st.button("Delete"):
        if selected_dir:
            delete_directory(selected_dir)
            st.success(f"Directory '{selected_dir}' deleted!")
            st.experimental_rerun()

    # Show and edit YAML content
    yaml_file_path = os.path.join(selected_dir, f"{selected_dir}_CV.yaml")
    if os.path.exists(yaml_file_path):
        yaml_data = load_yaml_file(yaml_file_path)

        st.subheader(f"Edit {selected_dir}_CV.yaml")
        edited_yaml = st.text_area("YAML Content", value=yaml.dump(yaml_data, default_flow_style=False), height=300)

        if st.button("Update"):
            save_yaml_file(yaml_file_path, yaml.safe_load(edited_yaml))
            st.success(f"YAML file for '{selected_dir}' updated!")

        # Render PDF button
        if st.button("Render PDF"):
            render_pdf(selected_dir, f"{selected_dir}_CV.yaml")
            pdf_file_path = os.path.join(selected_dir, "rendercv_output", f"{yaml_data['real_name']}_CV.pdf")
            if os.path.exists(pdf_file_path):
                with open(pdf_file_path, 'rb') as pdf_file:
                    st.download_button(label="Download PDF", data=pdf_file, file_name=f"{yaml_data['real_name']}_CV.pdf", mime="application/pdf")
            else:
                st.error("PDF rendering failed.")

else:
    st.write("No directories available.")
