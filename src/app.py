from flask import Flask,request,jsonify
import requests as req
import os
path=os.path
import sys
import json
import argparse
import hashlib
import datetime
import uuid
#SHA-512 Hashed Secret Key
API_SECRET_KEY_HASHED='95af72f12a6b78bd03c6e81c6904230efa856e4b08c1d64886adbef3529d12d89f51e11a8daebe442b299dabee98677f593352de2ab36da2ec69c76922b3ec8e' #doyal_baba

with open("./ip_table.json") as handle:
    SPECIFIED_IPS=json.load(handle)

app=Flask(__name__)
def ArgParseActivity():
    parser=argparse.ArgumentParser(prog="social_media_reaction_server")
    parser.add_argument("-P","--port",help="Port to listen on",action="store")
    parser.add_argument("-H","--host",help="Host to bind with",action="store")
    parser.add_argument("-D","--debug",help="Runs in Debug Mode",action="store_true")
    return parser.parse_args()

def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']


def getClientClass():
    ip = get_client_ip()
    if ip in SPECIFIED_IPS["blacklist"]:
        return "Blacklisted"
    elif ip in SPECIFIED_IPS["silver"]:
        return "Silver"
    elif ip in SPECIFIED_IPS["bronze"]:
        return "Bronze"
    elif ip in SPECIFIED_IPS["gold"]:
        return "Gold"
    elif ip in SPECIFIED_IPS["diamond"]:
        return "Diamond"
    elif ip in SPECIFIED_IPS["platinum"]:
        return "Platinum"
    else:
        return "Normal"


def LoadBucket(bucket):
    with open(path.join("./buckets/",bucket+".json")) as handle:
        return json.load(handle)

def DumpBucket(bucket,postid,n_data):
    with open(path.join("./buckets/",bucket+".json"),"w") as handle:
        json.dump(n_data,handle,indent=2)
    
def isBucketAvailable(bucket):
    if bucket+".json" in os.listdir("./buckets/"):
        return True
    return False


def DislikeToPost(bucket,postid,ip):
    bucket_data=LoadBucket(bucket)
    del bucket_data[postid]["likes"][bucket_data[postid]["likes"].index(ip)]
    DumpBucket(bucket,postid,bucket_data)

def LikeToPost(bucket,postid,ip):
    bucket_data=LoadBucket(bucket)
    bucket_data[postid]["likes"].append(ip)
    DumpBucket(bucket,postid,bucket_data)

def commentObj(comment):
    bdst=datetime.datetime.now() + datetime.timedelta(hours=6)
    date=bdst.day
    month=bdst.month
    year=bdst.year
    hour=bdst.hour
    minute=bdst.minute

    return {
        "comment":comment,
        "id":uuid.uuid4().hex,
        "time":{
            "day":date,
            "month":month,
            "year":year,
            "hour":hour,
            "minute":minute
        }
    }

@app.route("/")
def Index():
    if getClientClass()=="Blacklisted":
        return jsonify({
            "msg":"Your Device is blocked by the author of this API. It might occur if you use any vpn or proxy service. Turn of that service and try again."
        })
    return jsonify({
        "msg":"Social Media Reaction Manager v1.0.0. (C) 2021 Nur Mahmud Ul Alam Tasin"
    })


@app.route("/<bucket>/<postid>/like/",methods=["POST"])
def ReactTo(bucket,postid):
    if getClientClass()=="Blacklisted":
        return jsonify({
            "msg":"Your Device is blocked by the author of this API. It might occur if you use any vpn or proxy service. Turn of that service and try again."
        })
    if not isBucketAvailable(bucket):
        return jsonify({
            "success":False,
            "msg":"Invalid Bucket Name Given."
        })
    bucket_data=LoadBucket(bucket)
    if not postid in bucket_data:
        return jsonify({
            "success":False,
            "msg":"Invalid Post ID"
        })
    if get_client_ip() in bucket_data[postid]["likes"]:
        DislikeToPost(bucket,postid,get_client_ip())
        return jsonify({
            "success":True,
            "msg":"Disliked the post."
        })
    else:
        LikeToPost(bucket,postid,get_client_ip())
        return jsonify({
            "success":True,
            "msg":"Liked the post."
        })

@app.route("/<bucket>/<postid>/like/",methods=["GET"])
def ReactCount(bucket,postid):
    if getClientClass()=="Blacklisted":
        return jsonify({
            "msg":"Your Device is blocked by the author of this API. It might occur if you use any vpn or proxy service. Turn of that service and try again."
        })
    if not isBucketAvailable(bucket):
        return jsonify({
            "success":False,
            "msg":"Invalid Bucket Name Given."
        })
    bucket_data=LoadBucket(bucket)
    if not postid in bucket_data:
        return jsonify({
            "success":False,
            "msg":"Invalid Post ID"
        })
    return jsonify({
        "success":True,
        "count":len(bucket_data[postid]["likes"])
    })


@app.route("/<bucket>/<postid>/comment/",methods=["POST"])
def CommentTo(bucket,postid):
    if getClientClass()=="Blacklisted":
        return jsonify({
            "msg":"Your Device is blocked by the author of this API. It might occur if you use any vpn or proxy service. Turn of that service and try again."
        })
    if not isBucketAvailable(bucket):
        return jsonify({
            "success":False,
            "msg":"Invalid Bucket Name Given."
        })
    bucket_data=LoadBucket(bucket)
    if not postid in bucket_data:
        return jsonify({
            "success":False,
            "msg":"Invalid Post ID"
        })
    try:
        comment=request.json["comment"]
        if comment.strip()=="":
            return jsonify({
                "success":False,
                "msg":"Blank Comment is not consired as a valid comment."
            })
    except KeyError:
        return jsonify({
            "success":False,
            "msg":"Comment Not Provided!!"
        })
    try:
        if len(bucket_data[postid]["comments"][get_client_ip()])==5:
            return jsonify({
                "success":False,
                "msg":"You've commented 5 times.You can't comment anymore."
            })
        bucket_data[postid]["comments"][get_client_ip()].append(commentObj(comment))
    except KeyError:
        bucket_data[postid]["comments"][get_client_ip()]=[commentObj(comment)]
    
    DumpBucket(bucket,postid,bucket_data)
    return jsonify({
        "success":True,
        "msg":"Comment Added Successfully."
    })

@app.route("/<bucket>/<postid>/comment/",methods=["GET"])
def PushComments(bucket,postid):
    if getClientClass()=="Blacklisted":
        return jsonify({
            "msg":"Your Device is blocked by the author of this API. It might occur if you use any vpn or proxy service. Turn of that service and try again."
        })
    if not isBucketAvailable(bucket):
        return jsonify({
            "success":False,
            "msg":"Invalid Bucket Name Given."
        })
    bucket_data=LoadBucket(bucket)
    if not postid in bucket_data:
        return jsonify({
            "success":False,
            "msg":"Invalid Post ID"
        })
    comments=[]
    for ips in bucket_data[postid]["comments"]:
        for comment in bucket_data[postid]["comments"][ips]:
            comments.append({
                "text":comment["comment"],
                "id":comment["id"],
                "time":comment["time"]})
    return jsonify({
        "success":True,
        "msg":"Comments Pushed.",
        "comments":comments
    })

@app.route("/<bucket>/<postid>/comment/delete/",methods=["POST"])
def DeleteComment(bucket,postid):
    if getClientClass()=="Blacklisted":
        return jsonify({
            "msg":"Your Device is blocked by the author of this API. It might occur if you use any vpn or proxy service. Turn of that service and try again."
        })
    if not isBucketAvailable(bucket):
        return jsonify({
            "success":False,
            "msg":"Invalid Bucket Name Given."
        })
    bucket_data=LoadBucket(bucket)
    if not postid in bucket_data:
        return jsonify({
            "success":False,
            "msg":"Invalid Post ID"
        })
    if not "id" in request.json:
        return jsonify({
            "success":False,
            "msg":"Comment ID must be passed."
        })
    client_ip=get_client_ip()
    for ips in bucket_data[postid]["comments"]:
        i=0
        for comment in bucket_data[postid]["comments"][ips]:
            if comment["id"]==request.json["id"]:
                if client_ip==ips:
                    del bucket_data[postid]["comments"][ips][i]
                    DumpBucket(bucket,postid,bucket_data)
                    return jsonify({
                        "success":True,
                        "msg":f"comment {request.json['id']} was deleted successfully."
                    })
                else:
                    return jsonify({
                        "success":False,
                        "msg":f"It seems that you haven't wrote the comment with id `{request.json['id']}`."
                    })
            i+=1
    return jsonify({
        "success":False,
        "msg":f"No comment found with id `{request.json['id']}`."
    })

@app.route("/create/bucket/",methods=["POST"])
def CreateBucket():
    if getClientClass()=="Blacklisted":
        return jsonify({
            "msg":"Your Device is blocked by the author of this API. It might occur if you use any vpn or proxy service. Turn of that service and try again."
        })
    if not "api-key" in request.json:
        return jsonify({
            "success":False,
            "msg":"To create bucket you need administrator previllages. Provide an API KEY."
        })
    if not hashlib.sha512(request.json["api-key"].encode()).hexdigest()==API_SECRET_KEY_HASHED:
        return jsonify({
            "success":False,
            "msg":"API KEY is incorrect."
        })
    if not "bucket" in request.json:
        return jsonify({
            "success":False,
            "msg":"bucket name not defined."
        })
    if isBucketAvailable(request.json["bucket"]):
        return jsonify({
            "success":False,
            "msg":f"bucket `{request.json['bucket']}` already exists."
        })
    os.system(f"touch ./buckets/{request.json['bucket']}.json")
    with open(f"./buckets/{request.json['bucket']}.json","w") as handle:
        handle.write("{}")
    return jsonify({
        "success":True,
        "msg":f"bucket `{request.json['bucket']}` created."
    })

@app.route("/<bucket>/delete/",methods=["POST"])
def DeleteBucket(bucket):
    if getClientClass()=="Blacklisted":
        return jsonify({
            "msg":"Your Device is blocked by the author of this API. It might occur if you use any vpn or proxy service. Turn of that service and try again."
        })
    if not "api-key" in request.json:
        return jsonify({
            "success":False,
            "msg":"To create bucket you need administrator previllages. Provide an API KEY."
        })
    if not hashlib.sha512(request.json["api-key"].encode()).hexdigest()==API_SECRET_KEY_HASHED:
        return jsonify({
            "success":False,
            "msg":"API KEY is incorrect."
        })
    if not isBucketAvailable(bucket):
        return jsonify({
            "success":False,
            "msg":f"bucket `{bucket}` doesn't exist."
        })
    os.mkdir(f"./recycle/{get_client_ip()}/")
    naming_suffix='-'.join([str(datetime.datetime.now().day),str(datetime.datetime.now().month),str(datetime.datetime.now().year),str(datetime.datetime.now().hour),str(datetime.datetime.now().minute)])
    os.system(f"mv ./buckets/{bucket}.json ./recycle/{get_client_ip()}/{bucket}-{naming_suffix}.json")
    return jsonify({
        "success":True,
        "msg":f"bucket `{bucket}` moved to recycle bin and will be deleted automatically within 30 days."
    })

@app.route("/<bucket>/create/post/",methods=["POST"])
def CreatePostID(bucket):
    if getClientClass()=="Blacklisted":
        return jsonify({
            "msg":"Your Device is blocked by the author of this API. It might occur if you use any vpn or proxy service. Turn of that service and try again."
        })
    if not "api-key" in request.json:
        return jsonify({
            "success":False,
            "msg":"To create bucket you need administrator previllages. Provide an API KEY."
        })
    if not hashlib.sha512(request.json["api-key"].encode()).hexdigest()==API_SECRET_KEY_HASHED:
        return jsonify({
            "success":False,
            "msg":"API KEY is incorrect."
        })
    if not "postid" in request.json:
         return jsonify({
            "success":False,
            "msg":"Post ID not given."
        })
    if not isBucketAvailable(bucket):
        return jsonify({
            "success":False,
            "msg":"Invalid Bucket Name Given."
        })
    bucket_data=LoadBucket(bucket)
    if request.json["postid"] in bucket_data:
        return jsonify({
            "success":False,
            "msg":f"Post with id `{request.json['postid']}` already exists in bucket `{bucket}`."
        })
    bucket_data[request.json["postid"]]={
        "posts":{},
        "likes":[]
    }
    with open(f"./buckets/{bucket}.json","w") as handle:
        handle.write(json.dumps(bucket_data,indent=2))
    return jsonify({
        "success":True,
        "msg":f"Post with ID `{request.json['postid']}` was created."
    })

@app.route("/<bucket>/<postid>/delete/",methods=["POST"])
def DeletePost(bucket,postid):
    if getClientClass()=="Blacklisted":
        return jsonify({
            "msg":"Your Device is blocked by the author of this API. It might occur if you use any vpn or proxy service. Turn of that service and try again."
        })
    if not "api-key" in request.json:
        return jsonify({
            "success":False,
            "msg":"To create bucket you need administrator previllages. Provide an API KEY."
        })
    if not hashlib.sha512(request.json["api-key"].encode()).hexdigest()==API_SECRET_KEY_HASHED:
        return jsonify({
            "success":False,
            "msg":"API KEY is incorrect."
        })
    if not isBucketAvailable(bucket):
        return jsonify({
            "success":False,
            "msg":"Invalid Bucket Name Given."
        })
    bucket_data=LoadBucket(bucket)
    if not postid in bucket_data:
        return jsonify({
            "success":False,
            "msg":f"Post with id `{request.json['postid']}` doesn't exist in bucket `{bucket}`."
        })
    del bucket_data[postid]
    with open(f"./buckets/{bucket}.json","w") as handle:
        handle.write(json.dumps(bucket_data,indent=2))
    return jsonify({
        "success":True,
        "msg":f"Post with ID `{postid}` was deleted."
    })


if __name__=="__main__":
    args=ArgParseActivity()
    app.run(port=int(args.port or 8080),host=str(args.host or "0.0.0.0"),debug=args.debug)