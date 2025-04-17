#!/usr/bin/python
"""
Title: appplication: Ancient IBD Analysis Workflow
Date:2025-04-10
Author: Tongrui Zhang

Description:
    This program is a web application for analyzing ancient IBD (Identity By Descent) data between a modern individual and ancient populations.
    Users can upload a modern individual file in 23andMe format to calculate IBD, which will be validated and processed if necessary.
    The application also allows users to manage (upload or delete) ancient individual BAM files. Related config file should be correctly modified.
    After processing the input files, users can run the IBD calculation workflow using Snakemake. It also supports dry runs to preview the workflow without executing it. Number of cores can be set for the workflow.
    When the workflow is completed, the result will be displayed and can be downloaded as a TSV file.

List of functions:
    1.validate_bam_file(): validate the user-uploaded BAM file.
    check the file extension and use samtools to quickly validate the content.
    
Procedure:
    1. Preparation: check if the necessary directories exist and set up the streamlit web application with a title and description.
    2. Upload modern individual file: offer 2 choices for the user to upload a modern individual file:
    "Valid 23andMe input file with details: rsid, chromosome, position and genotype" which can directly upload and "Original 23andMe file needs processing" which needs validating and processing the file to be uploaded
    with the script valid_23am.py.
    3. Update ancient individual files: allow users to manage ancient individual BAM files, including uploading new files and deleting existing ones.
    Users should also modify the related config file to specify the correct sample names and BAM file paths for the changed files.
    Only valid updates will be accepted.
    4. Run IBD calculating: provide options to run the IBD analysis workflow using Snakemake.
    Users can choose to perform a dry run to preview the workflow or run it for real. The number of cores for the workflow can be set.
    5. Result: display the result of the IBD analysis, including a preview of the result report and a download option for the TSV file.

Usage:
    1.local computer: streamlit run app.py
    2.server: If connecting to the server via SSH, you may need to set up an SSH tunnel on local computer to access the application, eg. ssh -L 8501:localhost:8501 inf-48-2024@130.235.8.214
              Afterwards, run the command on the server: streamlit run app.py
              Users can also specify the server configuration parameters for the Streamlit application, eg. streamlit run app.py --server.port=8501 --server.address=0.0.0.0
"""
############################################################################################################################################
import streamlit as st
import os
import subprocess
import pandas as pd
import yaml
from pathlib import Path
import tempfile

def validate_bam_file(uploaded_file):

    try:
        # check the file extension: it should end with .bam
        if not uploaded_file.name.lower().endswith('.bam'):
            st.warning("file should end with .bam")
            return False

        # use tempfile to create a temporary file for validation
        with tempfile.NamedTemporaryFile(delete=True, suffix='.bam') as temp_file:
            temp_path = temp_file.name
            temp_file.write(uploaded_file.getbuffer())
            temp_file.flush()

            # validate the BAM file using samtools quickcheck
            # if no samtools, just skip the check 
            try:
                result = subprocess.run(
                    ["samtools", "quickcheck", temp_path], 
                    capture_output=True, 
                    text=True
                )

                if result.returncode == 0:
                    return True
                else:
                    st.error("invalid bam file didn't pass the samtools check")
                    return False
            except FileNotFoundError:
                st.warning("no samtools, still allow uploading but should be careful of bam file content")
                return True

    except Exception as e:
        st.error(f"error in checking bam file: {str(e)}")
        return False

#check the original directory structure and make sure the required folders exist in the current working directory
if not os.path.exists("resources/testind") or not os.path.exists("config") or not os.path.exists("resources/anc_bam"):
    st.error("❌ ERROR: lack required directory structure!")
    st.error("Make sure you are running in the correct working directory")
    st.error("basic directory needed：'resources/testind' and 'config' and 'resources/anc_bam'")
    st.stop() 

st.set_page_config(
    page_title="Ancient IBD Calculation Workflow",
    page_icon="🧬",
    layout="wide"
)
    
# set up title and description for the web application
st.title("🧬 Ancient IBD Analysis Workflow")
st.markdown("Upload a modern individual file and calculate the IBD against ancient populations with this workflow.")

# Upload modern individual file
st.header("1. Upload modern individual file")
# offer 2 choices for the user to upload a modern individual file
file_type = st.radio(
    "choose file format",
    ["Valid 23andMe input file with details: rsid, chromosome, position and genotype", "Original 23andMe file needs processing"],
    help="Choose 'valid 23andMe input file with details: rsid, chromosome, position and genotype' if you're totally sure\
        your file is valid, otherwise choose 'original 23andMe file needs processing' to make your input file valid."
)
# file uploader with dynamic label based on file type selection
uploaded_file = st.file_uploader(
    "Upload your modern file" + ("(Original 23andMe file format)" if file_type == "Original 23andMe file needs processing" else " (with valid format)"), 
    type=["txt", "csv"]
)

# process the uploaded file
mdsample = None
modern_file_path = None
validated_file_path = None

if uploaded_file is not None:
    filename = uploaded_file.name
    temp_file_path = f"resources/testind/temp_{filename}"

    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ file has been uploaded: {filename}")
    # when user chooses the original 23andMe file format, it needs to be validated and processed
    if file_type == "Original 23andMe file needs processing":
        
        processed_filename = f"{Path(filename).stem}_processed.txt"
        validated_file_path = f"resources/testind/{processed_filename}"
        
        # use the script valid_23am.py to validate and process the file
        try:
            
            process = subprocess.run(
                ["python", "valid_23am.py", temp_file_path, validated_file_path],
                capture_output=True,
                text=True
            )
            # check the return code and output different corresponding messages for successful and failed upload
            if process.returncode == 0:
                st.success(f"✅ file has been sucessfully processed and saved: {processed_filename}")
                modern_file_path = validated_file_path
                mdsample = Path(processed_filename).stem
            else:
                st.error("❌ file format validation failed")
                error_msg = process.stderr if process.stderr else process.stdout
                st.error(f"error message as followed：\n{error_msg}")
                
                # offer the option to download the original file for modification
                with open(temp_file_path, 'rb') as f:
                    st.download_button(
                        label="📥 download the original file for modification",
                        data=f,
                        file_name=filename,
                        mime="text/plain"
                    )
        except Exception as e:
            st.error(f"error occurred while processing the original modern individual input file: {str(e)}")
    # when user chooses the valid 23andMe input file format, it can be directly uploaded
    else:
        modern_file_path = f"resources/testind/{filename}"
        # rename the temp file to the final file name
        if os.path.exists(temp_file_path):
            os.rename(temp_file_path, modern_file_path)
        mdsample = Path(filename).stem
        st.info(f"📄 file saved: {modern_file_path}")
    
    # update the config file with the modern sample name and path
    if modern_file_path and mdsample:
        config_path = "config/config.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file) or {}
        else:
            config = {}
        
        config['modern_sample'] = modern_file_path        
        with open(config_path, 'w') as file:
            yaml.dump(config, file)
        
        st.success("✅ config updated!")

# manage ancient individual files (this part is not recommended as it'll take a long time to process the updated files even only 1 ancient file changed. it's a challenge for patience.)
# (more importantly, if there's really a need to change the ancient individual files, it's more effienct to update the BAM files the related config file directly instead of doing it on the web.)
st.header("2. Update ancient individual files (NOT recommended)")
show_ancient_management = st.checkbox("I need to change the Ancient Individuals file", value=False)

if show_ancient_management:
    anc_samples_path = "config/anc_samples.tsv"
    # load the existing ancient individual sample related config file
    ancient_df = pd.read_csv(anc_samples_path, sep='\t')
    
    st.subheader("edit anc_samples.tsv (recording ancient individual sample name and related file path")    
    # create a data editor for the ancient individual sample config file
    edited_df = st.data_editor(ancient_df, use_container_width=True,num_rows="dynamic")
    
    # if the edited dataframe is not equal to the original dataframe, check the format of the edited dataframe
    # only update this config file if the format is correct
    if not edited_df.equals(ancient_df):
        
        format_error = False
        # check the sample path is provided in the edited table and starts with fixed format 'resources/anc_bam/' and ends with '.bam'
        for idx, row in edited_df.iterrows():
            if row['bam'] is None or pd.isna(row['bam']):
                st.info(f"❌ the {idx+1} row: bam file path is empty, it should start with 'resources/anc_bam/'")
                format_error = True
            elif not row['bam'].startswith('resources/anc_bam/') or not row['bam'].endswith('.bam'):
                st.info(f"❌ the {idx+1} row: bam file path should start with 'resources/anc_bam/' and end with '.bam'")
                format_error = True
  
        if not format_error:
            if st.button("table change saved"):
                edited_df.to_csv(anc_samples_path, sep='\t', index=False)
                st.success("✅ anc_samples.tsv has been updated")
                st.rerun()
    
    st.subheader("upload ancient individual bam file")

    # file_uploader for the ancient individual BAM file
    uploaded_bam = st.file_uploader("choose the ancient individual bam file to upload", type=['bam'])


    if uploaded_bam is not None:
        st.session_state['uploaded_bam'] = uploaded_bam
        uploaded_sample_id = os.path.basename(uploaded_bam.name).split('.')[0]
        
        # validate the uploaded BAM file
        if validate_bam_file(uploaded_bam):

            # show the upload-sample name selector for user to double check the file to be uploaded is for the expected sample, aslo check the update for the config file for ancient individual samples is correct
            # the selector will list all the sample names got from the edited dataframe (the config file for ancient individual samples)
            # user should select the sample name from selector that matches the uploaded BAM file name, or error message will be shown. this is based on the assumption that the sample name in the config file matches the BAM file name 
            # this will avoid the situation that user upload a BAM file but there's something wrong with the update for the related congig file          
            selected_sample = st.selectbox(
                "select sample file name", 
                edited_df['sample_name'].tolist(), # get the sample names from the edited dataframe
                key=f"sample_selector_{uploaded_bam.name}"  # use unique key for each file uploader
            )
            
            # check if the selected sample name from the selector matches the uploaded BAM file name
            names_match = selected_sample == uploaded_sample_id
            
            if not names_match:
                st.error(f"❌ selected sample name '{selected_sample}' isn't equal to '{uploaded_sample_id}'")
                st.warning("Please select the matching sample name or upload the correct BAM file")
            
            selected_row = edited_df[edited_df['sample_name'] == selected_sample].iloc[0]
            bam_path = selected_row['bam']
            
            # show the upload button for the BAM file in case the sample name matches
            if names_match:
                if st.button("ready to upload"):
                    if not bam_path.startswith('resources/anc_bam/'):
                        st.error("❌ bam file starts with 'resources/anc_bam/'?")
                    else:
                        os.makedirs(os.path.dirname(bam_path), exist_ok=True)
                        
                        with open(bam_path, "wb") as f:
                            f.write(uploaded_bam.getbuffer())
                        
                        st.success("✅ bam file saved")
                        st.rerun()
        else:
            st.error("❌ invalid bam file")

    # BAM file management list 
    st.subheader("List of uploaded bam files")
    for idx, row in edited_df.iterrows():
        sample_name = row['sample_name']
        bam_path = row['bam']
        
        # skip invalid paths for bam files 
        if bam_path is None or pd.isna(bam_path) or not bam_path.startswith('resources/anc_bam/'):
            continue
        
        bam_exists = os.path.exists(bam_path)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"sample: {sample_name}")
            st.write(f"path: {bam_path}")
            
            if bam_exists:
                file_size = os.path.getsize(bam_path) / (1024 * 1024)  # convert the filesize to MB
                st.info(f"file size: {file_size:.2f} MB")
            else:
                st.warning("⚠️ bam file doesn't exist")
        
        with col2:
            if bam_exists:
                if st.button(f"Delete", key=f"delete_{idx}"): #user can delete the bam file
                    try:
                        os.remove(bam_path)
                        st.success("✅ bam file has been deleted")
                        st.rerun()
                    except Exception as e:
                        st.error(f"error in deleting bam file: {str(e)}")

# run IBD calculating based on snakemake workflow
st.header("3. Run IBD calculating")

# user can choose the number of cores for running the workflow
cores = st.slider("choose cores for running", min_value=4, max_value=256, value=64, step=4)

col1, col2 = st.columns(2)

with col1:
    dry_run = st.button("dry run (for previewing)")

with col2:
    run_actual = st.button("run")

# Snakemake dry-run
if dry_run and mdsample:
    st.subheader("dry run output")
    with st.spinner("doing dry run..."):
        cmd = ["snakemake", "--dry-run", "--rerun-triggers", "mtime"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        st.code(result.stdout)
        if result.stderr:
            st.error("error output:")
            st.code(result.stderr)
# Snakemake run
if run_actual and mdsample:
    st.subheader("doing real workflow running")
    progress_bar = st.progress(0)
    status = st.empty()
    
    status.info("starting workflow running...")
    progress_bar.progress(10)
    
    log_area = st.empty()
    
    process = subprocess.Popen(
        ["snakemake", "--cores", str(cores), "--rerun-triggers", "mtime"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    logs = []

    progress = 10
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            logs.append(output.strip())
            log_area.code('\n'.join(logs[-20:])) # show the last 20 lines of the log
            
            if progress < 90:
                progress += 0.5
                progress_bar.progress(min(int(progress), 90))
            
    progress_bar.progress(100)
    
    return_code = process.poll()
    
    if return_code == 0:
        status.success("✅ workflow completed!")
        
        # show the result
        st.header("4. Result!")
        result_file = f"results/06_ibd/processed_ibd_report_{mdsample}.tsv"
        
        if os.path.exists(result_file):
            df = pd.read_csv(result_file, sep='\t')
            st.success(f"✅ result report found: {result_file}")
            
            st.subheader("report preview")
            st.dataframe(df)
            
            # create download button
            with open(result_file, 'rb') as f:
                st.download_button(
                    label="📥 Download results for TSV",
                    data=f,
                    file_name=f"processed_ibd_report_{mdsample}.tsv",
                    mime="text/tab-separated-values"
                )
        else:
            st.warning(f"result file not found: {result_file}")
    else:
        status.error(f"❌ workflow failed, check the return code: {return_code}")

# check if the result file already exists
if not (dry_run or run_actual) and mdsample:
    result_file = f"results/06_ibd/processed_ibd_report_{mdsample}.tsv"
    if os.path.exists(result_file):
        st.header("4. Result")
        df = pd.read_csv(result_file, sep='\t')
        st.success(f"✅ Found existed result: {result_file}")
        
        st.subheader("result preview")
        st.dataframe(df)
        
        with open(result_file, 'rb') as f:
            st.download_button(
                label="📥 Download results for TSV",
                data=f,
                file_name=f"processed_ibd_report_{mdsample}.tsv",
                mime="text/tab-separated-values"
            )