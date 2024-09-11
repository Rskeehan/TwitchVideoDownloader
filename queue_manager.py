download_queue = []

def add_to_queue(url, output_path, resolution):
    download_queue.append((url, output_path, resolution))
    if len(download_queue) == 1:
        start_next_in_queue()

def remove_from_queue(queue_listbox):
    selected = queue_listbox.curselection()
    if not selected:
        return
    
    index = selected[0]
    del download_queue[index]
    update_queue_listbox(queue_listbox)

def move_up_in_queue(queue_listbox):
    selected = queue_listbox.curselection()
    if not selected or selected[0] == 0:
        return
    
    index = selected[0]
    download_queue[index], download_queue[index-1] = download_queue[index-1], download_queue[index]
    update_queue_listbox(queue_listbox)
    queue_listbox.selection_set(index-1)

def move_down_in_queue(queue_listbox):
    selected = queue_listbox.curselection()
    if not selected or selected[0] == len(download_queue) - 1:
        return
    
    index = selected[0]
    download_queue[index], download_queue[index+1] = download_queue[index+1], download_queue[index]
    update_queue_listbox(queue_listbox)
    queue_listbox.selection_set(index+1)

def start_next_in_queue():
    if download_queue:
        url, output_path, resolution = download_queue[0]
        return url, output_path, resolution  # Pass the information back to the caller (main.py)

def process_next_in_queue():
    if download_queue:
        download_queue.pop(0)
        return start_next_in_queue()  # Return the next item in the queue

def update_queue_listbox(queue_listbox):
    queue_listbox.delete(0, queue_listbox.size())
    for i, item in enumerate(download_queue):
        url, _, _ = item
        queue_listbox.insert(i, url)
