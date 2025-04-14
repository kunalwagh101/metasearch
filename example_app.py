import os
import datetime

from metasearch.plugins.text_search import add_file_to_text_index
from pathlib import Path

import metasearch
def main():
    # current_path = Path.cwd().parent
  
    config = metasearch.Config(
        scan_paths=["H:\\trail","H:\exam","H:\job"],
        
    )
    
    engine = metasearch.Engine(config)
    result = engine.search_first_match('producer:"Microsoft: Print To PDF"')
    if result:
        print("Found:", result)
    else:
        print("No match found.")

    result1 = engine.search('author:"Kunal Wagh"')
    if result1:
        print("Found:", result1)
    else:
        print("No match found.")
    

   

    print("=== Initial Search (Lazy Indexing Trigger) ===")
    initial_results = engine.search("file_name:Approach")
    if initial_results:
        print("Files found:")
        for result in initial_results:
            print(" -", result)
    else:
        print("No files Approach  found. (Lazy indexing may have run but no files matched.)")
    # H:\Aganitha\test.sh

    initial_results = engine.search("file_name:test")
    if initial_results:
        print("Files found test.sh ==== :")
        for result in initial_results:
            print(" -", result)
    else:
        print("No files found. (Lazy indexing may have run but no files matched.)")



  
    sample_file = os.path.join("H:\\trail", "extrail.txt")
    print(f"\n=== Annotating file: {sample_file} ===")
    engine.annotate(sample_file, {
        "company": "abc",
        "description": "Example annotation added for testing."
    })


    result_first = engine.search_first_match('company:"abc"')
    print("Search First Match returned:", result_first)

    
    # See all metadata
    meta = engine.get_metadata(sample_file)
    print("this is the meta data :meta", meta)

   

    print("\n=== Searching for files with company 'abc' ===")
    query_company = 'company:abc'
    results_company = engine.search(query_company)
    for res in results_company:
        print("Found:", res)

    
  
    
    # 4. Search for files modified in the last 5 hours.
    print("\n=== Searching for files updated in the last 5 hours ===")
    now = datetime.datetime.now()
    five_hours_ago = now - datetime.timedelta(hours=5)
    query_mod_time = f"modified:[{five_hours_ago.isoformat()} TO {now.isoformat()}]"
    results_recent_mod = engine.search(query_mod_time)
    for res in results_recent_mod:
        print("Recently modified:", res)
    
    # 5. Search for files created in the last 5 hours.
    print("\n=== Searching for files created in the last 5 hours ===")
    query_create_time = f"created:[{five_hours_ago.isoformat()} TO {now.isoformat()}]"
    results_recent_create = engine.search(query_create_time)
    for res in results_recent_create:
        print("Recently created:", res)


   
    print("\n=== Searching for files > 5 MB ===")
    five_mb = 2 * 1048576  # 5 MB in bytes
    query_size_gt = f"size_bytes:[{five_mb + 1} TO ]"
    results_size_gt = engine.search(query_size_gt)

    print("File > 5MB:", "Size:", results_size_gt)
    
 
    print("\n=== Searching for files < 5 MB ===")
    query_size_lt = f"size_bytes:[0 TO {five_mb}]"
    results_size_lt = engine.search(query_size_lt)
    for res in results_size_lt:
        print("File < 5MB:", res, "Size:", res)


    two_mb = 2 * 1024 * 1024  # 2 MB in bytes
    print("\n=== Searching for files < 2 MB ===")
    size_results = engine.search_by_size(0, two_mb)
    if size_results:
        for f in size_results:
            print("Found file:", f, "Size:")
    else:
        print("No files found in size range.")



    print(f"\n=== Removing File from Index: {sample_file} ===")
    engine.remove_file(sample_file)

     # sample_file = os.path.join("H:\\trail", "example1.txt")
    # print(f"\n=== Annotating file: {sample_file} ===")
    # engine.annotate(sample_file, {
    #     "pricing": "abc",
    #     "description": "This is a description",
    #     "value": "554"
    # })







    # # Optionally, add sample_file to the text search plugin index.
    # # sample_metadata = engine.get_metadata(sample_file)
    # # add_file_to_text_index(sample_metadata)
    # print("\n=== Searching for files with actor 'abc' ===")
    # query_actor = 'actor:"abc"'
    # results_actor = engine.search(query_actor)
    # for res in results_actor:
    #     print("Found:", res["file_path"])
    
    # Update the index manually.
    # print("\n=== Updating Index for Directory H:\\trail ===")
    
    
    # # --- Search Query Examples ---
    # # 1. Search for files with actor "abc".
    
    # # Remove a file from the index.
    # print(f"\n=== Removing File from Index: {sample_file} ===")
    # engine.remove_file(sample_file)
    
    # print("\n=== Searching for the Removed File ===")
    # post_removal_results = engine.search(f'"{sample_file}"')  
    # if post_removal_results:
    #     print("File still present in index:")
    #     for res in post_removal_results:
    #         print(" -", res["file_path"])
    # else:
    #     print("File successfully removed from index.")
    
    engine.shutdown()
    # print("\nEngine shutdown complete.")

    #2. Search for files larger than 5 MB.
    # print("\n=== Searching for files > 5 MB ===")
    # five_mb = 5 * 1048576  # 5 MB in bytes
    # query_size_gt = f"size_bytes:[{five_mb + 1} TO ]"
    # results_size_gt = engine.search(query_size_gt)

    # print("File > 5MB:", "Size:", results_size_gt)
    
    # # 3. Search for files smaller than 5 MB.
    # print("\n=== Searching for files < 5 MB ===")
    # query_size_lt = f"size_bytes:[0 TO {five_mb}]"
    # results_size_lt = engine.search(query_size_lt)
    # for res in results_size_lt:
    #     print("File < 5MB:", res, "Size:", res)

if __name__ == "__main__":
    main()