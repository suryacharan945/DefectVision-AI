"""
Official VisA Cashew Stream-Extraction Script.
Streams directly from Amazon Science AWS S3 VisA_20220922.tar archive over HTTP,
extracting strictly members belonging to the 'cashew' category into Google Drive,
then cleanly terminates the stream without downloading remaining categories.
"""
import os
import sys
import time
import tarfile
import urllib.request

URL = "https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar"
DEST_DIR = r"G:\My Drive\DefectVisionAI\dataset\raw\visa"

def stream_cashew():
    os.makedirs(DEST_DIR, exist_ok=True)
    print(f"Connecting to official Amazon Science S3 endpoint:\n  {URL}")
    print(f"Destination directory:\n  {DEST_DIR}")
    
    t0 = time.time()
    req = urllib.request.Request(URL, headers={"User-Agent": "DefectVisionAI-Auditor/1.0"})
    
    extracted_files = []
    seen_cashew = False
    skipped_count = 0
    total_bytes_extracted = 0
    
    with urllib.request.urlopen(req) as resp:
        print("Connected successfully. Opening streaming tar reader (mode='r|')...")
        with tarfile.open(fileobj=resp, mode="r|") as tar:
            for member in tar:
                # Check if member belongs to cashew
                if member.name.startswith("cashew/") or member.name == "cashew":
                    seen_cashew = True
                    # Extract safely
                    tar.extract(member, path=DEST_DIR)
                    if member.isfile():
                        extracted_files.append(member.name)
                        total_bytes_extracted += member.size
                        if len(extracted_files) % 50 == 0:
                            print(f"  Extracted {len(extracted_files)} cashew files ({total_bytes_extracted / (1024*1024):.1f} MB)...")
                else:
                    if seen_cashew:
                        # We have finished the cashew segment and entered the next category!
                        print(f"Finished cashew category archive! Encountered next category member: {member.name}")
                        print("Terminating HTTP stream cleanly...")
                        break
                    skipped_count += 1
                    if skipped_count % 500 == 0:
                        print(f"  Skipped {skipped_count} preceding non-cashew members...")
                        
    elapsed = time.time() - t0
    print(f"\nStream extraction complete in {elapsed:.1f} seconds.")
    print(f"Total non-cashew members skipped: {skipped_count}")
    print(f"Total cashew files extracted: {len(extracted_files)}")
    print(f"Total cashew payload extracted: {total_bytes_extracted / (1024*1024):.2f} MB")
    
    # Verification
    cashew_root = os.path.join(DEST_DIR, "cashew")
    if os.path.exists(cashew_root):
        print(f"\nCashew directory successfully verified at: {cashew_root}")
        for root, dirs, files in os.walk(cashew_root):
            rel = os.path.relpath(root, cashew_root)
            print(f"  {rel}: {len(files)} files")
    else:
        print(f"ERROR: Expected directory {cashew_root} not found!")

if __name__ == "__main__":
    stream_cashew()
