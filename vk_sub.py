import vk_api
import vk_api.audio
from jconfig import MemoryConfig
import getpass
import json

def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция.
    """
    key = getpass.getpass("Enter authentication code: ")
    remember_device = False

    return key, remember_device

def main():
    session = vk_api.VkApi(input("User: "), getpass.getpass("Password: "), auth_handler=auth_handler, config=MemoryConfig)
    session.auth()
    api = session.get_api()
    audio = vk_api.audio.VkAudio(session)
    friends = map(lambda a: list(a.values())[:3], api.users.get(user_ids=api.friends.get()['items']))
    
    url_session = audio._vk.http

    for user_id, first_name, last_name in friends:
        data = url_session.get(f"https://vk.com/audios{user_id}").text
        beg_follow = data.find("AudioUtils.followOwner(")
        beg_unfollow = data.find("AudioUtils.unfollowOwner(")

        if "Музыка скрыта или удалена" in data or (beg_follow == -1 and beg_unfollow == -1):
            print(f"No luck for {first_name} {last_name}")
            continue
        elif beg_unfollow != -1:
            print(f"Already subscribed to {first_name} {last_name}")
            continue
        
        end_follow = beg_follow + data[beg_follow:].find(")") + 1
        hash = data[beg_follow:end_follow].split("&#39;")[-2]
        answ = url_session.post("https://vk.com/al_audio.php?act=follow_owner",
                                data={"al": 1, "hash": hash, "owner_id":user_id}).text
        # json_response = json.loads(answ.replace('<!--', ''))
        # print(json_response)
        print(f"Subscribed to {first_name} {last_name}")

if __name__ == "__main__":
    main()