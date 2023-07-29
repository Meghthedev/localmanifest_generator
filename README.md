# Local Manifest Maker

This Python script automates the generation of a local manifest by comparing two given manifests. It primarily focuses on identifying repositories that are forks of existing ones and creates a new local manifest with only the relevant repositories needed for the custom project.

The script takes two input manifest files: the original manifest and the updated manifest. It then analyzes both manifests to identify the differences in repository information, such as paths, names, and remotes. It specifically looks for new repositories (forks) present in the updated manifest that were not included in the original manifest.

## What dosent work:
-If the second rom manifest has a remote that first one dosent, that isnt included in the final manifest

-output dosent look too clean

-need to manually combine all the default.xml and other manifests snippets for both roms