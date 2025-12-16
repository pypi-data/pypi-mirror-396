import argparse
import hashlib
import mimetypes
import os
import re

import dropbox
import requests
from tqdm import tqdm


def get_extension_from_headers(response) -> str:
    """
    Guess the file extension from the HTTP Content-Type header.
    """
    content_type = response.headers.get("content-type")
    if content_type:
        ext = mimetypes.guess_extension(content_type)
        return ext if ext else ".jpg"
    return ".jpg"


def download_and_replace_images(
    markdown_content: str, doc_folder: str, doc_filename: str
) -> str:
    """
    Scans markdown for images, downloads them, and updates the links.
    Returns the modified markdown string.
    """
    image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    matches = image_pattern.findall(markdown_content)

    if not matches:
        return markdown_content

    assets_dir = os.path.join(doc_folder, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    new_content = markdown_content

    # Notify user if a doc has many images
    if len(matches) > 5:
        tqdm.write(f"   -> Downloading {len(matches)} images for '{doc_filename}'...")

    for i, (alt_text, url) in enumerate(matches):
        try:
            # Create unique hash for filename
            url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:10]

            # Request image
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                ext = get_extension_from_headers(r)
                image_filename = f"{doc_filename}_img_{i}_{url_hash}{ext}"
                local_image_path = os.path.join(assets_dir, image_filename)

                # Write to disk
                with open(local_image_path, "wb") as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)

                # Replace link in Markdown
                relative_path = f"assets/{image_filename}"
                original_markdown_link = f"![{alt_text}]({url})"
                new_markdown_link = f"![{alt_text}]({relative_path})"

                new_content = new_content.replace(
                    original_markdown_link, new_markdown_link
                )
            else:
                tqdm.write(
                    f"      [Warning] Could not download image {i} in '{doc_filename}'"
                    f" (Status {r.status_code})"
                )

        except Exception as e:
            tqdm.write(
                f"      [Error] Failed downloading image {i} in '{doc_filename}': {e}"
            )

    return new_content


def find_files_to_export(
    dbx: dropbox.Dropbox, remote_subdir: str
) -> list[dropbox.files.FileMetadata]:
    """
    Scans Dropbox folder for .paper files to export.
    """

    files_to_process = []

    # Recursive list of all files
    result = dbx.files_list_folder(remote_subdir, recursive=True)
    # Pagination loop to get ALL files
    while True:
        for entry in result.entries:
            if not isinstance(entry, dropbox.files.FileMetadata):
                continue
            if entry.name.lower().endswith(".paper"):
                files_to_process.append(entry)

        if result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
        else:
            break

    return files_to_process


def export_file(
    dbx: dropbox.Dropbox, file_meta: dropbox.files.FileMetadata, local_dir: str
) -> None:
    """
    Convert a Dropbox Paper file to Markdown and save it locally.
    """

    # calculate paths
    rel_path = file_meta.path_display.lstrip("/")
    base_name = os.path.splitext(os.path.basename(rel_path))[0]
    folder_path = os.path.join(local_dir, os.path.dirname(rel_path))
    save_path = os.path.join(folder_path, base_name + ".md")

    # ensure local folder exists
    os.makedirs(folder_path, exist_ok=True)

    try:
        # Export Markdown
        metadata, response = dbx.files_export(
            file_meta.path_lower, export_format="markdown"
        )
        content_str = response.content.decode("utf-8")

        # Handle Images
        final_content = download_and_replace_images(content_str, folder_path, base_name)

        # Save File
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(final_content)

    except dropbox.exceptions.ApiError as e:
        tqdm.write(f"\n[FAILED] Dropbox API Error on '{file_meta.name}': {e}")
    except Exception as e:
        tqdm.write(f"\n[FAILED] General Error on '{file_meta.name}': {e}")


def switch_to_team_root(dbx: dropbox.Dropbox, account: dropbox.users.FullAccount):
    # Check if the user is part of a team with a complex root structure
    if hasattr(account.root_info, "root_namespace_id"):
        root_ns_id = account.root_info.root_namespace_id
        print(f"   * Detected Team Account. Namespace ID: {root_ns_id}")
        print("   * Switching API context to Team Root...")

        # This 'wraps' the client to look at the Team Root instead of Personal Root
        dbx = dbx.with_path_root(dropbox.common.PathRoot.root(root_ns_id))
    else:
        print("   * Standard Personal Account detected.")


def export_directory(remote_dir: str, local_dir: str, access_token: str) -> None:
    dbx: dropbox.Dropbox = dropbox.Dropbox(access_token)

    print("--- Dropbox Paper to Markdown + Images Exporter ---")

    try:
        # CHECK FOR TEAM ROOT (The Critical Fix)
        account = dbx.users_get_current_account()
        switch_to_team_root(dbx, account)

        print("1. Scanning Dropbox for .paper files... (This takes a moment)")
        files_to_process = find_files_to_export(dbx, remote_dir)

        print(f"2. Found {len(files_to_process)} Paper documents. Starting export...\n")
        # The Loop with Progress Bar
        for file_meta in tqdm(files_to_process, unit="doc", desc="Exporting"):
            export_file(dbx, file_meta, local_dir)

        print(
            f"\nSUCCESS: Export completed. Files saved to: {os.path.abspath(local_dir)}"
        )

    except dropbox.exceptions.AuthError:
        print("\n[FATAL ERROR] Invalid Access Token.")
        print("Please check your permissions in the Dropbox Console.")
        return


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export Dropbox Paper documents to Markdown with images"
    )
    parser.add_argument(
        "--access-token",
        default=None,
        help="Dropbox API access token (default: DROPBOX_ACCESS_TOKEN env, or prompt)",
    )
    parser.add_argument(
        "--local-dir",
        default="./paper_export",
        help="Local directory to save exported files (default: ./paper_export)",
    )
    parser.add_argument(
        "--remote-dir",
        default="",
        help="Dropbox directory to export from (default: root)",
    )

    args = parser.parse_args()

    access_token = args.access_token
    if not access_token:
        access_token = os.environ.get("DROPBOX_ACCESS_TOKEN")
    if not access_token:
        access_token = input(
            "If you do not have access token yet, see docs how to generate one at "
            "https://www.dropbox.com/developers/apps/\n"
            "Enter Dropbox access token: "
        ).strip()
    if not access_token:
        print("Error: No access token provided.")
        return

    export_directory(args.remote_dir, args.local_dir, access_token)


if __name__ == "__main__":
    main()
