def create_folders(parent_folder, subfolder_prefix, subfolder_index):
    ''' This function takes a parent folder, a subfolder_prefix,
    and a subfolder_index as arguments. It creates a path based on 
    these arguments and returns it.
    '''

    import os
    
    folder_name = f"{subfolder_prefix}{subfolder_index}"
    folder_path = os.path.join(parent_folder, folder_name)

    # Create the subfolder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path