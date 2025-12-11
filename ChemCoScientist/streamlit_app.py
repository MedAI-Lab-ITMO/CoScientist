import streamlit as st
from dotenv import load_dotenv

from ChemCoScientist.frontend import chat, init_page, side_bar
from ChemCoScientist.frontend.paper_management import paper_management
from ChemCoScientist.frontend.dataset_management import dataset_management
from ChemCoScientist.frontend.utils import start_cleanup_thread
from ChemCoScientist.memory.json_db import JSONFileDB
from definitions import ROOT_DIR, CONFIG_PATH

load_dotenv(CONFIG_PATH)

import os

if __name__ == "__main__":

    path = f'{ROOT_DIR}/app/ChemCoScientist/data_store'
    os.makedirs(os.path.join(path, 'datasets'), exist_ok=True)
    os.makedirs(os.path.join(path, 'imgs'), exist_ok=True)
    os.makedirs(os.path.join(path, 'another'), exist_ok=True)

    db = JSONFileDB(os.environ.get('MEMORY_DB_PATH', 'ChemCoScientist/data_store/files_db.json'))

    start_cleanup_thread()
    init_page()
    side_bar()

    # Add these 4 lines BEFORE your existing tabs code
    if "stay_on_files" not in st.session_state:
        st.session_state.stay_on_files = True

    # Delay paper_management() until after tabs render
    paper_content = None
    if st.session_state.stay_on_files:
        paper_content = st.container()

    # tab_chat, tab_files, tab_datasets = st.tabs(["💬 Chat", "📁 File Management", "Available Datasets"])
    #
    # with tab_chat:
    #     chat()
    # with tab_files:
    #     paper_management()
    # with tab_datasets:
    #     dataset_management(db)

    # # Replace your tabs section with:
    # if "active_tab" not in st.session_state:
    #     st.session_state.active_tab = "chat"  # or "files" to default to files
    #
    # tab_options = ["💬 Chat", "📁 File Management", "Available Datasets"]
    # selected_tab = st.tab_bar(
    #     tab_options,
    #     key="main_tabs",
    #     default=st.session_state.active_tab
    # )
    #
    # if selected_tab == tab_options[0]:
    #     st.session_state.active_tab = "chat"
    #     chat()
    # elif selected_tab == tab_options[1]:
    #     st.session_state.active_tab = "files"
    #     paper_management()
    # else:
    #     st.session_state.active_tab = "datasets"
    #     dataset_management(db)

    # # Replace ALL your tabs code with this:
    # if "active_tab" not in st.session_state:
    #     st.session_state.active_tab = "files"  # Default to File Management
    #
    # tab_choice = st.radio(
    #     "Navigate:",
    #     ["💬 Chat", "📁 File Management", "Available Datasets"],
    #     index=["chat", "files", "datasets"].index(st.session_state.active_tab),
    #     key="tab_selector",
    #     horizontal=True
    # )
    #
    # st.session_state.active_tab = {
    #     "💬 Chat": "chat",
    #     "📁 File Management": "files",
    #     "Available Datasets": "datasets"
    # }[tab_choice]
    #
    # if st.session_state.active_tab == "chat":
    #     chat()
    # elif st.session_state.active_tab == "files":
    #     paper_management()
    # else:
    #     dataset_management(db)

    # # 1. Initialize tab state BEFORE tabs
    # if "active_tab" not in st.session_state:
    #     st.session_state.active_tab = "files"  # Default to File Management
    #
    # # 2. Render tabs ONCE in a container
    # with st.container():
    #     tab_chat, tab_files, tab_datasets = st.tabs(["💬 Chat", "📁 File Management", "Available Datasets"])
    #
    # # 3. Use EXPANDERS keyed to session state to simulate tab content
    # if st.session_state.active_tab == "chat":
    #     with st.expander("💬 Chat", expanded=True):
    #         chat()
    # elif st.session_state.active_tab == "files":
    #     with st.expander("📁 File Management", expanded=True):
    #         paper_management()
    # else:
    #     with st.expander("Available Datasets", expanded=True):
    #         dataset_management(db)
    #
    # # 4. Navigation buttons ABOVE tabs (click to change active tab)
    # col1, col2, col3 = st.columns(3)
    # if col1.button("💬 Chat"):
    #     st.session_state.active_tab = "chat"
    #     st.rerun()
    # if col2.button("📁 Files"):
    #     st.session_state.active_tab = "files"
    #     st.rerun()
    # if col3.button("📊 Datasets"):
    #     st.session_state.active_tab = "datasets"
    #     st.rerun()

    # tab_chat, tab_files, tab_datasets = st.tabs(["💬 Chat", "📁 File Management", "Available Datasets"],
    #                                             key="persistent_tabs")
    #
    # with tab_chat:
    #     st.empty()  # Placeholder - prevents content render
    # with tab_files:
    #     paper_management()
    # with tab_datasets:
    #     st.empty()  # Placeholder
    #
    # # Force File Management tab active after any backend call
    # if st.session_state.get("just_selected_file", False):
    #     del st.session_state["just_selected_file"]
    #     st.session_state.current_active_tab = "files"

    tab_chat, tab_files, tab_datasets = st.tabs(["💬 Chat", "📁 File Management", "Available Datasets"])

    with tab_chat:
        chat()
    with tab_files:
        if paper_content:
            paper_content.write("")  # Render paper_management() in container
            paper_management()
    with tab_datasets:
        dataset_management(db)


