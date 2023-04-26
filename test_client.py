import requests

base = "http://localhost:5000/"

def get_room_test():
    url = "http://localhost:5000" +"get_room/"
    params = {
        "room_id": 619041,
        "guid": 30,
    }      
    response = requests.get(url, params=params)
    print(response.content)

def get_all_room_test():
    url = base + "get_all_room"
    response = requests.get(url)
    print(response.content)

        
def join_room_test():
    url = "http://localhost:5000/join/"
    data = {
        # "room_id": 619041,
        "guid": 30
    }
    response = requests.post(url, data=data)
    print(response.content)
    
def update_room_test():
    url = "http://localhost:5000/update_room/"
    data = {
        "room_id": 321661,
        "guid": 30,
        "start_game": True,
        "IP_endpoint": "127.0.0.1:8000"
    }
    response = requests.post(url, data=data)
    print(response.content)
    
    
def create_room_test():
    url = "http://localhost:5000/create_room/"
    data = {
        "guid": 30
    }
    response = requests.post(url, data=data)
    print(response.content)
    
def leave_room():
    url = "http://localhost:5000/leave_room/"
    data ={
        "guid": 30,
        "room_id": 936270
    }
    response = requests.post(url, data=data)
    print(response.content)
        
if __name__ == "__main__":
    # create_room_test()
    # get_all_room_test()
    join_room_test()
    # leave_room()