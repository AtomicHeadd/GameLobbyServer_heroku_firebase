from flask import Flask, request, jsonify
import random
import json
import os

import pyrebase

env = json.load(open(".env", "r"))
print(env)

# https://github.com/nhorvath/Pyrebase4
app = Flask(__name__)
firebase = pyrebase.initialize_app(env["config"])
db = firebase.database()

# required: guid
@app.route("/create_room/", methods=['POST'])
def create_room():
    if "guid" not in request.form:
        return "No Room Found."
    all_rooms = db.child("room").get()
    room_ids = [room.val()["room_id"] for room in all_rooms.each()]
    print(room_ids)
    room_id = random.randint(0,1000000)
    while room_id in room_ids: room_id = random.randint(0,1000000)
    new_room = {"guid_list" : request.form["guid"], "player_count" : 1, "room_id": room_id}
    json_text = new_room
    json_text["player_index"] = 0
    return jsonify(json_text)

# 30件返す
@app.route("/get_all_room/", methods=["GET"])
def get_rooms():
    all_rooms = db.child("room").get()
    if all_rooms is None: return "No Room Found."
    all_rooms = [room.val() for room in all_rooms.each()]
    all_rooms = [room for room in all_room if room["player_count"] < 4][:30]
    room_info_list = [{"room_id": room["room_id"], "player_count": room["player_count"]} for room in all_room]
    print(room_info_list)
    return jsonify(room_info_list)
    
# required: guid
# optional: room_id if you join specific room
@app.route("/join/", methods=['POST'])
def join():
    if "guid" not in request.form: return "No Room Found."
    all_rooms = [room.val() for room in db.child("room").get().each()]
    public_join = "room_id" not in request.form
    if public_join: candidates = all_rooms
    else:
        room_id = int(request.form["room_id"])
        candidates = [room for room in all_rooms if room["room_id"] == room_id]
    if len(candidates) == 0: return "No Room Found."
    room = candidates[0]
    if request.form["guid"] in str(room["guid_list"]): return jsonify(room)
    room["player_count"] += 1
    guid_list = str(room["guid_list"]).split(",")
    guid_list.append(request.form["guid"])
    room["guid_list"] = str(guid_list)
    json_text = {**room, "player_index": room["player_count"] - 1}
    return jsonify(json_text)

# requried: room_id: int, guid: int
@app.route("/get_room/", methods=['GET'])
def get_room_state():
    room_id = request.args.get("room_id", 0)
    guid = request.args.get("guid", " ")
    if room_id == 0 or guid == " ": return "No Room Found."
    all_rooms = [room.val() for room in db.child("room").get().each()]
    room = [room for room in all_rooms if room["room_id"] == room_id]
    if len(room) == 0: return "No Room Found."
    room = room[0]
    if guid not in str(room["guild_list"]): return "No Room Found."
    guids = room["guid_list"].split(",")
    json_text = {**room, "player_index": guids.index(guid)}
    return jsonify(json_text)

# requried: room_id: int, guid: int
@app.route("/leave_room/", methods=["POST"])
def leave_room():
    if "room_id" not in request.form or "guid" not in request.form:
        return "Failed"
    room = session.query(Room).filter(Room.room_id == int(request.form["room_id"])).first()
    if room is None: return "Failed"
    guids, endpoints, ports = room.get_lists()
    if request.form["guid"] not in guids: return "Failed"
    room.player_count -= 1
    if room.player_count == 0: 
        session.delete(room)
        return "Success"
    player_index = guids.index(request.form["guid"])
    guids.pop(player_index).append("0")
    endpoints.pop(player_index).append("0")
    ports.pop(player_index).append("False")
    room.endpoints = ",".join(endpoints)
    room.invalid_endpoints = ",".join(ports)
    room.guids = ",".join(guids)
    return "Success"

# 部屋更新。スタート処理、エンドポイント設定、ポート無効報告
# required: room_id=int, guid=int
# at least 1 required: start_game=Any, IP_endpoint="oo.oo.oo.oo:xxxx", port_report="oo.oo.oo.oo:xxxx"
@app.route("/update_room/", methods=['POST'])
def update_room_state():
    if "room_id" not in request.form or "guid" not in request.form:
        return "No Room Found."
    room_id = int(request.form["room_id"])
    guid = request.form["guid"]
    room = session.query(Room).filter(Room.room_id == room_id).first()
    if (room is None): return "No Room Found."
    guids, endpoints, ports = room.get_lists()
    player_index = guids.index(guid)
    if (guid not in guids): return "No Room Found."
    print(" ".join(request.form.keys()))
    if "start_game" in request.form and room.room_state is RoomState.WAITING.value and player_index == 0:
        print("ゲーム開始");
        room.room_state = RoomState.PORTWAITING.value
    if "IP_endpoint" in request.form:
        endpoints[player_index] = request.form["IP_endpoint"]
        print("aaa")
        registered_count = sum(i != "0" for i in endpoints)
        print(registered_count)
        if registered_count == room.player_count: #集まった
            room.room_state = RoomState.PLAYING.value
            if room.invision_index == "":
                invision_index = random.randint(0, room.player_count-1)
                room.invision_index = str(invision_index)
        ports[player_index] = False
        room.endpoints = ",".join(endpoints)
        room.invalid_endpoints = ",".join([str(i) for i in ports])
    if "port_report" in request.form and request.form["port_report"] in endpoints:
        EP_index = endpoints.index(request.form["port_report"])
        ports[EP_index] = True
        room.invalid_endpoints = ",".join([str(i) for i in ports])
    session.commit()
    json_text = room.get_state_dict()
    json_text["player_index"] = player_index
    session.close()
    return jsonify(json_text)

## おまじない
if __name__ == "__main__":
    app.run(debug=True)