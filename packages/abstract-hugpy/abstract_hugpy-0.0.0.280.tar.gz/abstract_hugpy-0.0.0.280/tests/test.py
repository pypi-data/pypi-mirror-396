from imports import *
from abstract_apis import *
DOMAIN = 'https://typicallyouitliers.com'
def get_for_clownworld_endpoint(*args,**kwargs):
    kwargs['domain']= kwargs.get('domain') or DOMAIN

    return get_endpoint_urls(*args,**kwargs)
key="extractfields"
endpoint = 'https://typicallyoutliers.com/video/get_pipeline_data'
video_url = "https://www.youtube.com/watch?v=mIMMZQJ1H6E"
data = {"url":video_url,"key":key}
result  = postRequest(endpoint,data=data)
input(result)
##domain=DOMAIN,endpoint=endpoint,
##video_id = infoRegistry().get_video_info(video_url)
##input(video_id)
##key="extractfields"
##data = {"url":video_url,"key":key}
##input(data)
##result  = postRequest(endpoint,data=data)
##input(result)
##if __name__ == "__main__":
##
##    url = "https://stackoverflow.com/questions/77230706/using-only-pip-for-installing-spacy-model-en-core-web-sm"
##
##    # Example: pull your raw pipeline dict
##    info = get_pipeline_data(video_id='oC1nc0UqXRc', key="extractfields")
##    input(info)
##
##    input("Press Enter to exit...")
