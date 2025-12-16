import hashlib
import logging
import os
import re
import stat
import sys
from pathlib import Path

import click as click


def sha1sum(filename):
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha1').hexdigest()


def is_hidden_file(filepath):
    if os.name == 'nt':
        return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
    else:
        return Path(filepath).name.startswith('.')


def exit_with_error(code: int):
    logging.error("Exiting.. Please check above errors")
    sys.exit(code)


def read_existing_checksums(checksum_file):
    """
    Read existing checksum.txt file and return a dictionary of filename -> checksum.
    
    Args:
        checksum_file: Path to the checksum.txt file
        
    Returns:
        Dictionary mapping filename to checksum, or empty dict if file doesn't exist
    """
    checksums = {}
    if not os.path.exists(checksum_file):
        return checksums
    
    try:
        with open(checksum_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comment lines
                if not line or line.startswith('#'):
                    continue
                # Parse tab-separated filename and checksum
                parts = line.split('\t')
                if len(parts) == 2:
                    filename, checksum = parts
                    checksums[filename] = checksum
    except Exception as e:
        logging.warning("[WARN] Could not read existing checksum.txt: %s", str(e))
    
    return checksums


@click.command()
@click.option('--files_dir', type=click.Path(), required=False,
              help="Checksum will be computed for all the files in this directory")
@click.option('--files_list_path', type=click.Path(), required=False,
              help="Path of the file that contains list of all files whose Checksum should be computed")
@click.option('--out_path', type=click.Path(), required=True, help="Path to save the computed checksum.txt file")
def main(files_dir, files_list_path, out_path):
    # Configure logging to output to console
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    if not os.path.isdir(out_path):
        logging.error("[ERROR] Output directory doesn't exist: %s", out_path)
        exit_with_error(1)

    checksum_file = os.path.join(out_path, "checksum.txt")
    
    # Read existing checksums if file exists (for incremental updates)
    existing_checksums = {}
    if os.path.exists(checksum_file):
        logging.info("[INFO] checksum.txt already exists. Will perform incremental update.")
        existing_checksums = read_existing_checksums(checksum_file)
        logging.info("[INFO] Found %d existing checksum entries.", len(existing_checksums))
    
    # Check write permissions
    try:
        cfile = open(checksum_file, 'w')
        cfile.write('# SHA-1 Checksum \n')
        cfile.close()
    except PermissionError as e:
        logging.error("[ERROR] No permissions to write to: %s", checksum_file)
        exit_with_error(1)

    f_list = []
    if files_dir is None and files_list_path is None:
        logging.error("[ERROR] Either dir option or list option should be specified")
        exit_with_error(1)

    if files_dir is not None:
        if not os.path.isdir(files_dir):
            logging.error("[ERROR] Directory doesn't exist: %s", files_dir)
            exit_with_error(1)
        else:
            dir_list = os.listdir(files_dir)
            for file_name in dir_list:
                if file_name == 'checksum.txt':
                    continue
                full_file_name = os.path.join(files_dir, file_name)
                if os.path.isdir(full_file_name) and not is_hidden_file(full_file_name):
                    logging.error("[ERROR] Directories are not allowed: %s", file_name)
                    exit_with_error(1)
                if os.path.isfile(full_file_name) and bool(re.search('[^-_.A-Za-z0-9]', file_name)):
                    logging.error("[ERROR] invalid filename (only underscore and hyphen special chars are allowed): %s", file_name)
                    exit_with_error(1)
                if not is_hidden_file(full_file_name):
                    f_list.append(full_file_name)

    if files_list_path is not None:
        if not os.path.isfile(files_list_path):
            logging.error("[ERROR] File doesn't exist: %s", files_list_path)
            exit_with_error(1)
        else:
            file_names = []
            dup_files = []
            with open(files_list_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not os.path.isfile(line):
                        if os.path.isdir(line):
                            logging.error("[ERROR] Directories are not allowed: %s", line)
                        else:
                            logging.error("[ERROR] File doesn't exist: %s", line)
                        exit_with_error(1)
                    elif is_hidden_file(line):
                        logging.error("[ERROR] Hidden files are not allowed: %s", line)
                        exit_with_error(1)
                    else:
                        f_list.append(line)
                        file_name = Path(line).name
                        if bool(re.search('[^-_.A-Za-z0-9]', file_name)):
                            logging.error("[ERROR] invalid filename (only underscore and hyphen special chars are allowed): %s", file_name)
                            exit_with_error(1)
                        if file_name in file_names:
                            dup_files.append(file_name)
                        else:
                            file_names.append(file_name)

            if len(dup_files) > 0:
                logging.error("[ERROR] Following files have duplicate entries: %s", dup_files)
                exit_with_error(1)
    
    # Build set of current filenames for tracking what's still present
    current_files = set()
    for f in f_list:
        current_files.add(Path(f).name)
    
    # Track statistics for incremental update
    reused_count = 0
    new_count = 0
    removed_count = 0
    
    # Identify removed files (in existing checksums but not in current files)
    if existing_checksums:
        removed_files = set(existing_checksums.keys()) - current_files
        removed_count = len(removed_files)
        if removed_files:
            logging.info("[INFO] Removing %d files that no longer exist: %s", removed_count, list(removed_files))
    
    # Open checksum file once and keep it open for all writes
    with open(checksum_file, 'a') as cfile:
        i = 0
        for f in f_list:
            i = i+1
            file_name = Path(f).name
            
            # Check if we can reuse existing checksum
            if file_name in existing_checksums:
                sha1_sum = existing_checksums[file_name]
                reused_count += 1
                logging.info("[ %d / %d ] Reusing existing checksum for: %s -> %s", i, len(f_list), file_name, sha1_sum)
            else:
                # Compute new checksum
                logging.info("[ %d / %d ] Processing: %s", i, len(f_list), f)
                if not os.path.isfile(f):
                    logging.error("[ERROR] File no longer exists: %s", f)
                    exit_with_error(1)
                sha1_sum = sha1sum(f)
                new_count += 1
                logging.info("[ %d / %d ] Generated checksum for: %s -> %s", i, len(f_list), file_name, sha1_sum)
            
            # Write to checksum file
            cfile.write(file_name + '\t' + sha1_sum + '\n')

    out_path = Path(checksum_file).parent.resolve()
    logging.info("checksum.txt file has been stored in path: %s", out_path)
    
    # Print summary statistics if incremental update was performed
    if existing_checksums:
        logging.info("[INFO] Incremental update summary: %d reused, %d new, %d removed", 
                     reused_count, new_count, removed_count)


if __name__ == '__main__':
    main()
