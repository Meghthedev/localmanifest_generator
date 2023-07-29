import re

def read_manifest(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def write_manifest(file_path, lines):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def get_repo_info(line):
    path_start = line.find('path="') + len('path="')
    path_end = line.find('"', path_start)
    path = line[path_start:path_end]

    name_start = line.find('name="') + len('name="')
    name_end = line.find('"', name_start)
    name = line[name_start:name_end]

    return path, name

def remove_comments(lines):
    return [line for line in lines if not line.strip().startswith('<!--')]

def clean_stray_elements(lines):
    cleaned_lines = []
    ignore_linkfile = False
    for line in lines:
        if '<linkfile' in line:
            ignore_linkfile = True
        elif '</project>' in line:
            ignore_linkfile = False
            continue

        if not ignore_linkfile and line.strip().startswith('<'):
            cleaned_lines.append(line)

    # Remove all line gaps longer than one line
    final_lines = []
    empty_line_count = 0
    for line in cleaned_lines:
        if line.strip():  # Check if the line is not empty
            final_lines.append(line)
            empty_line_count = 0
        elif empty_line_count < 2:  # Keep one empty line
            final_lines.append(line)
            empty_line_count += 1

    return final_lines

def get_remote_name(line):
    if 'remote="' in line:
        start_index = line.index('remote="') + len('remote="')
        end_index = line.index('"', start_index)
        remote_name = line[start_index:end_index]
        return remote_name
    return None

def remote_exists(remote_name, manifest_lines):
    for line in manifest_lines:
        if f'<remote  name="{remote_name}"' in line:
            return True
    return False

def find_remote_block_end(lines, start_index):
    for i in range(start_index + 1, len(lines)):
        if '</remote>' in lines[i]:
            return i
    return start_index

def main():
    old_manifest_file = "old_manifest.xml"  # Replace with the path to your old manifest file
    new_manifest_file = "new_manifest.xml"  # Replace with the path to your new manifest file

    old_manifest_lines = read_manifest(old_manifest_file)
    new_manifest_lines = read_manifest(new_manifest_file)

    tracked_repos = set()

    for line in old_manifest_lines:
        if '<project' in line:
            path, name = get_repo_info(line)
            tracked_repos.add((path, name))

    local_manifest_lines = []

    extra_remotes = set()

    for line in new_manifest_lines:
        if '<project' in line:
            path, name = get_repo_info(line)
            if 'remote="aosp"' not in line and (path, name) not in tracked_repos:
                local_manifest_lines.append(f'  <remove-project name="{path}" />\n')
                local_manifest_lines.append(line)

        elif '<default' in line:
            if line not in old_manifest_lines:
                # The <default> remote in the new manifest is different, rename it to <default1>
                default_remote_y = line.replace('<default', '<default1')
                local_manifest_lines.append(default_remote_y)
        else:
            local_manifest_lines.append(line)

        if '<remote ' in line:
            remote_name = get_remote_name(line)
            if not remote_exists(remote_name, old_manifest_lines):
                start_index = new_manifest_lines.index(line)
                end_index = find_remote_block_end(new_manifest_lines, start_index)
                extra_remotes.update(new_manifest_lines[start_index:end_index + 1])

    local_manifest_lines = remove_comments(local_manifest_lines)
    local_manifest_lines = clean_stray_elements(local_manifest_lines)

    # Remove common remotes and keep only the extra remotes in the new manifest
    local_manifest_lines = [line for line in local_manifest_lines if line not in extra_remotes]

    # Remove the superproject and contactinfo lines
    local_manifest_lines = [line for line in local_manifest_lines if not line.strip().startswith('<superproject')]
    local_manifest_lines = [line for line in local_manifest_lines if not line.strip().startswith('<contactinfo')]

    local_manifest_file = "local_manifest.xml"  # Replace with the desired name for the output local manifest file
    write_manifest(local_manifest_file, local_manifest_lines)
    print(f"Local manifest file '{local_manifest_file}' has been generated.")

if __name__ == "__main__":
    main()
