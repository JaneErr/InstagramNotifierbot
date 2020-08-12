from instagramclient import InstagramClient
from instagram_web_api.errors import ClientError

class InstagramWebApi:
    def __init__(self):
        self.webapi = InstagramClient(auto_patch=True, drop_incompat_keys=False)

    def getUserId(self, username):
        return self.webapi.user_info2(username)['id']

    def getLastPost(self, user_id):
        media = self.webapi.user_feed(user_id, count=1)[0]['node']
        edges = media['edge_media_to_caption']['edges']
        post = {}
        post['type'] = media['type']

        if (bool(len(edges))):
            post['caption'] = '<a href="https://www.instagram.com/' + media['owner']['username'] + '">@' + media['owner']['username'] + '</a>: ' + edges[0]['node']['text'] + '\n' + media['link']
        else:
            post['caption'] = '<a href="https://www.instagram.com/' + media['owner']['username'] + '">@' + media['owner']['username'] + '</a>\n' + media['link']

        if (media['type'] == 'video'):
            post['content'] = media['videos']['low_resolution']['url']
        else:
            post['content'] = media['images']['standard_resolution']['url']

        return post

        
    
    def getLastPostId(self, user_id):
        media = self.webapi.user_feed(user_id, count=1)
        if (bool(len(media))):
            return media[0]['node']['id']
        else:
            return 0

    def userExist(self, username):
        try:
            self.webapi.user_info2(username)
        except ClientError:
            return False
        return True