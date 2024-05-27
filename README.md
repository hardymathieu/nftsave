# nftsave
Collect NFT data, pin ipfs content, download images, find out interesting things about your NFTs from an SQLite database.

# Why?
"NFTs are just pointers to a server."
Often true, but if that "server" is the ipfs, then you can actually (self) custody the files as well as the Non Fungible Token.
I'd been meaning to find a way to do that "at scale" and after finding no reasonable existing solution, decided to whip it up myself. Because "don't trust, verify", "Not your key, not your coins", and all that.
(if unconvinced, learn more about why NFTs are awesome from [Punk6529](https://6529.io/education/tweetstorms/).)

# Disclaimer
I can't really code :D 

You'll figure it out soon if you start looking at the files. This was all put together with the help of various LLMs who helped me translate from English to Python.
But surprisingly, it runs. 
That's all I need it to do. It runs and it gets me my NFT data as intended.
It's likely quite inelegant, It's probably super inefficient. I haven't tried following good practices (even the ones I know about) but the objective was to get it running.
I can now speak computer, and get it to do my bidding, and that's awesome. Completely new unlock.

Maybe I'll look into optmizing it, although I enjoy 0 -> 1 more than 1 -> 1.5; so probably not. 
If you, dear reader, on the other hand do enjoy perfercting things, **contributions are very welcome!**

**I'm just sharing it because it might help someone else (1) custody their own NFTs so they can safeguard things they care about (2) realize that LLMs are pretty good at translating EN to Python and that you can get computers to do things for you if you leverage the power of that translation engine. Which I think are both worthwhile things to share.**

# How I use it
I have cron jobs that run each of the scripts, in the right sequence, so as to achieve the ojective.
It's easy, you edit your crontab everything just runs on a schedule.

# What's in it

Basically 5 steps: Ask Opensea for everything you hold > extract the CIDs > put it all in a database > Pin the CIDs to your IPFS node > download all the images.

## 1/ Opensea to csv
Uses the [Opensea API ](https://docs.opensea.io/) to get all the NFTs I have on all the wallets I give it for all the chains I want (that Opensea supports). And lists it all in a CSV file for use later, and a txt file with a list of everything the run collected, for safekeeping.

## 2/ Extract CIDs
Now that I have all the info from OpenSea, I need to extract the CIDs I will later pin to my ipfs node, whether in the "metadata" or "image" fields. Some of it is in base64 so that needs to be translated.
That gets written to another csv file

## 3/ Pushing it all to a database
At this step, we read the nfts.csv file and the nft_cids.csv file, join them with the unique_key we created, and turn that all into a SQLite database. Because that's easier to play with than 2 csv files.
As noted below, I could have just gone and written to an SQLite database for the two steps above as well. But I didn't know about SQlite when I wrote those scripts, and didn't really feel like rewriting them because they work.

## 4/ Pinning it all to my IPFS node
Since IPFS (kubo) has [an RPC API](https://docs.ipfs.tech/reference/kubo/rpc/), we can use that to read the db and pin very CID we encounter.
There was a python client implementation I never managed to get to work so I'm just doing the API calls directly. It works and it's really easier to understand.

I find ipfs to be super confusing but I think I got it all to work. I now have about 2GB of "pinned" data (that don't show up in the "files" section of the GUI client, because that's apparently the [MFS](https://docs.ipfs.tech/concepts/file-systems/) and it's something else for some reason).

I didn't go the complicated route and I recursively pin everything. I figured that way I'm doing a public service to all of the other owners of the same collections I'm holding. 
I mark it as "pinned" in the database so I don't try doing that again at the next run.

## 5/ downloading all images 
This is just so I can diplay them on my TV or find them easily if needed. It doesn't actually "back them up" since the authoritative server is the one referenced in the NFT metadata. And if the media at that link is taken down, there's no way I can prove I had downloaded it beforehand.
That's why onchain or ipfs NFTs are vastly superior to those pointing to a company server somewhere.
But sometimes NFTs are just fun and you don't care how long their media stays only. They're still a marker that something happened at sometime. 
And I'll still have the media for my own enjoyment if I want to.
Don't overthink it.
I mark it as downloaded in the DB so I don't redownload it at the next run.

# Obvious changes to make, if you want to improve it
- don't write your API keys in the script file, use os variables instead
- use the SQLite db from the start instead of relying on csv files initially. I only learned about SQLite after I had already created the first two scripts. And I didn't want to go back and change everything. it works :)
- make all the variables much easier to find (wallets, chains, API Keys,...) so it's easier to maintain
- if one thing requires that another thing be finished, build that into the script (as opposed to scheduling cron jobs naively 6 hours apart as "that should be enough")
- make sure everything (csv, db, logs,...) gets outputted/created inside the folder where the script it running or at least someplace more manageable than /home/hardymathieu. Because it can get a little messy. And the backup config (rsync) would be easier if there was more order.
- find an alternative to the OpenseaAPI just in case I can't rely on it anymore one of these days. Or to get data from more chains (Gnosis would be nice)

# PSA: A note if, like me, you're new(ish) to Python, and shy
The language (python) is great. But managing where it runs and the conflicts between all the things you install with "pip" is an incredible PITA.
I have had issues with that forever. 

I discovered 2 amazing things that really solve that:
(1) **colab.google.com** : super easy notebooks where you can just get to writing code without worrying about the infra. Thanks Google for all the free compute. I do all of my prototyping there. It works in 99.9999% of the cases where I need it. Obviously it can't work with my ipfs node (because it's behind my home network firewall) but for steps 1,2,3 and 5 that's where I first wrote all the code. The tweaking required when porting it over to my actual computer is absolutely minimal.
(2) **venv**, and right now I think it's the best thing after sliced bread.

I'd actually learned of [venv](https://docs.python.org/3/library/venv.html) a while back, and it felt a little intimidating.
It turns out, once you actually try it, it's really not.
It get you one Python environment in one folder. That's it, and that's awesome.

Here is all you really need to know: 

## Create the venv In Linux you do 

```
python -m venv /home/hardymathieu/nftipfs
```

That creates everything you need to run python thingies into one isolated, dedicated folder

## Then, to "pip install" stuf, you do

```
/home/hardymathieu/nftipfs/bin/python /home/hardymathieu/nftipfs/bin/pip install YOUR_PACKAGE 
```
And it won't conflict with anything else you might have done in any other project. It's like a little container for that project. Think of it like a PortableApp or a docker container.

## To run your .py files
(assuming they're in the same folder)

```
/home/hardymathieu/nftipfs/bin/python /home/hardymathieu/nftipfs/yourfile.py 
```

## venv and Cron
To make a .py script run correctly with cron, just add this at the top of your .py file, so that bash knows how to run it.

```
#!/home/hardymathieu/nftipfs/bin/python
#-*- coding: utf-8 -*- 
```
and make it executable

```
$ sudo chmod +x /home/hardymathieu/nftipfs/opensea2csv.py
```

then add the script to crontab

# Backup
To make sure you don't lose any of your hard work, and information gathered by all the daily cron jobs, use rsync and create a backup of the nfts.csv, nft_cids.csv, SQLite database, .ipfs folder
you might also want to backup all the .py files, and (if they aren't in the same place) possibly the folders where you have your python venv
