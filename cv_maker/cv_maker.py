import streamlit as st
import os
import shutil
import subprocess
import yaml
import glob
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Get the absolute path of the directory containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Helper functions to manage directories and files
def get_cv(target_dir):
    lista = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
    return lista

def delete_cv(target_dir):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

def load_yaml_file(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        return yaml.safe_load(file)

def save_yaml_file(yaml_file_path, data):
    with open(yaml_file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

def new_cv(name, user_dir):
    # Check if a YAML file with the same name already exists
    yaml_files = get_cv(f"{script_dir}/{user_dir}")
    if name in yaml_files:
        st.error(f"The name '{name}' has already been used. Please choose a different name.")
    elif name == 'config':
        st.error(f"The name '{name}' cannot be used. Please choose a different name.")
    else:
        shutil.os.makedirs(f"{script_dir}/{user_dir}/{name}")
        subprocess.run(["rendercv", "new", name], cwd=f"{script_dir}/{user_dir}/{name}")

def render_pdf(yaml_file, user_dir, name):
    subprocess.run(["rendercv", "render", yaml_file], cwd=f"{script_dir}/{user_dir}/{name}")
    # Delete all files in the directory that are not .pdf
    for file in os.listdir(f"{script_dir}/{user_dir}/{name}/rendercv_output"):
        file_path = os.path.join(script_dir, user_dir, name, 'rendercv_output', file)
        if os.path.isfile(file_path) and not file.endswith('.pdf'):
            os.remove(file_path)
    st.rerun()

def main():
    st.sidebar.markdown("""
    ## Code Explanation
    """)

    config_file = 'config.yaml'
    with open(config_file) as file:
        config = yaml.load(file, Loader=SafeLoader)
    # Initialize the authenticator
    authenticator = stauth.Authenticate(config['credentials'],
                                        config['cookie']['name'],
                                        config['cookie']['key'],
                                        config['cookie']['expiry_days'])

    # Use the login form provided by the authenticator
    authenticator.login('main')

    if st.session_state['authentication_status'] == False:
        st.write(f"[Create an account](https://t.me/{config['bot_username']})")
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] == None:
        st.write(f"[Create an account](https://t.me/{config['bot_username']})")
    elif st.session_state['authentication_status']:
        authenticator.logout('Logout', 'main')
        st.title("CV maker")
        user_dir = st.session_state['username']
        if not os.path.exists(f"{script_dir}/{user_dir}"):
            shutil.os.makedirs(f"{script_dir}/{user_dir}")

        # Section: Create new directory
        col1, col2 = st.columns([3, 1])
        with col1:
            new_name = st.text_input("Enter new directory name")
        with col2:
            if st.button("New"):
                if new_name:
                    new_cv(new_name, user_dir)
                    st.success(f"New directory '{new_name}' created!")
                else:
                    st.error("Please enter a name.")
                st.rerun()

        # Divider
        st.markdown("---")

        # Section: Manage existing directories
        directories = get_cv(f"{script_dir}/{user_dir}")

        if directories:
            st.subheader("Manage CV Directories")

            # Dropdown to select directory
            col3, col4 = st.columns([3, 1])
            with col3:
                selected_dir = st.selectbox("Select directory", directories)
            with col4:
                if st.button("Delete"):
                    if selected_dir:
                        delete_cv(f"{script_dir}/{user_dir}/{selected_dir}")
                        st.rerun()

            # Show and edit YAML content
            yaml_files = [f for f in os.listdir(f"{script_dir}/{user_dir}/{selected_dir}") if f.endswith('.yaml')]
            if yaml_files:
                yaml_file_path = f"{script_dir}/{user_dir}/{selected_dir}/{yaml_files[0]}"
                yaml_data = load_yaml_file(yaml_file_path)
                cv_content = st.text_area("CV", value=yaml.dump(yaml_data.get('cv', {}), default_flow_style=False), height=300)
                design_content = st.text_area("Design", value=yaml.dump(yaml_data.get('design', {}), default_flow_style=False), height=300)

                if st.button("Update and render"):
                    updated_yaml_data = {
                        'cv': yaml.safe_load(cv_content),
                        'design': yaml.safe_load(design_content)
                    }
                    save_yaml_file(yaml_file_path, updated_yaml_data)
                    render_pdf(f"{selected_dir}_CV.yaml", user_dir, selected_dir)

                if os.path.exists(f"{script_dir}/{user_dir}/{selected_dir}/rendercv_output"):
                    pdf_files = [f for f in os.listdir(f"{script_dir}/{user_dir}/{selected_dir}/rendercv_output") if f.endswith('.pdf')]
                    for p in pdf_files:
                        pdf_file_path = f"{script_dir}/{user_dir}/{selected_dir}/rendercv_output/{p}"
                        with open(pdf_file_path, 'rb') as pdf_file:
                            st.download_button(label=f"Download {p}",
                                            data=pdf_file,
                                            file_name=p,
                                            mime="application/pdf")

if __name__ == "__main__":
    main()
