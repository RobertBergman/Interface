from django.shortcuts import render, HttpResponse
import datetime
import time
import utils
# Create your views here.
def collect(request):

    success = utils.collect()

    end = datetime.datetime.now()
    if success:
        html = "<html><body>Collection Complete at %s</body></html>" % (end)
    else:
        html = "<html><body>Collection Failed</body></html>"
    print("request received")

    return HttpResponse(html)